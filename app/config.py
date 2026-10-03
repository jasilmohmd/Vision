"""Typed configuration shared by laptop and Uno Q runtimes."""

from dataclasses import dataclass, fields
from pathlib import Path
from typing import get_type_hints

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


@dataclass(frozen=True)
class Config:
    s3_ip: str = "192.168.43.101"
    c3_ip: str = "192.168.43.102"
    unoq_ip: str = "192.168.43.103"
    camera_http_port: int = 80
    camera_stream_port: int = 81
    audio_port: int = 5005
    light_port: int = 5006
    shoot_port: int = 5007
    gallery_port: int = 8080
    detect_every_n_frames: int = 5
    dead_zone: float = 0.08
    gain_deg: float = 12.0
    max_step_deg: float = 4.0
    pan_min: int = 10
    pan_max: int = 170
    tilt_min: int = 40
    tilt_max: int = 140
    invert_pan: bool = False
    invert_tilt: bool = False
    vosk_conf_threshold: float = 0.7
    centre_timeout_s: float = 1.5
    photos_dir: Path = Path("photos")


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    """Load YAML, reject invalid values, and resolve photo paths beside it."""
    path = Path(path).expanduser().resolve()
    with path.open(encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("Configuration must be a YAML mapping")
    hints = get_type_hints(Config)
    unknown = set(data) - {field.name for field in fields(Config)}
    if unknown:
        raise ValueError(f"Unknown configuration keys: {', '.join(sorted(map(str, unknown)))}")
    for name, value in data.items():
        expected = hints[name]
        if expected is Path:
            valid = isinstance(value, str) and bool(value.strip())
        elif expected is float:
            valid = type(value) in (int, float)
        else:
            valid = type(value) is expected
        if not valid:
            raise ValueError(f"Invalid type for {name}: expected {expected.__name__}")
        if expected is float:
            data[name] = float(value)
    photo_path = Path(data.get("photos_dir", "photos")).expanduser()
    data["photos_dir"] = (path.parent / photo_path).resolve()
    config = Config(**data)
    for name in ("s3_ip", "c3_ip", "unoq_ip"):
        if not getattr(config, name).strip():
            raise ValueError(f"{name} must not be empty")
    for name in ("camera_http_port", "camera_stream_port", "audio_port", "light_port", "shoot_port", "gallery_port"):
        if not 1 <= getattr(config, name) <= 65535:
            raise ValueError(f"{name} must be between 1 and 65535")
    if config.detect_every_n_frames < 1:
        raise ValueError("detect_every_n_frames must be positive")
    if not 0 <= config.dead_zone <= 1 or not 0 <= config.vosk_conf_threshold <= 1:
        raise ValueError("dead_zone and vosk_conf_threshold must be between 0 and 1")
    for name in ("gain_deg", "max_step_deg", "centre_timeout_s"):
        value = getattr(config, name)
        if not 0 < value < float("inf"):
            raise ValueError(f"{name} must be finite and positive")
    for axis in ("pan", "tilt"):
        if not 0 <= getattr(config, f"{axis}_min") < getattr(config, f"{axis}_max") <= 180:
            raise ValueError(f"{axis} limits must satisfy 0 <= min < max <= 180")
    return config
