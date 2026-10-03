from pathlib import Path

import pytest

from app.config import load_config
from app.main import main


def test_default_contract():
    config = load_config()
    assert (config.camera_http_port, config.camera_stream_port) == (80, 81)
    assert (config.audio_port, config.light_port, config.shoot_port, config.gallery_port) == (5005, 5006, 5007, 8080)
    assert (config.pan_min, config.pan_max, config.tilt_min, config.tilt_max) == (10, 170, 40, 140)
    assert config.photos_dir.is_absolute()


def test_override_and_relative_photos(tmp_path):
    path = tmp_path / "custom.yaml"
    path.write_text("s3_ip: localhost\ngain_deg: 6\ninvert_pan: true\nphotos_dir: images\n", encoding="utf-8")
    config = load_config(path)
    assert config.s3_ip == "localhost"
    assert config.gain_deg == 6.0
    assert config.invert_pan is True
    assert config.photos_dir == tmp_path / "images"
    assert main(["--config", str(path)]) == 0


@pytest.mark.parametrize("contents", [
    "- not a mapping", "unknown: 1", "audio_port: 0", "pan_min: 175",
    "invert_pan: 'false'", "detect_every_n_frames: true", "dead_zone: 2",
    "vosk_conf_threshold: -1", "gain_deg: .nan", "centre_timeout_s: 0",
    "photos_dir: ''", "s3_ip: ''",
])
def test_invalid_configuration(tmp_path, contents):
    path = tmp_path / "invalid.yaml"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(path)


def test_help_does_not_load_config(capsys):
    with pytest.raises(SystemExit) as result:
        main(["--config", "missing.yaml", "--help"])
    assert result.value.code == 0
    assert "--config" in capsys.readouterr().out
