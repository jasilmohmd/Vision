"""YOLOv8/YOLO11 raw ONNX detection; no PyTorch runtime dependency."""
import ast
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

Detection = tuple[str, float, float, float, float, float]
COCO_NAMES = (
    "person bicycle car motorcycle airplane bus train truck boat traffic_light "
    "fire_hydrant stop_sign parking_meter bench bird cat dog horse sheep cow "
    "elephant bear zebra giraffe backpack umbrella handbag tie suitcase frisbee "
    "skis snowboard sports_ball kite baseball_bat baseball_glove skateboard "
    "surfboard tennis_racket bottle wine_glass cup fork knife spoon bowl banana "
    "apple sandwich orange broccoli carrot hot_dog pizza donut cake chair couch "
    "potted_plant bed dining_table toilet tv laptop mouse remote keyboard "
    "cell_phone microwave oven toaster sink refrigerator book clock vase scissors "
    "teddy_bear hair_drier toothbrush"
).split()


def letterbox(frame, size):
    """Return NCHW RGB float tensor, actual x/y scale, and integer padding."""
    height, width = frame.shape[:2]
    target_w, target_h = size
    scale = min(target_w / width, target_h / height)
    resized_w, resized_h = round(width * scale), round(height * scale)
    left, top = (target_w - resized_w) // 2, (target_h - resized_h) // 2
    image = cv2.resize(frame, (resized_w, resized_h))
    image = cv2.copyMakeBorder(image, top, target_h - resized_h - top,
                              left, target_w - resized_w - left,
                              cv2.BORDER_CONSTANT, value=(114, 114, 114))
    tensor = np.ascontiguousarray(image[:, :, ::-1].transpose(2, 0, 1)[None], dtype=np.float32) / 255.0
    return tensor, (resized_w / width, resized_h / height), (left, top)


def decode_output(output, frame_shape, scales, padding, names, target_class,
                  confidence=0.35, nms_threshold=0.45):
    """Decode raw xywh + class scores, suppress overlap, restore image coords."""
    if target_class not in names:
        raise ValueError(f"Unknown class: {target_class}")
    rows = np.asarray(output)
    if rows.ndim != 3 or rows.shape[0] != 1:
        raise ValueError(f"Expected raw batch-one YOLO output, got {rows.shape}")
    rows = rows[0]
    channels = 4 + len(names)
    if rows.shape[0] == channels:
        rows = rows.T
    elif rows.shape[1] != channels:
        raise ValueError(f"Expected {channels} raw channels; export with nms=False")
    class_ids = rows[:, 4:].argmax(axis=1)
    scores = rows[np.arange(len(rows)), class_ids + 4]
    selected = (class_ids == names.index(target_class)) & (scores >= confidence)
    rows, scores = rows[selected], scores[selected]
    height, width = frame_shape[:2]
    boxes, valid_scores = [], []
    for row, score in zip(rows, scores):
        if not np.isfinite(row).all():
            continue
        cx, cy, w, h = row[:4]
        x1 = np.clip((cx - w / 2 - padding[0]) / scales[0], 0, width)
        y1 = np.clip((cy - h / 2 - padding[1]) / scales[1], 0, height)
        x2 = np.clip((cx + w / 2 - padding[0]) / scales[0], 0, width)
        y2 = np.clip((cy + h / 2 - padding[1]) / scales[1], 0, height)
        if x2 > x1 and y2 > y1:
            boxes.append([float(x1), float(y1), float(x2 - x1), float(y2 - y1)])
            valid_scores.append(float(score))
    if not boxes:
        return []
    indices = np.asarray(cv2.dnn.NMSBoxes(boxes, valid_scores, confidence, nms_threshold)).reshape(-1)
    return [(target_class, valid_scores[int(i)], *boxes[int(i)]) for i in indices]


class YoloDetector:
    def __init__(self, model_path='models/yolov8n.onnx', confidence=0.35, nms_threshold=0.45):
        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"Missing {path}; run python -m tools.export_onnx")
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        self.session = ort.InferenceSession(str(path), options, providers=['CPUExecutionProvider'])
        self.input = self.session.get_inputs()[0]
        shape = self.input.shape
        if len(shape) != 4 or shape[:2] != [1, 3] or not all(isinstance(v, int) for v in shape[2:]):
            raise ValueError('Use a static batch-one RGB export')
        if self.input.type != 'tensor(float)':
            raise ValueError('Use an FP32 export')
        self.size = (shape[3], shape[2])
        raw_names = self.session.get_modelmeta().custom_metadata_map.get('names')
        if raw_names:
            parsed = ast.literal_eval(raw_names)
            self.names = [parsed[i] for i in range(len(parsed))] if isinstance(parsed, dict) else list(parsed)
        else:
            self.names = COCO_NAMES
        self.confidence, self.nms_threshold = confidence, nms_threshold

    def detect(self, frame, target_class='person') -> list[Detection]:
        tensor, scales, padding = letterbox(frame, self.size)
        output = self.session.run(None, {self.input.name: tensor})[0]
        return decode_output(output, frame.shape, scales, padding, self.names,
                             target_class, self.confidence, self.nms_threshold)
