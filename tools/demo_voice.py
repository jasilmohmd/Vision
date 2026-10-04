"""Print voice events from laptop mic or UDP; no camera/control actions."""
import argparse
from dataclasses import asdict
import json
import struct
from pathlib import Path
from queue import Empty
from time import monotonic

from app.config import load_config
from app.voice.audio_source import LaptopMicSource, UdpAudioSource
from app.voice.commands import COMMAND_PHRASES
from app.voice.recognizer import VoiceRecognizer


def print_events(events):
    drained = []
    while True:
        try:
            event = events.get_nowait()
        except Empty:
            return drained
        drained.append(event)
        print(json.dumps(asdict(event)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--mic', choices=['laptop', 'udp'], default='laptop')
    parser.add_argument('--device', type=int, help='Input device ID; default uses system input')
    parser.add_argument('--levels', action='store_true', help='Print input RMS/peak once per second for diagnosis')
    parser.add_argument('--model', default='models/vosk-model-small-en-us-0.15')
    parser.add_argument('--seconds', type=float, default=0, help='0 means run until Ctrl+C')
    parser.add_argument('--list-devices', action='store_true')
    parser.add_argument('--list-commands', action='store_true')
    parser.add_argument('--checklist', action='store_true', help='Guide all 19 commands, then background chatter')
    parser.add_argument('--background-seconds', type=float, default=20, help='Chatter duration in checklist mode')
    parser.add_argument('--report', type=Path, help='Checklist summary JSON only; no audio or chatter transcript')
    args = parser.parse_args()
    if args.list_commands:
        print('\n'.join(COMMAND_PHRASES))
        return
    if args.list_devices:
        import sounddevice as sd
        print(sd.query_devices())
        return
    if not 0 <= args.seconds < float('inf'):
        parser.error('--seconds must be finite and non-negative')
    if not 0 < args.background_seconds < float('inf'):
        parser.error('--background-seconds must be finite and positive')
    if args.checklist and args.mic != 'laptop':
        parser.error('--checklist requires --mic laptop for Phase 2 acceptance')
    if args.report and not args.checklist:
        parser.error('--report requires --checklist')
    source = None
    try:
        config = load_config(args.config)
        recognizer = VoiceRecognizer(args.model, config.vosk_conf_threshold)
        source = (LaptopMicSource(args.device) if args.mic == 'laptop'
                  else UdpAudioSource(port=config.audio_port))
        print('Keep quiet for two seconds while the microphone starts.', flush=True)
        recognizer.calibrate(source)
    except Exception as error:
        if source is not None:
            source.close()
        parser.exit(1, f'Voice setup failed: {error}\n')
    if args.mic == 'laptop':
        import sounddevice as sd
        print(f'Input device: {sd.query_devices(args.device, kind="input")["name"]}', flush=True)
    print('Listening at 16 kHz mono; say "camera <command>". Ctrl+C exits.', flush=True)
    if args.mic == 'udp':
        print(f'UDP listening on {source.address}', flush=True)
    checked = set()
    background_start = None
    false_commands = 0

    def consume():
        nonlocal background_start, false_commands
        for event in print_events(recognizer.events):
            if not args.checklist or event.kind != 'command':
                continue
            if background_start is not None:
                false_commands += 1
            else:
                checked.add(event.text)
                missing = [phrase for phrase in COMMAND_PHRASES if phrase not in checked]
                print(f'Commands checked: {len(checked)}/19', flush=True)
                if missing:
                    print(f'Next: {missing[0]}', flush=True)
                else:
                    background_start = monotonic()
                    print(f'Now talk normally for {args.background_seconds:g} seconds WITHOUT command phrases. '
                          'No command events should appear.', flush=True)

    if args.checklist:
        print('Stand 0.5-1 m from the laptop microphone. Say each prompted phrase, '
              'then pause for its command event. Repeat if low_confidence appears.', flush=True)
        print(f'Next: {COMMAND_PHRASES[0]}', flush=True)
    deadline = monotonic() + args.seconds if args.seconds else float('inf')
    next_level = monotonic()
    try:
        with source:
            try:
                while monotonic() < deadline:
                    chunk = source.read_chunk()
                    if args.levels and chunk and monotonic() >= next_level:
                        samples = [sample[0] for sample in struct.iter_unpack('<h', chunk)]
                        rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5 / 32768
                        peak = max(abs(sample) for sample in samples) / 32768
                        print(f'Input level: rms={rms:.5f} peak={peak:.5f}', flush=True)
                        next_level = monotonic() + 1
                    recognizer.process_chunk(chunk)
                    consume()
                    if background_start is not None and monotonic() - background_start >= args.background_seconds:
                        break
            except KeyboardInterrupt:
                pass
            finally:
                recognizer.discard_pending()
                consume()
    except Exception as error:
        parser.exit(1, f'Voice input failed: {error}\n')
    if args.checklist:
        observed = monotonic() - background_start if background_start is not None else 0
        report = dict(commands_recognised=sorted(checked),
                      missing_commands=[phrase for phrase in COMMAND_PHRASES if phrase not in checked],
                      background_seconds_observed=observed, background_seconds_required=args.background_seconds,
                      background_command_events=false_commands, confidence_threshold=config.vosk_conf_threshold,
                      device=args.device, distance_requires_user_confirmation='0.5-1 m')
        report['checks_passed'] = (len(checked) == 19 and observed >= args.background_seconds and false_commands == 0)
        print(json.dumps(report, indent=2), flush=True)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Stopped.', flush=True)


if __name__ == '__main__':
    main()
