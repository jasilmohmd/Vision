"""Runtime recovery and bounded, structured operational logging."""
from datetime import datetime, timezone
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from time import monotonic

log = logging.getLogger(__name__)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        data = dict(timestamp=datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
                    level=record.levelname, logger=record.name, message=record.getMessage())
        if record.exc_info:
            data['exception'] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)


def configure_logging(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    handler = TimedRotatingFileHandler(directory / 'vision.jsonl', when='midnight',
                                      backupCount=7, encoding='utf-8', utc=True)
    handler.setFormatter(JsonFormatter())
    logging.getLogger().addHandler(handler)
    return handler


class AudioWatchdog:
    def __init__(self, clock=monotonic, timeout=5):
        self.clock, self.timeout = clock, timeout
        self.started = clock()
        self.silent = False

    def poll(self, last_received):
        reference = self.started if last_received is None else last_received
        silent = self.clock() - reference > self.timeout
        if silent and not self.silent:
            log.warning('Voice unit has sent no valid audio packet for over %gs; app remains running', self.timeout)
        elif self.silent and not silent:
            log.info('Voice unit audio delivery resumed')
        self.silent = silent


class CameraRecovery:
    def __init__(self, camera, controller, lights, speaker, clock=monotonic):
        self.camera, self.controller, self.lights, self.speaker = camera, controller, lights, speaker
        self.clock = clock
        self.online = False
        self.reported_offline = False
        self.next_retry = 0
        self.delay = .2

    def offline(self, reason):
        if self.online or not self.reported_offline:
            log.warning('Camera unavailable: %s; tracking target retained for recovery', reason)
            self.lights.set_reconnecting(True)
            self.reported_offline = True
        self.online = False

    def poll(self, fresh, freshness_check=None):
        from app.io.camera_client import CameraOffline
        if not fresh:
            self.offline('no fresh camera frames')
            return False
        if self.online:
            return True
        now = self.clock()
        if now < self.next_retry:
            return False
        try:
            status = self.camera.status()
            self.controller.sync(status['pan'], status['tilt'])
        except CameraOffline as error:
            self.offline(str(error))
            self.next_retry = self.clock() + self.delay
            self.delay = min(2, self.delay * 2)
            return False
        # /status may block long enough that the caller's original frame expires.
        # Announce recovery only if the stream is still fresh after the request.
        if freshness_check is not None and not freshness_check():
            self.offline('no fresh camera frames after status check')
            self.next_retry = self.clock() + self.delay
            self.delay = min(2, self.delay * 2)
            return False
        self.online = True
        self.reported_offline = False
        self.delay = .2
        self.next_retry = 0
        self.lights.set_reconnecting(False)
        self.speaker.say('Camera ready')
        log.info('Camera ready; control positions synchronized')
        return True
