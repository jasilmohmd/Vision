"""Shared CLI options and sources for Phase 1 demo/benchmark."""
import cv2
from app.config import load_config
from app.vision.detector import YoloDetector
from app.vision.face import FaceDetector
from app.vision.tracker import TargetTracker


def add_options(parser):
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--source', default='0', help='Webcam index or video file')
    parser.add_argument('--target', choices=['person', 'face', 'dog', 'cat'], default='person')
    parser.add_argument('--model', default='models/yolov8n.onnx')
    parser.add_argument('--face-model', default='models/face_detection_yunet_2023mar.onnx')
    parser.add_argument('--tracker', choices=['CSRT', 'KCF'], default='CSRT')
    parser.add_argument('--frames', type=int, default=0, help='Frame limit; 0 means unlimited in demo')


def build_pipeline(args):
    config = load_config(args.config)
    detector = FaceDetector(args.face_model) if args.target == 'face' else YoloDetector(args.model)
    tracker = TargetTracker(detector, args.target, config.detect_every_n_frames, preferred=args.tracker)
    return detector, tracker


def open_source(source):
    capture = cv2.VideoCapture(int(source) if source.isdecimal() else source)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f'Cannot open camera/video source: {source}')
    return capture
