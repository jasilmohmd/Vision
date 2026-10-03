"""MJPEG reader thread with a latest-frame buffer and reconnect."""
import logging
from threading import Event, Lock, Thread
from time import monotonic
import cv2
import numpy as np
import requests


class MjpegStream:
    def __init__(self, url):
        self.url = url
        self.stopped = Event()
        self.lock = Lock()
        self.frame = None
        self.number = 0
        self.received_at = 0.0
        self.thread = Thread(target=self._run, name='mjpeg-reader', daemon=True)

    def start(self):
        self.thread.start()

    def latest(self):
        with self.lock:
            frame = self.frame.copy() if self.frame is not None else None
            return self.number, frame, self.received_at

    def _run(self):
        session = requests.Session()
        session.trust_env = False
        delay = .2
        try:
            while not self.stopped.is_set():
                try:
                    with session.get(self.url, stream=True, timeout=(2, 2)) as response:
                        response.raise_for_status()
                        buffer = b''
                        for chunk in response.iter_content(chunk_size=4096):
                            if self.stopped.is_set():
                                return
                            buffer += chunk
                            while True:
                                start = buffer.find(b'\xff\xd8')
                                end = buffer.find(b'\xff\xd9', start + 2) if start >= 0 else -1
                                if end < 0:
                                    break
                                jpeg, buffer = buffer[start:end + 2], buffer[end + 2:]
                                frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
                                if frame is not None:
                                    with self.lock:
                                        self.frame = frame
                                        self.number += 1
                                        self.received_at = monotonic()
                                    delay = .2
                            if len(buffer) > 2 * 1024 * 1024:
                                buffer = b''
                    raise requests.ConnectionError('MJPEG stream ended')
                except requests.RequestException as error:
                    logging.warning('Camera stream unavailable: %s', error)
                    self.stopped.wait(delay)
                    delay = min(2, delay * 2)
        finally:
            session.close()

    def close(self):
        self.stopped.set()
        if self.thread.is_alive():
            self.thread.join(timeout=3)
