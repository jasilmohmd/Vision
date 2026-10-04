"""Validate runtime dependencies/models without opening cameras or microphones."""
import argparse
from importlib import metadata
import hashlib
import json
from pathlib import Path
import platform
import tempfile

from app.config import load_config


def check_model_manifest(root, manifest):
    root = Path(root).resolve()
    entries = json.loads(Path(manifest).read_text(encoding='utf-8'))
    for entry in entries:
        path = (root / entry['path']).resolve()
        if not path.is_relative_to(root / 'models'):
            raise ValueError('Manifest path must be inside models/')
        if path.stat().st_size != entry['size'] or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Model checksum mismatch: {entry["path"]}')
    return len(entries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--models-dir', type=Path, default=Path('models'))
    parser.add_argument('--require-linux', action='store_true')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.require_linux and platform.system() != 'Linux':
        parser.error('This deployment must run on Linux')
    config = load_config(args.config)
    import cv2
    import onnxruntime
    import numpy
    from app.vision.detector import YoloDetector
    from app.vision.face import FaceDetector
    from app.vision.tracker import create_tracker
    from app.voice.recognizer import VoiceRecognizer
    variants = []
    for name in ('opencv-python', 'opencv-python-headless', 'opencv-contrib-python', 'opencv-contrib-python-headless'):
        try:
            metadata.version(name)
            variants.append(name)
        except metadata.PackageNotFoundError:
            pass
    if len(variants) != 1 or 'contrib' not in variants[0]:
        raise RuntimeError(f'Install exactly one contrib cv2 distribution; found {variants}')
    if args.require_linux and variants[0] != 'opencv-contrib-python-headless':
        raise RuntimeError('Uno Q deployment requires opencv-contrib-python-headless')
    export_packages = []
    for name in ('torch', 'ultralytics'):
        try:
            metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
        export_packages.append(name)
        if args.require_linux:
            raise RuntimeError(f'{name} is an export dependency; use a separate runtime venv')
    if args.manifest:
        verified = check_model_manifest(Path.cwd(), args.manifest)
    else:
        verified = None
    detector = YoloDetector(args.models_dir / 'yolov8n.onnx')
    face = FaceDetector(args.models_dir / 'face_detection_yunet_2023mar.onnx')
    recognizer = VoiceRecognizer(args.models_dir / 'vosk-model-small-en-us-0.15', config.vosk_conf_threshold)
    create_tracker('CSRT')
    create_tracker('KCF')
    config.photos_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=config.photos_dir, prefix='.runtime-check-', delete=True) as probe:
        probe.write(b'write-check')
        probe.flush()
    report = dict(platform=platform.system(), architecture=platform.machine(), python=platform.python_version(),
                  opencv=cv2.__version__, opencv_distribution=variants[0], onnxruntime=onnxruntime.__version__,
                  numpy=numpy.__version__, laptop_export_packages=export_packages, models_loaded=['YOLO ONNX', 'YuNet', 'Vosk'],
                  trackers=['CSRT', 'KCF'], model_checksums_verified=verified, photos_writable=True,
                  camera_host=config.s3_ip, light_host=config.c3_ip, gallery_port=config.gallery_port)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
