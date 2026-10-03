"""Webcam/video target box and normalised offset overlay; q/ESC exits."""
import argparse
import cv2
from tools.vision_common import add_options, build_pipeline, open_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_options(parser)
    parser.add_argument('--headless', action='store_true', help='Print offsets without a preview window')
    args = parser.parse_args()
    if args.frames < 0:
        parser.error('--frames must be non-negative')
    try:
        _, tracker = build_pipeline(args)
        capture = open_source(args.source)
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    count = 0
    try:
        while not args.frames or count < args.frames:
            ok, frame = capture.read()
            if not ok:
                if count == 0:
                    raise RuntimeError('No frames received')
                break
            frame = cv2.resize(frame, (320, 240))
            box, offset = tracker.update(frame)
            print(f'frame={count} box={box} offset={offset}', flush=True)
            if not args.headless:
                if box is not None:
                    x, y, w, h = map(int, box)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = 'No target' if offset is None else f'{args.target} dx={offset[0]:+.2f} dy={offset[1]:+.2f}'
                cv2.putText(frame, text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                cv2.imshow('Phase 1 vision - q/ESC to quit', frame)
                if cv2.waitKey(1) & 0xff in (ord('q'), 27):
                    break
            count += 1
    finally:
        capture.release()
        if not args.headless:
            cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
