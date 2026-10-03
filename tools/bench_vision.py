"""Measure detector-only and detector+tracker processing FPS, excluding capture."""
import argparse
import json
from pathlib import Path
from time import perf_counter
import cv2
from tools.vision_common import add_options, build_pipeline, open_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_options(parser)
    parser.set_defaults(frames=100)
    parser.add_argument('--output', type=Path, help='Optional JSON benchmark report')
    args = parser.parse_args()
    if args.frames < 1:
        parser.error('--frames must be positive')
    detector, tracker = build_pipeline(args)
    capture = open_source(args.source)
    frames = []
    try:
        for _ in range(args.frames):
            ok, frame = capture.read()
            if not ok:
                break
            frames.append(cv2.resize(frame, (320, 240)))
    finally:
        capture.release()
    if not frames:
        parser.error('No frames received')
    # Warm up model before timing; pipeline starts with fresh tracking state.
    detector.detect(frames[0], args.target)
    detections = 0
    start = perf_counter()
    for frame in frames:
        detections += bool(detector.detect(frame, args.target))
    detection_seconds = perf_counter() - start
    tracked = 0
    start = perf_counter()
    for frame in frames:
        tracked += tracker.update(frame)[0] is not None
    tracking_seconds = perf_counter() - start
    report = dict(source=args.source, target=args.target, tracker=args.tracker,
                  frame_size=[320, 240], frames=len(frames),
                  detector_only_fps=len(frames) / detection_seconds,
                  detector_tracker_fps=len(frames) / tracking_seconds,
                  detected_frames=detections, tracked_frames=tracked,
                  detect_every_n_frames=tracker.interval)
    print(json.dumps(report, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
