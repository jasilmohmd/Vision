"""Laptop only: export the specified YOLOv8n model at 320 pixels."""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weights', default='yolov8n.pt')
    parser.add_argument('--output-dir', type=Path, default=Path('models'))
    args = parser.parse_args()
    from ultralytics import YOLO
    args.output_dir.mkdir(parents=True, exist_ok=True)
    weights = Path(args.weights)
    if args.weights == 'yolov8n.pt':
        weights = args.output_dir / weights.name
    exported = Path(YOLO(str(weights)).export(format='onnx', imgsz=320,
                    batch=1, dynamic=False, simplify=False, nms=False, opset=17, device='cpu'))
    destination = args.output_dir / exported.name
    if exported.resolve() != destination.resolve():
        shutil.copy2(exported, destination)
    print(f'Exported: {destination.resolve()}')


if __name__ == '__main__':
    main()
