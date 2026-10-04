from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tarfile
import pytest
import yaml
from app.config import Config, load_config
from deploy.package_unoq import package, mock_config
from tools.check_runtime import check_model_manifest


def fixture_project(root):
    for name in ('app', 'tools', 'deploy'):
        (root / name).mkdir()
        (root / name / 'sample.py').write_text('pass')
    (root / 'app' / '__pycache__').mkdir()
    (root / 'app' / '__pycache__' / 'sample.pyc').write_bytes(b'cache')
    (root / 'app' / '.env').write_text('PRIVATE')
    (root / 'requirements-unoq.txt').write_text('requests')
    (root / 'README.md').write_text('runtime')
    models = root / 'models'
    models.mkdir()
    for name in ('yolov8n.onnx', 'face_detection_yunet_2023mar.onnx'):
        (models / name).write_bytes(b'model')
    (models / 'vosk-model-small-en-us-0.15' / 'am').mkdir(parents=True)
    (models / 'vosk-model-small-en-us-0.15' / 'am' / 'final.mdl').write_bytes(b'voice model')
    (models / 'yolov8n.pt').write_bytes(b'export weights')
    (models / 'private.jpg').write_bytes(b'private photo')
    (root / 'firmware').mkdir()
    (root / 'firmware' / 'secrets.h').write_text('PRIVATE')
    (root / 'photos').mkdir()
    (root / 'photos' / 'IMG_0001.jpg').write_bytes(b'private photo')


def test_explicit_package_and_mock_config(tmp_path):
    fixture_project(tmp_path)
    original = replace(Config(), photos_dir=tmp_path / 'photos')
    report = package(tmp_path, original, '192.168.29.58', '192.168.29.199', tmp_path / 'logs')
    assert report['model_files'] == 3
    with tarfile.open(tmp_path / 'logs' / 'phase5-source.tar.gz') as archive:
        names = archive.getnames()
        assert not any('firmware' in name or 'photos' in name or '.env' in name or '__pycache__' in name for name in names)
        data = yaml.safe_load(archive.extractfile('config.phase5.yaml'))
        assert data['s3_ip'] == data['c3_ip'] == '192.168.29.58'
        assert data['unoq_ip'] == '192.168.29.199' and data['photos_dir'] == 'photos'
        assert data['camera_http_port'] == 80 and data['audio_port'] == 5005
        manifest = json.load(archive.extractfile('deploy/phase5-model-manifest.json'))
    with tarfile.open(tmp_path / 'logs' / 'phase5-models.tar.gz') as archive:
        assert not any(name.endswith(('.pt', '.jpg')) for name in archive.getnames())
    assert original.s3_ip == Config().s3_ip and original.photos_dir == tmp_path / 'photos'
    assert load_config(tmp_path / 'logs' / 'config.phase5.yaml').photos_dir == tmp_path / 'logs' / 'photos'
    manifest_file = tmp_path / 'manifest.json'
    manifest_file.write_text(json.dumps(manifest))
    assert check_model_manifest(tmp_path, manifest_file) == 3
    (tmp_path / manifest[0]['path']).write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='checksum mismatch'):
        check_model_manifest(tmp_path, manifest_file)


def test_missing_models_prevents_package(tmp_path):
    fixture_project(tmp_path)
    (tmp_path / 'models' / 'yolov8n.onnx').unlink()
    with pytest.raises(FileNotFoundError):
        package(tmp_path, Config(), '192.168.29.58', '192.168.29.199', tmp_path / 'logs')
    assert not (tmp_path / 'logs').exists()


@pytest.mark.parametrize('address', ['bad', '::1', '192.168.29.999'])
def test_bad_addresses_rejected(address):
    with pytest.raises(ValueError):
        mock_config(Config(), address, '192.168.29.199')


def test_manifest_cannot_escape_models(tmp_path):
    (tmp_path / 'outside').write_bytes(b'outside')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps([dict(path='outside', size=7, sha256=hashlib.sha256(b'outside').hexdigest())]))
    with pytest.raises(ValueError, match='inside models'):
        check_model_manifest(tmp_path, manifest)
