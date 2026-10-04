"""Experimental C3 BLE audio/light transport; UDP remains the default.

Notification: uint32 little-endian first-sample index + s16le/16kHz mono PCM.
Indices detect gaps; reconnect resets the sequence and buffered audio.
"""
import asyncio
import logging
import struct
from collections import deque
from threading import Condition, Event, Thread
from time import monotonic

from app.io.light_client import LIGHT_COLORS, STEADY_STATES
from app.voice.audio_source import AudioSource, CHUNK_BYTES, CHUNK_SECONDS, SILENCE

SERVICE_UUID = '9b930001-8a97-4ed0-9f08-42d26e75baf1'
AUDIO_UUID = '9b930002-8a97-4ed0-9f08-42d26e75baf1'
LIGHT_UUID = '9b930003-8a97-4ed0-9f08-42d26e75baf1'
log = logging.getLogger(__name__)


class BlePcmBuffer:
    def __init__(self):
        self.condition = Condition()
        self.data = bytearray()
        self.expected = None
        self.received_samples = self.missing_samples = self.invalid_packets = 0
        self.received_packets = self.out_of_order = self.dropped_bytes = 0
        self.silence_chunks = self.padded_samples = 0
        self.last_received = None
        self.max_gap = 0
        self.next_playout = None
        self.closed = False
        self.session_started = monotonic()
        self.gap_events = deque(maxlen=32)

    def reset_session(self):
        with self.condition:
            self.data.clear()
            self.expected = self.next_playout = None
            self.session_started = monotonic()
            self.condition.notify_all()

    def feed(self, packet):
        with self.condition:
            if len(packet) < 6 or len(packet) > 244 or len(packet) % 2:
                self.invalid_packets += 1
                return
            index = struct.unpack_from('<I', packet)[0]
            samples = (len(packet) - 4) // 2
            if self.expected is not None:
                gap = (index - self.expected) & 0xffffffff
                if gap >= 0x80000000:
                    self.out_of_order += 1
                    return
                if gap:
                    self.gap_events.append({'at_s': round(monotonic() - self.session_started, 3), 'samples': gap})
                    self.missing_samples += gap
                    if gap <= 4096:
                        self.data.extend(bytes(gap * 2))
                    else:
                        self.data.clear()
                        self.next_playout = None
            self.expected = (index + samples) & 0xffffffff
            now = monotonic()
            if self.last_received is not None:
                self.max_gap = max(self.max_gap, now - self.last_received)
            self.last_received = now
            self.received_samples += samples
            self.received_packets += 1
            self.data.extend(packet[4:])
            if len(self.data) > 8192:
                excess = ((len(self.data) - 8192 + CHUNK_BYTES - 1) // CHUNK_BYTES) * CHUNK_BYTES
                del self.data[:excess]
                self.dropped_bytes += excess
            self.condition.notify_all()

    @property
    def last_received_at(self):
        with self.condition:
            return self.last_received

    def read_chunk(self):
        with self.condition:
            deadline = monotonic() + .25
            while not self.closed:
                now = monotonic()
                if self.next_playout is None:
                    remaining = deadline - now
                    if len(self.data) < CHUNK_BYTES * 4 and remaining > 0:
                        self.condition.wait(remaining)
                        continue
                    if len(self.data) < CHUNK_BYTES:
                        return b''
                    self.next_playout = now
                wait = self.next_playout - now
                if wait > 0:
                    self.condition.wait(wait)
                    # A reconnect can reset both data and the playout clock.
                    continue
                self.next_playout = max(now, self.next_playout + CHUNK_SECONDS)
                available = min(len(self.data), CHUNK_BYTES)
                result = bytes(self.data[:available]) + bytes(CHUNK_BYTES - available)
                del self.data[:available]
                if available < CHUNK_BYTES:
                    self.silence_chunks += 1
                    self.padded_samples += (CHUNK_BYTES - available) // 2
                return result
            return b''

    def close(self):
        with self.condition:
            self.closed = True
            self.condition.notify_all()


class BleVoiceTransport(AudioSource):
    """One BLE connection provides audio and the LightClient-compatible API."""
    def __init__(self, address):
        # Optional import: UDP/laptop users never need Bleak installed.
        from bleak import BleakClient, BleakScanner
        self.client_type, self.scanner = BleakClient, BleakScanner
        self.address = address
        self.buffer = BlePcmBuffer()
        self.stopped = Event()
        self.loop = self.client = self.task = None
        self.steady_state = 'ready'
        self.reconnecting = False
        self.connected = Event()
        self.thread = Thread(target=self._run, name='ble-voice', daemon=True)
        self.thread.start()

    @property
    def last_received_at(self):
        return self.buffer.last_received_at

    def read_chunk(self):
        return self.buffer.read_chunk()

    def _run(self):
        try:
            asyncio.run(self._worker())
        except asyncio.CancelledError:
            pass

    async def _worker(self):
        self.loop = asyncio.get_running_loop()
        self.task = asyncio.current_task()
        while not self.stopped.is_set():
            try:
                device = await self.scanner.find_device_by_address(self.address, timeout=8)
                if device is None:
                    raise RuntimeError('C3 BLE advertisement not found')
                async with self.client_type(device, timeout=10) as client:
                    self.client = client
                    self.buffer.reset_session()
                    await client.start_notify(AUDIO_UUID, lambda _, data: self.buffer.feed(data))
                    self.connected.set()
                    await self._write(self._wire_state(self.steady_state))
                    log.info('C3 BLE connected: %s', self.address)
                    while client.is_connected and not self.stopped.is_set():
                        await asyncio.sleep(.1)
            except Exception as error:
                if not self.stopped.is_set():
                    log.warning('C3 BLE unavailable: %s', error)
            finally:
                self.connected.clear()
                self.client = None
                self.buffer.reset_session()
            for _ in range(20):
                if self.stopped.is_set():
                    break
                await asyncio.sleep(.1)

    def _wire_state(self, state):
        return 'reconnect' if self.reconnecting and self.steady_state != 'sleep' else state

    async def _write(self, state):
        if self.client is not None and self.client.is_connected:
            await self.client.write_gatt_char(LIGHT_UUID, state.encode('ascii'), response=True)

    def _schedule_write(self, state):
        if self.loop is not None and self.connected.is_set() and not self.stopped.is_set():
            future = asyncio.run_coroutine_threadsafe(self._write(state), self.loop)
            def done(result):
                try:
                    result.result()
                except Exception as error:
                    log.warning('BLE light write failed: %s', error)
            future.add_done_callback(done)

    def send(self, state):
        if state not in LIGHT_COLORS:
            raise ValueError(f'Unknown light state: {state}')
        if state in STEADY_STATES:
            self.steady_state = state
        self._schedule_write(self._wire_state(state))

    def set_reconnecting(self, enabled):
        if self.reconnecting != enabled:
            self.reconnecting = enabled
            self._schedule_write(self._wire_state(self.steady_state))

    def close(self):
        if self.stopped.is_set():
            return
        self.stopped.set()
        self.buffer.close()
        # Discovery/connect can take up to 18s; cancellation avoids leaked connections.
        if self.loop is not None and self.loop.is_running():
            self.loop.call_soon_threadsafe(self._cancel)
        self.thread.join(timeout=3)

    def _cancel(self):
        if self.task is not None:
            self.task.cancel()
