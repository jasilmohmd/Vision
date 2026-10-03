"""Laptop microphone to raw UDP audio; print C3 light commands and flash restore."""
import argparse
import socket
from threading import Event, Thread
from time import monotonic
from app.config import load_config
from app.io.light_client import LIGHT_COLORS, STEADY_STATES, FLASH_STATES
from app.voice.audio_source import LaptopMicSource

class LightMonitor:
    def __init__(self, host='127.0.0.1', port=5006):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.socket.settimeout(.05)
        self.stop = Event()
        self.thread = Thread(target=self._run, daemon=True)
        self.steady, self.restore_at = 'ready', None

    def start(self):
        self.thread.start()

    def _run(self):
        while not self.stop.is_set():
            try:
                data, _ = self.socket.recvfrom(64)
                state = data.decode('ascii')
                if state not in LIGHT_COLORS:
                    continue
                print(f'Light: {state} ({LIGHT_COLORS[state]})', flush=True)
                if state in STEADY_STATES:
                    self.steady, self.restore_at = state, None
                elif state in FLASH_STATES:
                    self.restore_at = monotonic() + .3
            except socket.timeout:
                pass
            except (OSError, UnicodeError):
                if self.stop.is_set():
                    break
            if self.restore_at and monotonic() >= self.restore_at:
                print(f'Light: {self.steady} ({LIGHT_COLORS[self.steady]}) restored', flush=True)
                self.restore_at = None

    def close(self):
        self.stop.set()
        self.socket.close()
        self.thread.join(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--device', type=int)
    parser.add_argument('--host', default='127.0.0.1', help='App audio destination')
    parser.add_argument('--bind', default='127.0.0.1', help='Light listener address')
    parser.add_argument('--seconds', type=float, default=0)
    parser.add_argument('--silence', action='store_true', help='Send silence without opening microphone')
    args = parser.parse_args()
    config = load_config(args.config)
    monitor = LightMonitor(args.bind, config.light_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    source = None
    try:
        if not args.silence:
            source = LaptopMicSource(args.device)
        monitor.start()
        print(f'Mock voice ready: audio -> {args.host}:{config.audio_port}, lights :{config.light_port}', flush=True)
        started, next_packet = monotonic(), monotonic()
        while not args.seconds or monotonic() - started < args.seconds:
            packet = source.read_chunk() if source else b'\0' * 1024
            sock.sendto(packet, (args.host, config.audio_port))
            if source is None:
                next_packet += .032
                monitor.stop.wait(max(0, next_packet - monotonic()))
    except KeyboardInterrupt:
        pass
    finally:
        if source:
            source.close()
        sock.close()
        if monitor.thread.is_alive():
            monitor.close()
        else:
            monitor.socket.close()

if __name__ == '__main__':
    main()
