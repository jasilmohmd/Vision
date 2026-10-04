"""Bounded speech/silence segmentation of mono s16le input, without recordings."""
from array import array
import math
import sys

from app.voice.audio_source import SAMPLE_RATE


def pcm_rms(pcm):
    samples = array('h')
    samples.frombytes(pcm)
    if sys.byteorder != 'little':
        samples.byteswap()
    return math.sqrt(sum(value * value for value in samples) / len(samples)) if samples else 0.


class SpeechEndpoint:
    pre_roll_bytes = int(.192 * SAMPLE_RATE) * 2
    quiet_seconds = .7
    max_seconds = 8.

    def __init__(self):
        self.noise_rms = 100.
        self.reset()

    def calibrate(self, levels):
        if levels:
            ordered = sorted(levels)
            # Use a quiet percentile, not a speech-contaminated mean. Bound the
            # result so startup noise can never set an unreachable speech gate.
            self.noise_rms = max(20., min(500., ordered[int(.2 * (len(ordered) - 1))]))
        self.reset()

    def reset(self):
        self.active = False
        self.pre_roll = bytearray()
        self.silence = self.duration = 0.

    def feed(self, pcm):
        level = pcm_rms(pcm)
        seconds = len(pcm) / (2 * SAMPLE_RATE)
        if not self.active:
            self.pre_roll.extend(pcm)
            del self.pre_roll[:-self.pre_roll_bytes]
            if level < self.noise_rms * 5:
                return b'', False
            self.active = True
            audio = bytes(self.pre_roll)
            self.pre_roll.clear()
            self.duration = len(audio) / (2 * SAMPLE_RATE)
        else:
            audio = pcm
            self.duration += seconds
        self.silence = self.silence + seconds if level < self.noise_rms * 3 else 0.
        return audio, self.silence >= self.quiet_seconds or self.duration >= self.max_seconds
