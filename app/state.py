"""Control state and cancellable photo jobs; disk save always precedes ACK."""
import logging
from enum import Enum
from threading import Event, RLock, Thread
from time import monotonic

log = logging.getLogger(__name__)

class Mode(str, Enum):
    SLEEP = 'SLEEP'
    IDLE = 'IDLE'
    TRACKING = 'TRACKING'
    SHOOTING = 'SHOOTING'
    TIMER = 'TIMER'

class StateMachine:
    def __init__(self, controller, camera, lights, store, speaker, config,
                 clock=monotonic, timer_interval=1.0, burst_interval=.4):
        self.controller, self.camera, self.lights = controller, camera, lights
        self.store, self.speaker, self.config = store, speaker, config
        self.clock, self.timer_interval, self.burst_interval = clock, timer_interval, burst_interval
        self.mode, self.target = Mode.IDLE, None
        self.resume_mode = Mode.IDLE
        self.lock, self.cancel = RLock(), Event()
        self.worker = None
        self.offset, self.offset_at = None, float('-inf')
        self.missing_since = None
        self.capturing, self.pending_ack = False, False
        self.lights.send('ready')

    @property
    def tracking_target(self):
        with self.lock:
            active = self.mode == Mode.TRACKING or (self.mode == Mode.SHOOTING and self.resume_mode == Mode.TRACKING)
            return self.target if active and not self.capturing else None

    def handle_event(self, event):
        if event.kind == 'command':
            self.handle(event.command, event.text)
        elif self.mode != Mode.SLEEP:
            self.lights.send('heard' if event.kind == 'heard' else 'error')

    def handle(self, command, text=''):
        with self.lock:
            if command is None or (self.mode == Mode.SLEEP and command.action != 'wake'):
                return
            action = command.action
            log.info('Command: %s', text or action)
            if action == 'sleep':
                self.cancel.set()
                self.mode, self.target = Mode.SLEEP, None
                self.lights.send('sleep')
            elif action == 'wake':
                if self.mode == Mode.SLEEP:
                    self.mode = Mode.IDLE
                    self.lights.send('ready')
            elif action == 'stop_tracking':
                self.target = None
                self.resume_mode = Mode.IDLE
                if self.mode == Mode.TRACKING:
                    self.mode = Mode.IDLE
                    self.lights.send('ready')
            elif self.mode in (Mode.IDLE, Mode.TRACKING):
                if action == 'track':
                    self.mode, self.target = Mode.TRACKING, command.target
                    self.offset, self.offset_at = None, float('-inf')
                    self.missing_since = self.clock()
                    self.lights.send('tracking')
                elif action == 'move':
                    self.controller.manual(command.direction, command.small)
                elif action == 'centre':
                    self.controller.centre()
                elif action in ('shoot', 'burst', 'timer'):
                    if self.worker and self.worker.is_alive():
                        return
                    self.resume_mode = self.mode
                    self.mode = Mode.TIMER if action == 'timer' else Mode.SHOOTING
                    self.cancel.clear()
                    self.worker = Thread(target=self._shoot_job, args=(action, text or f'camera {action}'), daemon=True)
                    self.worker.start()

    def tick(self, offset):
        with self.lock:
            now = self.clock()
            self.offset, self.offset_at = offset, now
            if self.tracking_target is None:
                return
            if offset is None:
                if self.missing_since is None:
                    self.missing_since = now
                if now - self.missing_since > 2 and self.lights.steady_state != 'nosubject':
                    self.lights.send('nosubject')
            else:
                self.missing_since = None
                if self.lights.steady_state != 'tracking':
                    self.lights.send('tracking')
                self.controller.track(offset)

    def _wait_centred(self):
        deadline = monotonic() + self.config.centre_timeout_s
        while not self.cancel.is_set():
            with self.lock:
                if self.resume_mode != Mode.TRACKING:
                    return
                if self.offset is not None and self.clock() - self.offset_at < .5 and all(abs(v) <= self.config.dead_zone for v in self.offset):
                    return
            if monotonic() >= deadline or self.cancel.wait(.025):
                return

    def _shoot_job(self, action, text):
        try:
            if action == 'timer':
                for _ in range(3):
                    if self.cancel.is_set():
                        return
                    self.lights.send('heard')
                    if self.cancel.wait(self.timer_interval):
                        return
                with self.lock:
                    if self.cancel.is_set():
                        return
                    self.mode = Mode.SHOOTING
            self._wait_centred()
            for index in range(3 if action == 'burst' else 1):
                with self.lock:
                    if self.cancel.is_set():
                        return
                    self.capturing = True
                try:
                    if self.pending_ack:
                        self.camera.ack()
                        self.pending_ack = False
                    photo = self.camera.capture()
                    entry = self.store.save(photo, text)
                    self.pending_ack = True
                    self.camera.ack()
                    self.pending_ack = False
                    self.lights.send('saved')
                    self.speaker.say(f"Photo {int(entry['filename'][4:-4])} saved")
                    log.info('Saved %s', entry['filename'])
                finally:
                    with self.lock:
                        self.capturing = False
                if index < 2 and action == 'burst' and self.cancel.wait(self.burst_interval):
                    return
        except Exception:
            log.exception('Photo job failed; unsaved captures remain held by camera')
            if not self.cancel.is_set():
                self.lights.send('error')
        finally:
            with self.lock:
                if self.mode in (Mode.SHOOTING, Mode.TIMER):
                    self.mode = self.resume_mode
                    steady = 'tracking' if self.mode == Mode.TRACKING else 'ready'
                    if self.lights.steady_state != steady:
                        self.lights.send(steady)

    def close(self):
        self.cancel.set()
        if self.worker:
            self.worker.join(13)
