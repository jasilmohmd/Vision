"""CSRT/KCF tracking with periodic detection and nearest-target association."""
import cv2

Box = tuple[float, float, float, float]


def create_tracker(preferred='CSRT'):
    names = ('CSRT', 'KCF') if preferred.upper() == 'CSRT' else ('KCF',)
    for name in names:
        for namespace in (cv2, getattr(cv2, 'legacy', None)):
            factory = getattr(namespace, f'Tracker{name}_create', None)
            if factory:
                try:
                    return factory()
                except cv2.error:
                    continue
    raise RuntimeError('CSRT/KCF unavailable; install only opencv-contrib-python (or headless on Uno Q)')


def normalized_offset(box, frame_shape):
    height, width = frame_shape[:2]
    x, y, w, h = box
    return (max(-1.0, min(1.0, 2 * (x + w / 2) / width - 1)),
            max(-1.0, min(1.0, 2 * (y + h / 2) / height - 1)))


def clip_box(box, frame_shape):
    height, width = frame_shape[:2]
    x, y, w, h = map(float, box)
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(width, x + w), min(height, y + h)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return None
    return (x1, y1, x2 - x1, y2 - y1)


class TargetTracker:
    def __init__(self, detector, target_class='person', detect_every_n_frames=5,
                 tracker_factory=None, preferred='CSRT'):
        if detect_every_n_frames < 1:
            raise ValueError('Detection interval must be positive')
        self.detector = detector
        self.target_class = target_class
        self.interval = detect_every_n_frames
        self.factory = tracker_factory or (lambda: create_tracker(preferred))
        self.tracker = None
        self.box = None
        self.last_box = None
        self.frame_number = 0

    def update(self, frame) -> tuple[Box | None, tuple[float, float] | None]:
        failed = self.tracker is None
        if self.tracker is not None:
            ok, tracked = self.tracker.update(frame)
            self.box = clip_box(tracked, frame.shape) if ok else None
            failed = self.box is None
            if self.box is not None:
                self.last_box = self.box
        if failed or self.frame_number % self.interval == 0:
            detections = self.detector.detect(frame, self.target_class)
            candidates = []
            for detection in detections:
                box = clip_box(detection[2:], frame.shape)
                if box is not None:
                    candidates.append((detection[1], box))
            if candidates:
                if self.last_box is None:
                    chosen = max(candidates, key=lambda candidate: candidate[0])[1]
                else:
                    cx = self.last_box[0] + self.last_box[2] / 2
                    cy = self.last_box[1] + self.last_box[3] / 2
                    chosen = min(candidates, key=lambda candidate:
                                 (candidate[1][0] + candidate[1][2] / 2 - cx) ** 2 +
                                 (candidate[1][1] + candidate[1][3] / 2 - cy) ** 2)[1]
                self.tracker = self.factory()
                x, y, w, h = chosen
                x, y = int(x), int(y)
                roi = (x, y, min(frame.shape[1] - x, max(1, int(round(w)))),
                       min(frame.shape[0] - y, max(1, int(round(h)))))
                result = self.tracker.init(frame, roi)
                if result is False:
                    self.tracker, self.box = None, None
                else:
                    self.box, self.last_box = chosen, chosen
            else:
                self.tracker, self.box = None, None
        self.frame_number += 1
        if self.box is None:
            return None, None
        return self.box, normalized_offset(self.box, frame.shape)
