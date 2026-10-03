from dataclasses import replace
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
import json
import pytest
from app.config import Config
from app.control.controller import Controller
from app.storage import PhotoStore

JPEG = b'\xff\xd8photo\xff\xd9'

@pytest.fixture
def rig():
    camera = Mock()
    camera.move.side_effect = lambda pan, tilt: dict(pan=pan, tilt=tilt)
    now = [0.0]
    controller = Controller(camera, Config(), clock=lambda: now[0])
    return controller, camera, now

def test_dead_zone_and_gain(rig):
    control, camera, now = rig
    assert not control.track((.08, -.08))
    camera.move.assert_not_called()
    assert control.track((.25, -.25))
    assert (control.pan, control.tilt) == (93, 87)
    now[0] += .1
    control.track((1, -1))
    assert (control.pan, control.tilt) == (97, 83)

def test_rate_limit(rig):
    control, camera, now = rig
    control.track((1, 1))
    for time in (.01, .05, .099):
        now[0] = time
        assert not control.track((1, 1))
    now[0] = .1
    assert control.track((1, 1))
    assert camera.move.call_count == 2

def test_limits_inversion_and_manual(rig):
    control, camera, now = rig
    control.config = replace(Config(), invert_pan=True, invert_tilt=True)
    control.track((1, 1))
    assert (control.pan, control.tilt) == (86, 86)
    now[0] += .1
    control.manual('left', small=True)
    assert control.pan == 87
    now[0] += .1
    control.sync(169, 139)
    control.track((-1, -1))
    assert (control.pan, control.tilt) == (170, 140)
    now[0] += .1
    control.centre()
    assert (control.pan, control.tilt) == (90, 90)

@pytest.mark.parametrize('offset', [(float('nan'), 0), (2, 0), (0, float('inf'))])
def test_invalid_offsets(rig, offset):
    with pytest.raises(ValueError):
        rig[0].track(offset)

def test_numbering_restart_orphan_and_timestamp(tmp_path):
    store = PhotoStore(tmp_path)
    first = store.save(JPEG, 'camera shoot')
    assert first['filename'] == 'IMG_0001.jpg'
    assert datetime.fromisoformat(first['timestamp']).tzinfo is not None
    (tmp_path / 'IMG_0007.jpg').write_bytes(JPEG)
    second = PhotoStore(tmp_path).save(JPEG, 'camera burst')
    assert second['filename'] == 'IMG_0008.jpg'
    assert [p['command'] for p in store.list_photos()] == ['camera shoot', 'camera burst']
    assert (tmp_path / 'IMG_0001.jpg').read_bytes() == JPEG

def test_corrupt_index_is_preserved(tmp_path):
    (tmp_path / 'index.json').write_text('{oops')
    with pytest.raises(ValueError):
        PhotoStore(tmp_path).save(JPEG, 'camera shoot')
    assert (tmp_path / 'index.json').read_text() == '{oops'
    assert not list(tmp_path.glob('IMG_*'))

def test_failed_index_write_removes_unindexed_photo(tmp_path, monkeypatch):
    store = PhotoStore(tmp_path)
    store.save(JPEG, 'first')
    original = Path.replace
    def fail(path, destination):
        if path.name == 'index.json.tmp':
            raise OSError('disk full')
        return original(path, destination)
    monkeypatch.setattr(Path, 'replace', fail)
    with pytest.raises(OSError):
        store.save(JPEG, 'second')
    assert len(store.list_photos()) == 1
    assert not (tmp_path / 'IMG_0002.jpg').exists()

def test_bad_jpeg_and_large_number(tmp_path):
    store = PhotoStore(tmp_path)
    with pytest.raises(ValueError):
        store.save(b'bad', 'camera shoot')
    (tmp_path / 'IMG_9999.jpg').write_bytes(JPEG)
    assert store.save(JPEG, 'camera shoot')['filename'] == 'IMG_10000.jpg'
