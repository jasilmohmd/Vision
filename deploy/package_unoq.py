"""Create explicit runtime/model archives and a separate laptop-mock config."""
import argparse
from dataclasses import asdict
import hashlib
import io
import ipaddress
import json
from pathlib import Path
import tarfile
import yaml
from app.config import DEFAULT_CONFIG_PATH, load_config

ROOT = Path(__file__).resolve().parent.parent
MODEL_NAMES = ('yolov8n.onnx', 'face_detection_yunet_2023mar.onnx', 'vosk-model-small-en-us-0.15')


def ipv4(value):
    return str(ipaddress.IPv4Address(value))


def mock_config(config, laptop_ip, unoq_ip):
    data = asdict(config)
    data.update(s3_ip=ipv4(laptop_ip), c3_ip=ipv4(laptop_ip), unoq_ip=ipv4(unoq_ip), photos_dir='photos')
    return data


def included(info):
    parts = Path(info.name).parts
    if any(part in ('__pycache__', '.venv', '.git') or part.startswith('.env') for part in parts):
        return None
    if info.name.endswith(('.pyc', '.pyo')) or Path(info.name).name == 'secrets.h':
        return None
    return info


def add_bytes(archive, name, data):
    info = tarfile.TarInfo(name)
    info.size, info.mode = len(data), 0o644
    archive.addfile(info, io.BytesIO(data))


def package(root, config, laptop_ip, unoq_ip, output):
    root, output = Path(root), Path(output)
    paths = [root / 'models' / name for name in MODEL_NAMES]
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f'Missing required model: {path}; follow README model setup')
    if not (paths[2] / 'am' / 'final.mdl').is_file():
        raise FileNotFoundError('Vosk model is incomplete: am/final.mdl missing')
    output.mkdir(parents=True, exist_ok=True)
    data = mock_config(config, laptop_ip, unoq_ip)
    model_files = []
    for path in paths:
        model_files.extend([path] if path.is_file() else sorted(item for item in path.rglob('*') if item.is_file()))
    manifest = [{'path': file.relative_to(root).as_posix(), 'size': file.stat().st_size,
                 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for file in model_files]
    source = output / 'phase5-source.tar.gz'
    models = output / 'phase5-models.tar.gz'
    with tarfile.open(source, 'w:gz') as archive:
        for name in ('app', 'tools', 'deploy', 'requirements-unoq.txt', 'README.md'):
            archive.add(root / name, arcname=name, filter=included)
        add_bytes(archive, 'config.phase5.yaml', yaml.safe_dump(data, sort_keys=False).encode())
        add_bytes(archive, 'deploy/phase5-model-manifest.json', json.dumps(manifest, indent=2).encode())
    with tarfile.open(models, 'w:gz') as archive:
        for path in paths:
            archive.add(path, arcname=path.relative_to(root).as_posix(), filter=included)
    (output / 'config.phase5.yaml').write_text(yaml.safe_dump(data, sort_keys=False), encoding='utf-8')
    report = dict(laptop_ip=data['s3_ip'], unoq_ip=data['unoq_ip'], model_files=len(manifest),
                  archives=[dict(filename=path.name, bytes=path.stat().st_size,
                                 sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in (source, models)])
    (output / 'phase5-package.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--laptop-ip', required=True, type=ipv4)
    parser.add_argument('--unoq-ip', required=True, type=ipv4)
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH)
    parser.add_argument('--output', type=Path, default=ROOT / 'logs')
    args = parser.parse_args()
    report = package(ROOT, load_config(args.config), args.laptop_ip, args.unoq_ip, args.output)
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
