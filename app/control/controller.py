"""Normalised image offsets to clamped/rate-limited absolute servo targets."""
import math
from time import monotonic


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class Controller:
    def __init__(self, camera, config, clock=monotonic):
        self.camera, self.config, self.clock = camera, config, clock
        self.pan = int(clamp(90, config.pan_min, config.pan_max))
        self.tilt = int(clamp(90, config.tilt_min, config.tilt_max))
        self.last_move = float('-inf')

    def sync(self, pan, tilt):
        self.pan = int(clamp(pan, self.config.pan_min, self.config.pan_max))
        self.tilt = int(clamp(tilt, self.config.tilt_min, self.config.tilt_max))

    def _move(self, pan, tilt):
        config = self.config
        pan = int(round(clamp(pan, config.pan_min, config.pan_max)))
        tilt = int(round(clamp(tilt, config.tilt_min, config.tilt_max)))
        now = self.clock()
        if (pan, tilt) == (self.pan, self.tilt) or now - self.last_move < .1 - 1e-9:
            return False
        applied = self.camera.move(pan, tilt)
        self.sync(applied['pan'], applied['tilt'])
        self.last_move = now
        return True

    def track(self, offset):
        if offset is None:
            return False
        dx, dy = offset
        if not all(math.isfinite(value) and -1 <= value <= 1 for value in offset):
            raise ValueError('Offsets must be finite and within [-1, 1]')
        def step(value, invert):
            if abs(value) <= self.config.dead_zone:
                return 0
            delta = clamp(self.config.gain_deg * value, -self.config.max_step_deg, self.config.max_step_deg)
            return -delta if invert else delta
        return self._move(self.pan + step(dx, self.config.invert_pan),
                          self.tilt + step(dy, self.config.invert_tilt))

    def manual(self, direction, small=False):
        if direction not in {'left', 'right', 'up', 'down'}:
            raise ValueError('Unknown movement direction')
        delta = min(1, self.config.max_step_deg) if small else self.config.max_step_deg
        dx = (-delta if direction == 'left' else delta) if direction in {'left', 'right'} else 0
        dy = (-delta if direction == 'up' else delta) if direction in {'up', 'down'} else 0
        return self._move(self.pan + (-dx if self.config.invert_pan else dx),
                          self.tilt + (-dy if self.config.invert_tilt else dy))

    def centre(self):
        return self._move(90, 90)
