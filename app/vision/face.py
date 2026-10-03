"""YuNet face detector using the same detection tuple as YOLO."""
from pathlib import Path

import cv2

from app.vision.detector import Detection


class FaceDetector:
    def __init__(self, model_path='models/face_detection_yunet_2023mar.onnx', confidence=0.7):
        if not Path(model_path).is_file():
            raise FileNotFoundError(f'Missing {model_path}; run python -m tools.download_models')
        self.detector = cv2.FaceDetectorYN.create(str(model_path), '', (320, 320), confidence, 0.3, 5000)

    def detect(self, frame, target_class='face') -> list[Detection]:
        if target_class != 'face':
            return []
        height, width = frame.shape[:2]
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(frame)
        if faces is None:
            return []
        results = []
        for face in faces:
            x, y, w, h = map(float, face[:4])
            x1, y1 = max(0.0, x), max(0.0, y)
            x2, y2 = min(float(width), x + w), min(float(height), y + h)
            if x2 > x1 and y2 > y1:
                results.append(('face', float(face[-1]), x1, y1, x2 - x1, y2 - y1))
        return results
