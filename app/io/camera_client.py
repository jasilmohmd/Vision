"""S3 HTTP contract with bounded timeouts/retries and serialized requests."""
from threading import RLock
import requests


class CameraOffline(RuntimeError):
    pass


class CameraClient:
    def __init__(self, host, port=80, timeout=2, retries=2, session=None):
        self.base_url = f'http://{host}:{port}'
        self.timeout, self.retries = timeout, retries
        self.session = session or requests.Session()
        self.session.trust_env = False
        self.lock = RLock()

    def _get(self, path, params=None, jpeg=False):
        with self.lock:
            last_error = None
            for _ in range(self.retries + 1):
                try:
                    with self.session.get(self.base_url + path, params=params, timeout=self.timeout) as response:
                        response.raise_for_status()
                        if jpeg:
                            data = response.content
                            if response.headers.get('Content-Type', '').split(';')[0] != 'image/jpeg' or not data.startswith(b'\xff\xd8') or not data.endswith(b'\xff\xd9'):
                                raise ValueError('Camera returned an invalid JPEG response')
                            return data
                        result = response.json()
                        if not isinstance(result, dict):
                            raise ValueError('Camera returned non-object JSON')
                        return result
                except (requests.RequestException, ValueError) as error:
                    last_error = error
            raise CameraOffline(f'Camera request {path} failed after {self.retries + 1} attempts') from last_error

    def move(self, pan, tilt):
        result = self._get('/move', {'pan': int(round(pan)), 'tilt': int(round(tilt))})
        if any(type(result.get(axis)) is not int for axis in ('pan', 'tilt')):
            raise CameraOffline('Invalid move acknowledgement')
        return result

    def capture(self) -> bytes:
        return self._get('/capture', jpeg=True)

    def ack(self):
        if self._get('/ack').get('ok') is not True:
            raise CameraOffline('Invalid capture acknowledgement')

    def status(self):
        result = self._get('/status')
        if not {'pan', 'tilt', 'uptime_s', 'held_photo', 'rssi'} <= result.keys():
            raise CameraOffline('Incomplete camera status')
        return result

    def close(self):
        self.session.close()
