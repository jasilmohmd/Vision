"""Fixed-grammar Vosk recognizer with wake-word and per-word confidence gates."""
from dataclasses import dataclass
import json
import math
import logging
from pathlib import Path
from queue import Queue
from time import monotonic

from app.voice.audio_source import SAMPLE_RATE
from app.voice.commands import Command, GRAMMAR, parse
from app.voice.endpoint import SpeechEndpoint, pcm_rms


@dataclass(frozen=True)
class VoiceEvent:
    kind: str
    command: Command | None = None
    text: str = ''
    confidence: float | None = None


class VoiceRecognizer:
    def __init__(self, model_path='models/vosk-model-small-en-us-0.15',
                 confidence_threshold=0.7, events=None, *, engine=None):
        if not 0 <= confidence_threshold <= 1:
            raise ValueError('Confidence threshold must be between 0 and 1')
        self.threshold = confidence_threshold
        self.events = events if events is not None else Queue()
        self.heard = False
        self.endpoint = SpeechEndpoint()
        if engine is None:
            if not (Path(model_path) / 'am' / 'final.mdl').is_file():
                raise FileNotFoundError(f'Missing Vosk model {model_path}; run python -m tools.download_models')
            from vosk import Model, KaldiRecognizer
            self.model = Model(str(model_path))
            engine = KaldiRecognizer(self.model, SAMPLE_RATE, json.dumps(GRAMMAR))
        self.engine = engine
        self.engine.SetWords(True)

    def calibrate(self, source, seconds=2):
        """Consume a short startup background sample before announcing ready."""
        logging.info('Calibrating microphone: keep quiet for %g seconds.', seconds)
        levels, samples = [], 0
        deadline = monotonic() + seconds + 1
        while samples < SAMPLE_RATE * seconds and monotonic() < deadline:
            pcm = source.read_chunk()
            if pcm:
                if len(pcm) % 2:
                    raise ValueError('s16le PCM must contain complete 16-bit samples')
                levels.append(pcm_rms(pcm))
                samples += len(pcm) // 2
        self.endpoint.calibrate(levels)
        self.discard_pending()
        logging.info('Voice background RMS %.1f; phrase silence %.1fs.',
                     self.endpoint.noise_rms, self.endpoint.quiet_seconds)

    def process_chunk(self, pcm: bytes):
        if not pcm:
            return
        if len(pcm) % 2:
            raise ValueError('s16le PCM must contain complete 16-bit samples')
        audio, ended = self.endpoint.feed(pcm)
        if not audio:
            return
        if self.engine.AcceptWaveform(audio):
            self._final(json.loads(self.engine.Result()))
            self.discard_pending()
        else:
            text = json.loads(self.engine.PartialResult()).get('partial', '')
            if 'camera' in text.split() and not self.heard:
                self.events.put(VoiceEvent('heard'))
                self.heard = True
            if ended:
                self.flush()

    def _final(self, result):
        self.heard = False
        text = ' '.join(result.get('text', '').split())
        if not text or text == '[unk]':
            return
        command = parse(text)
        words = result.get('result', [])
        confidences = [word.get('conf') for word in words]
        complete = bool(words) and [word.get('word') for word in words] == text.split()
        valid = complete and all(type(conf) in (int, float) and math.isfinite(conf)
                                 and self.threshold <= conf <= 1 for conf in confidences)
        if command is not None and valid:
            self.events.put(VoiceEvent('command', command, text, min(confidences)))
        else:
            self.events.put(VoiceEvent('low_confidence', text=text))

    def flush(self):
        """Explicitly finish a phrase; ordinary shutdown discards pending audio."""
        self._final(json.loads(self.engine.FinalResult()))
        self.discard_pending()

    def discard_pending(self):
        self.engine.Reset()
        self.endpoint.reset()
        self.heard = False

    def run(self, source, stop_event):
        """Blocking worker for a future app thread; source ownership stays with caller."""
        try:
            while not stop_event.is_set():
                chunk = source.read_chunk()
                if stop_event.is_set():
                    break
                if chunk:
                    self.process_chunk(chunk)
        finally:
            self.discard_pending()
