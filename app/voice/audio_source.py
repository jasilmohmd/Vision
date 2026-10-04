"""Common 16 kHz mono s16le sources with bounded UDP jitter buffering."""
from abc import ABC, abstractmethod
from array import array
from collections import deque
from threading import Condition, Event, Thread
from time import monotonic
import socket
import sys

SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512
CHUNK_BYTES = CHUNK_SAMPLES * 2
CHUNK_SECONDS = CHUNK_SAMPLES / SAMPLE_RATE
SILENCE = bytes(CHUNK_BYTES)


class AudioSource(ABC):
    @abstractmethod
    def read_chunk(self) -> bytes:
        """Return PCM bytes; b'' means no audio available or source closed."""

    @abstractmethod
    def close(self):
        """Release devices/sockets; safe to call more than once."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class LaptopMicSource(AudioSource):
    def __init__(self, device=None):
        import sounddevice as sd
        self.overflow_count = 0
        self.closed = False
        self.stream = sd.RawInputStream(samplerate=SAMPLE_RATE, channels=1,
                                       dtype='int16', blocksize=CHUNK_SAMPLES, device=device)
        try:
            self.stream.start()
        except Exception:
            self.stream.close()
            raise

    def read_chunk(self) -> bytes:
        if self.closed:
            return b''
        data, overflow = self.stream.read(CHUNK_SAMPLES)
        self.overflow_count += bool(overflow)
        pcm = bytes(data)
        if sys.byteorder != 'little':
            samples = array('h')
            samples.frombytes(pcm)
            samples.byteswap()
            pcm = samples.tobytes()
        return pcm

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.stream.stop()
            finally:
                self.stream.close()


class UdpAudioSource(AudioSource):
    """Arrival-order buffer with 32 ms playout and silence on missing slots.

    The raw packet contract has no sequence numbers/timestamps, so reordering
    and exact loss positions cannot be reconstructed. Excess backlog is dropped
    to keep latency bounded. One consumer calls read_chunk().
    """
    def __init__(self, host='0.0.0.0', port=5005, jitter_packets=3, max_packets=8):
        if not 1 <= jitter_packets <= max_packets:
            raise ValueError('Require 1 <= jitter_packets <= max_packets')
        self.jitter_packets = jitter_packets
        self.max_packets = max_packets
        self.condition = Condition()
        self.stopped = Event()
        self.packets = deque()
        self.received_packets = self.invalid_packets = self.dropped_packets = self.silence_chunks = 0
        self.first_received = None
        self.last_received = None
        self.next_playout = None
        self.failure = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind((host, port))
            self.socket.settimeout(0.1)
        except Exception:
            self.socket.close()
            raise
        self.address = self.socket.getsockname()
        self.thread = Thread(target=self._receive, name='udp-audio', daemon=True)
        self.thread.start()

    def _receive(self):
        while not self.stopped.is_set():
            try:
                packet, _ = self.socket.recvfrom(65535)
            except socket.timeout:
                continue
            except OSError as error:
                if not self.stopped.is_set():
                    self.failure = error
                with self.condition:
                    self.condition.notify_all()
                return
            with self.condition:
                if len(packet) != CHUNK_BYTES:
                    self.invalid_packets += 1
                    continue
                self.received_packets += 1
                self.last_received = monotonic()
                if self.first_received is None:
                    self.first_received = self.last_received
                if len(self.packets) >= self.max_packets:
                    self.packets.popleft()
                    self.dropped_packets += 1
                self.packets.append(packet)
                self.condition.notify_all()

    @property
    def last_received_at(self):
        # Generated playout silence must never hide a disconnected voice unit.
        with self.condition:
            return self.last_received

    def read_chunk(self) -> bytes:
        with self.condition:
            if self.failure:
                raise RuntimeError('UDP audio receiver failed') from self.failure
            if self.stopped.is_set():
                return b''
            if self.next_playout is None:
                deadline = monotonic() + 0.25
                while not self.stopped.is_set():
                    if self.failure:
                        raise RuntimeError('UDP audio receiver failed') from self.failure
                    now = monotonic()
                    if self.first_received is not None:
                        ready_at = self.first_received + self.jitter_packets * CHUNK_SECONDS
                        if len(self.packets) >= self.jitter_packets or now >= ready_at:
                            break
                        wait = min(deadline - now, ready_at - now)
                    else:
                        wait = deadline - now
                    if wait <= 0:
                        return b''
                    self.condition.wait(wait)
                if self.stopped.is_set():
                    return b''
                self.next_playout = monotonic()
        if self.stopped.wait(max(0, self.next_playout - monotonic())):
            return b''
        with self.condition:
            if self.stopped.is_set():
                return b''
            if self.failure:
                raise RuntimeError('UDP audio receiver failed') from self.failure
            self.next_playout = max(self.next_playout + CHUNK_SECONDS, monotonic())
            if self.packets:
                return self.packets.popleft()
            self.silence_chunks += 1
            return SILENCE

    def close(self):
        if not self.stopped.is_set():
            self.stopped.set()
            with self.condition:
                self.condition.notify_all()
            self.socket.close()
            self.thread.join(timeout=1)
