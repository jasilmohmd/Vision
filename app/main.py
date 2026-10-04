"""Threaded laptop/Uno Q photography app. Phase 3 uses localhost board mocks."""
import argparse
from contextlib import ExitStack
import logging
from pathlib import Path
from queue import Empty
from threading import Event, Lock, Thread
from time import monotonic

from app.config import DEFAULT_CONFIG_PATH, load_config


def run(config, args):
    import cv2
    from app.io.camera_client import CameraClient, CameraOffline
    from app.io.light_client import LightClient
    from app.io.speaker import Speaker
    from app.control.controller import Controller
    from app.storage import PhotoStore
    from app.gallery.server import GalleryServer
    from app.state import StateMachine
    from app.vision.stream import MjpegStream
    from app.vision.detector import YoloDetector
    from app.vision.face import FaceDetector
    from app.vision.tracker import TargetTracker
    from app.voice.audio_source import LaptopMicSource, UdpAudioSource
    from app.voice.recognizer import VoiceRecognizer

    stop, display_lock = Event(), Lock()
    display = {'frame': None, 'box': None, 'offset': None}
    failures = []
    host = '127.0.0.1' if args.mock else config.s3_ip
    light_host = '127.0.0.1' if args.mock else config.c3_ip
    models = Path(args.models_dir)
    with ExitStack() as cleanup:
        camera = CameraClient(host, config.camera_http_port)
        cleanup.callback(camera.close)
        lights = LightClient(light_host, config.light_port)
        cleanup.callback(lights.close)
        speaker = Speaker(config.speaker_enabled)
        cleanup.callback(speaker.close)
        store = PhotoStore(config.photos_dir)
        controller = Controller(camera, config)
        status = camera.status()
        controller.sync(status['pan'], status['tilt'])
        detector = YoloDetector(models / 'yolov8n.onnx')
        face = FaceDetector(models / 'face_detection_yunet_2023mar.onnx')
        recognizer = VoiceRecognizer(models / 'vosk-model-small-en-us-0.15', config.vosk_conf_threshold)
        source = LaptopMicSource(args.device) if args.mic == 'laptop' else UdpAudioSource(port=config.audio_port)
        cleanup.callback(source.close)
        recognizer.calibrate(source)
        state = StateMachine(controller, camera, lights, store, speaker, config)
        cleanup.callback(state.close)
        stream = MjpegStream(f'http://{host}:{config.camera_stream_port}/stream')
        stream.start()
        cleanup.callback(stream.close)
        gallery = GalleryServer(store, port=config.gallery_port)
        gallery.start()
        cleanup.callback(gallery.close)

        def audio():
            try:
                recognizer.run(source, stop)
            except Exception as error:
                if not stop.is_set():
                    logging.exception('Audio worker stopped')
                    failures.append(error)
                    stop.set()

        def control():
            tracker, target, number = None, None, -1
            offset, box = None, None
            while not stop.is_set():
                began = monotonic()
                try:
                    while True:
                        try:
                            event = recognizer.events.get_nowait()
                        except Empty:
                            break
                        state.handle_event(event)
                    wanted = state.tracking_target
                    if wanted != target:
                        target = wanted
                        tracker = TargetTracker(face if target == 'face' else detector, target,
                                                config.detect_every_n_frames) if target else None
                        box, offset = None, None
                        number = -1
                    current, frame, received = stream.latest()
                    fresh = frame is not None and monotonic() - received < .5
                    if fresh and current != number:
                        number = current
                        box, offset = tracker.update(frame) if tracker else (None, None)
                    if not fresh:
                        offset, box = None, None
                    state.tick(offset)
                    with display_lock:
                        display.update(frame=frame, box=box, offset=offset)
                except CameraOffline as error:
                    logging.warning('%s', error)
                    lights.send('error')
                except Exception as error:
                    logging.exception('Control worker stopped')
                    failures.append(error)
                    stop.set()
                stop.wait(max(0, .1 - (monotonic() - began)))

        workers = [Thread(target=audio, name='voice-recognition', daemon=True),
                   Thread(target=control, name='control-loop', daemon=True)]
        for worker in workers:
            worker.start()
        logging.info('Ready. Say "camera track person", then "camera shoot". Gallery http://localhost:%s', config.gallery_port)
        started = monotonic()
        try:
            while not stop.is_set() and (not args.seconds or monotonic() - started < args.seconds):
                if args.preview:
                    with display_lock:
                        frame = display['frame'].copy() if display['frame'] is not None else None
                        box, offset = display['box'], display['offset']
                    if frame is not None:
                        if box:
                            x, y, w, h = map(round, box)
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f'{state.mode.value} pan={controller.pan} tilt={controller.tilt}', (5, 18), cv2.FONT_HERSHEY_SIMPLEX, .4, (255,255,255), 1)
                        if offset:
                            cv2.putText(frame, f'dx={offset[0]:+.2f} dy={offset[1]:+.2f}', (5, 36), cv2.FONT_HERSHEY_SIMPLEX, .4, (255,255,255), 1)
                        cv2.imshow('Vision - Phase 3 mock preview (Q exits)', frame)
                    if cv2.waitKey(1) & 255 == ord('q'):
                        break
                stop.wait(.025)
        except KeyboardInterrupt:
            pass
        finally:
            stop.set()
            source.close()
            for worker in workers:
                worker.join(7)
            if args.preview:
                cv2.destroyAllWindows()
        if failures:
            raise RuntimeError(str(failures[0])) from failures[0]
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH)
    parser.add_argument('--mock', action='store_true', help='Use localhost camera/light mocks')
    parser.add_argument('--mic', choices=('laptop', 'udp'), default='udp')
    parser.add_argument('--device', type=int, help='Laptop input device; used only with --mic laptop')
    parser.add_argument('--models-dir', default='models')
    parser.add_argument('--preview', action='store_true', help='Show crop, tracking box and angles; Q exits')
    parser.add_argument('--seconds', type=float, default=0, help='0 runs until Ctrl+C or Q')
    parser.add_argument('--check-config', action='store_true', help='Validate YAML and exit without opening devices')
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.seconds < 0:
        parser.error('--seconds cannot be negative')
    if args.check_config:
        print(f'Configuration valid. Photo directory: {config.photos_dir}')
        return 0
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    try:
        return run(config, args)
    except Exception:
        logging.exception('App could not continue')
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
