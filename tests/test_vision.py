import cv2
import numpy as np
import pytest

from app.vision.detector import COCO_NAMES, decode_output, letterbox, YoloDetector
from app.vision.face import FaceDetector
from app.vision.tracker import TargetTracker, normalized_offset, create_tracker


def test_letterbox_rgb_scale_and_inverse_nms():
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[:] = (10, 20, 30)
    tensor, scales, padding = letterbox(frame, (320, 320))
    assert tensor.shape == (1, 3, 320, 320)
    assert padding == (0, 40)
    assert tensor[0, :, 40, 0] == pytest.approx(np.array([30, 20, 10]) / 255)
    # Two overlapping people, one dog; suppress person duplicate and filter dog.
    rows = np.zeros((3, 84), dtype=np.float32)
    rows[:, :4] = [[160, 160, 100, 100], [161, 161, 100, 100], [80, 100, 20, 20]]
    rows[0, 4], rows[1, 4], rows[2, 4 + 16] = 0.9, 0.8, 0.95
    found = decode_output(rows.T[None], frame.shape, scales, padding, COCO_NAMES, 'person')
    assert len(found) == 1
    assert found[0][2:] == pytest.approx((110, 70, 100, 100))
    dog = decode_output(rows[None], frame.shape, scales, padding, COCO_NAMES, 'dog')
    assert len(dog) == 1 and dog[0][0] == 'dog'
    with pytest.raises(ValueError):
        decode_output(rows[None], frame.shape, scales, padding, COCO_NAMES, 'unknown')


def test_non_square_inverse_and_clipping():
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    _, scales, padding = letterbox(frame, (320, 320))
    rows = np.zeros((1, 84), dtype=np.float32)
    rows[0, :4] = (160, 160, 400, 400)
    rows[0, 4] = .9
    found = decode_output(rows[None], frame.shape, scales, padding, COCO_NAMES, 'person')
    assert found[0][2:] == pytest.approx((0, 0, 200, 100))


def test_offset_sign_and_bounds():
    assert normalized_offset((140, 100, 40, 40), (240, 320, 3)) == (0, 0)
    assert normalized_offset((220, 160, 40, 40), (240, 320, 3)) == (.5, .5)
    assert normalized_offset((-1000, 1000, 10, 10), (240, 320, 3)) == (-1, 1)


class FakeDetector:
    def __init__(self, batches):
        self.batches = iter(batches)
        self.calls = 0

    def detect(self, frame, target):
        self.calls += 1
        return next(self.batches)


class FakeTracker:
    def __init__(self, fail=False):
        self.fail = fail
        self.box = None

    def init(self, frame, box):
        self.box = box

    def update(self, frame):
        return not self.fail, self.box


def test_redetection_interval_and_nearest_identity():
    detector = FakeDetector([
        [('person', .9, 10, 10, 20, 20)],
        [('person', .99, 100, 100, 20, 20), ('person', .6, 12, 12, 20, 20)],
    ])
    pipeline = TargetTracker(detector, detect_every_n_frames=2, tracker_factory=FakeTracker)
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    assert pipeline.update(frame)[0] == (10, 10, 20, 20)
    pipeline.update(frame)
    assert detector.calls == 1
    assert pipeline.update(frame)[0] == (12, 12, 20, 20)
    assert detector.calls == 2


def test_tracker_failure_redetects_and_missing_target_clears_box():
    detector = FakeDetector([[('person', .9, 10, 10, 20, 20)], [],
                             [('person', .8, 15, 15, 20, 20)]])
    pipeline = TargetTracker(detector, tracker_factory=lambda: FakeTracker(fail=True))
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    pipeline.update(frame)
    assert pipeline.update(frame) == (None, None)
    assert pipeline.update(frame)[0] == (15, 15, 20, 20)
    assert detector.calls == 3


def test_real_csrt_and_kcf_on_textured_frame():
    rng = np.random.default_rng(123)
    texture = rng.integers(0, 256, (60, 60, 3), dtype=np.uint8)
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    frame[70:130, 90:150] = texture
    for name in ('CSRT', 'KCF'):
        tracker = create_tracker(name)
        assert tracker.init(frame, (90, 70, 60, 60)) is not False
        ok, box = tracker.update(frame)
        assert ok
        assert box == pytest.approx((90, 70, 60, 60), abs=3)


def test_missing_models_give_setup_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match='export_onnx'):
        YoloDetector(tmp_path / 'missing.onnx')
    with pytest.raises(FileNotFoundError, match='download_models'):
        FaceDetector(tmp_path / 'missing.onnx')


def test_csrt_falls_back_to_kcf(monkeypatch):
    from types import SimpleNamespace
    from app.vision import tracker as module
    sentinel = object()

    def unavailable():
        raise cv2.error('CSRT not supported')

    monkeypatch.setattr(module, 'cv2', SimpleNamespace(
        error=cv2.error, TrackerCSRT_create=unavailable,
        TrackerKCF_create=lambda: sentinel))
    assert module.create_tracker() is sentinel
