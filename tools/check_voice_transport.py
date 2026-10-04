"""Bounded optional BLE/UDP audio delivery check; no camera actions or audio files."""
import argparse
import json
from pathlib import Path
from time import monotonic, sleep

from app.config import load_config
from app.voice.audio_source import UdpAudioSource


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--transport', choices=('udp', 'ble'), required=True)
    parser.add_argument('--address', help='Verified C3 BLE address; required for BLE')
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--lights', action='store_true', help='Cycle NeoPixel states; no movements')
    args = parser.parse_args(argv)
    if args.seconds <= 0 or (args.transport == 'ble' and not args.address):
        parser.error('Positive --seconds and verified --address for BLE are required')
    config = load_config(args.config)
    if args.transport == 'ble':
        from app.voice.ble_source import BleVoiceTransport
        source = lights = BleVoiceTransport(args.address)
        if not source.connected.wait(20):
            source.close()
            result = {'transport': 'ble', 'ok': False, 'error': 'C3 BLE connection not established within 20s'}
            print(json.dumps(result, indent=2))
            if args.report:
                args.report.write_text(json.dumps(result, indent=2) + '\n')
            return 1
    else:
        from app.io.light_client import LightClient
        source = UdpAudioSource(port=config.audio_port)
        lights = LightClient(config.c3_ip, config.light_port)
    try:
        # Baseline after connection; count actual delivery, never synthetic playout silence.
        if args.transport == 'ble':
            buffer = source.buffer
            with buffer.condition:
                baseline = buffer.received_samples
                buffer.max_gap = 0
                missing = buffer.missing_samples
        else:
            baseline = source.received_packets * 512
        started = monotonic()
        while monotonic() - started < args.seconds:
            if args.transport == 'ble':
                source.read_chunk()
            else:
                source.read_chunk()
        elapsed = monotonic() - started
        if args.transport == 'ble':
            with buffer.condition:
                samples = buffer.received_samples - baseline
                result = dict(transport='ble', address=args.address, seconds=round(elapsed, 3),
                              received_samples=samples, sample_rate=round(samples / elapsed, 2),
                              missing_samples=buffer.missing_samples - missing,
                              max_gap_s=round(buffer.max_gap, 3), invalid_packets=buffer.invalid_packets,
                              out_of_order=buffer.out_of_order, buffer_dropped_bytes=buffer.dropped_bytes,
                              playout_silence_chunks=buffer.silence_chunks, padded_samples=buffer.padded_samples,
                              gap_events=list(buffer.gap_events))
            result['ok'] = (samples / elapsed >= 14400 and result['missing_samples'] == 0
                            and result['invalid_packets'] == 0 and result['max_gap_s'] < .1
                            and result['padded_samples'] == 0 and result['buffer_dropped_bytes'] == 0)
        else:
            samples = source.received_packets * 512 - baseline
            result = dict(transport='udp', seconds=round(elapsed, 3), received_samples=samples,
                          sample_rate=round(samples / elapsed, 2), invalid_packets=source.invalid_packets,
                          dropped_packets=source.dropped_packets)
            result['ok'] = samples / elapsed >= 14400 and source.invalid_packets == 0
        if args.lights:
            for state in ('ready', 'heard', 'tracking', 'nosubject', 'saved', 'error', 'reconnect', 'sleep', 'ready'):
                lights.send(state)
                print(f'Light write requested: {state}', flush=True)
                sleep(1)
            result['light_check'] = 'writes requested; physical colour confirmation required'
        print(json.dumps(result, indent=2))
        if args.report:
            args.report.write_text(json.dumps(result, indent=2) + '\n')
        return 0 if result['ok'] else 1
    finally:
        source.close()
        if lights is not source:
            lights.close()


if __name__ == '__main__':
    raise SystemExit(main())
