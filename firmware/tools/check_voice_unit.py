"""Record C3 UDP PCM for five seconds and cue every NeoPixel state."""
import argparse
import ipaddress
import math
from pathlib import Path
import socket
import struct
import time
import wave

STATES = ('ready', 'heard', 'tracking', 'nosubject', 'saved', 'error', 'reconnect', 'sleep')
PACKET_BYTES = 1024
SAMPLE_RATE = 16000


def levels(pcm):
    samples = [value[0] for value in struct.iter_unpack('<h', pcm)]
    if not samples:
        return 0.0, 0
    return math.sqrt(sum(value * value for value in samples) / len(samples)), max(map(abs, samples))


def check(ip, bind, output):
    # Destination UNOQ_IP must be the machine running this check, not another receiver.
    audio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    lights = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    trigger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        audio.bind((bind, 5005))
        trigger.bind((bind, 5007))
        trigger.setblocking(False)
        audio.settimeout(10)
        print(f'Waiting for {ip}: UDP5005, expected 1024-byte PCM packets', flush=True)
        while True:
            packet, peer = audio.recvfrom(65535)
            if peer[0] == ip:
                break
        started = time.monotonic()
        pcm = bytearray()
        count = malformed = 0
        while True:
            if len(packet) == PACKET_BYTES:
                pcm.extend(packet)
                count += 1
            else:
                malformed += 1
            remaining = 5 - (time.monotonic() - started)
            if remaining <= 0:
                break
            audio.settimeout(remaining)
            try:
                packet, peer = audio.recvfrom(65535)
            except socket.timeout:
                break
            while peer[0] != ip:
                remaining = 5 - (time.monotonic() - started)
                if remaining <= 0:
                    break
                audio.settimeout(remaining)
                try:
                    packet, peer = audio.recvfrom(65535)
                except socket.timeout:
                    break
            if peer[0] != ip:
                break
        elapsed = time.monotonic() - started
        rms, peak = levels(pcm)
        expected = elapsed * SAMPLE_RATE / 512
        shortfall = max(0.0, 100 * (1 - count / expected)) if expected else 0.0
        print(f'packets={count} malformed={malformed} observed={elapsed:.2f}s '
              f'PCM={len(pcm) / (2 * SAMPLE_RATE):.2f}s RMS={rms:.1f} peak={peak}', flush=True)
        print(f'Estimated rate shortfall={shortfall:.1f}% (raw PCM has no sequence numbers; exact loss is unavailable).')
        if not pcm or malformed:
            raise ValueError('No valid PCM or malformed packets received')
        output.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(pcm)
        print(f'WAV saved locally: {output.resolve()}; listen and confirm speech clarity.', flush=True)
        print('Watch the NeoPixel; each state below lasts one second.', flush=True)
        for state in STATES:
            print(f'light {state}', flush=True)
            lights.sendto(state.encode('ascii'), (ip, 5006))
            time.sleep(1)
        lights.sendto(b'ready', (ip, 5006))
        shoots = 0
        while True:
            try:
                message, peer = trigger.recvfrom(128)
            except BlockingIOError:
                break
            if peer[0] == ip and message == b'shoot':
                shoots += 1
        print(f'IR shoot messages={shoots}; IR omitted in this prototype.')
        if shortfall > 20:
            raise ValueError('Audio rate shortfall exceeds 20%; check signal and receiver load')
        print('PASS packet format/rate checks; colours and microphone quality need user confirmation.')
        return 0
    except (OSError, ValueError) as error:
        print(f'FAIL: {error}; check destination IP, exclusive UDP5005 receiver and network.')
        return 1
    finally:
        audio.close()
        lights.close()
        trigger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ip', required=True, type=ipaddress.IPv4Address)
    parser.add_argument('--bind', default='0.0.0.0', type=ipaddress.IPv4Address)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().parents[1] / '.build' / 'voice_checks' / 'check.wav')
    args = parser.parse_args()
    return check(str(args.ip), str(args.bind), args.output)


if __name__ == '__main__':
    raise SystemExit(main())
