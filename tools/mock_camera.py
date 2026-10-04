"""Laptop webcam implementing the S3 HTTP contract with a moving 320x240 crop."""
import argparse
from threading import Event, RLock, Thread
from time import monotonic
import cv2
import numpy as np
from flask import Flask, Response, jsonify, request
from werkzeug.serving import make_server
from app.config import load_config

class MockCamera:
    def __init__(self, source=0, image=None, synthetic=False):
        self.lock, self.stop = RLock(), Event()
        self.pan, self.tilt, self.held = 90, 90, None
        self.started = monotonic()
        self.capture_device, self.worker = None, None
        if image:
            self.frame = cv2.imread(str(image))
            if self.frame is None:
                raise ValueError(f'Cannot read image {image}')
        elif synthetic:
            self.frame = np.zeros((720, 1280, 3), np.uint8)
            cv2.rectangle(self.frame, (540, 200), (740, 600), (0, 255, 0), -1)
        else:
            self.capture_device = cv2.VideoCapture(source)
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            ok, self.frame = self.capture_device.read()
            if not ok:
                self.capture_device.release()
                raise RuntimeError('Webcam could not be opened; close other camera apps')
            self.worker = Thread(target=self._read, daemon=True)
            self.worker.start()
        self.control = Flask('mock_camera_control')
        self.stream = Flask('mock_camera_stream')
        self.servers, self.threads = [], []
        self._routes()

    def _read(self):
        while not self.stop.is_set():
            ok, frame = self.capture_device.read()
            if ok:
                with self.lock:
                    self.frame = frame
            else:
                self.stop.wait(.05)

    def crop(self):
        with self.lock:
            frame = self.frame.copy()
            pan, tilt = self.pan, self.tilt
        h, w = frame.shape[:2]
        if w < 320 or h < 240:
            frame = cv2.resize(frame, (max(320, w), max(240, h)))
            h, w = frame.shape[:2]
        x = round((pan - 10) / 160 * (w - 320))
        y = round((tilt - 40) / 100 * (h - 240))
        return frame[y:y+240, x:x+320]

    @staticmethod
    def jpeg(frame):
        ok, data = cv2.imencode('.jpg', frame)
        if not ok:
            raise RuntimeError('JPEG encoding failed')
        return data.tobytes()

    def _routes(self):
        @self.control.get('/move')
        def move():
            try:
                pan, tilt = int(request.args['pan']), int(request.args['tilt'])
            except (KeyError, ValueError):
                return jsonify(error='Integer pan and tilt required'), 400
            with self.lock:
                self.pan, self.tilt = max(10, min(170, pan)), max(40, min(140, tilt))
                return jsonify(pan=self.pan, tilt=self.tilt)

        @self.control.get('/capture')
        def capture():
            with self.lock:
                if self.held is None:
                    self.held = self.jpeg(self.frame)
                return Response(self.held, mimetype='image/jpeg')

        @self.control.get('/ack')
        def ack():
            with self.lock:
                self.held = None
            return jsonify(ok=True)

        @self.control.get('/status')
        def status():
            with self.lock:
                return jsonify(pan=self.pan, tilt=self.tilt, uptime_s=round(monotonic()-self.started), held_photo=self.held is not None, rssi=-30)

        @self.stream.get('/stream')
        def stream():
            def frames():
                while not self.stop.is_set():
                    jpeg = self.jpeg(self.crop())
                    yield b'--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(len(jpeg)).encode() + b'\r\n\r\n' + jpeg + b'\r\n'
                    self.stop.wait(.05)
            return Response(frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start(self, host='127.0.0.1', control_port=80, stream_port=81):
        for app, port in ((self.control, control_port), (self.stream, stream_port)):
            server = make_server(host, port, app, threaded=True)
            self.servers.append(server)
            thread = Thread(target=server.serve_forever, daemon=True)
            self.threads.append(thread)
            thread.start()
        return self

    def close(self):
        self.stop.set()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        if self.worker:
            self.worker.join(2)
        if self.capture_device:
            self.capture_device.release()
        for thread in self.threads:
            thread.join(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--source', default='0')
    parser.add_argument('--bind', default='127.0.0.1', help='Bind laptop LAN IP for Uno Q mock testing')
    parser.add_argument('--image')
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--seconds', type=float, default=0)
    args = parser.parse_args()
    config = load_config(args.config)
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    camera = MockCamera(int(args.source) if args.source.isdigit() else args.source, args.image, args.synthetic)
    try:
        camera.start(host=args.bind, control_port=config.camera_http_port, stream_port=config.camera_stream_port)
        print(f'Mock camera ready: control :{config.camera_http_port}, stream :{config.camera_stream_port}', flush=True)
        camera.stop.wait(args.seconds or None)
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()

if __name__ == '__main__':
    main()
