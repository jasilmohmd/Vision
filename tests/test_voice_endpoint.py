from array import array
import json
from threading import Event

import pytest

from app.voice.audio_source import SILENCE
from app.voice.endpoint import SpeechEndpoint, pcm_rms
from app.voice.recognizer import VoiceRecognizer
from tests.test_voice import FakeEngine, events, result


def pcm(level):
    return array('h', [level] * 512).tobytes()


class WaitingEngine:
    """Models the observed recognizer that never ends a phrase by itself."""
    def __init__(self, phrases):
        self.phrases = iter(phrases)
        self.audio = []
        self.ends = self.resets = 0

    def SetWords(self, value):
        pass

    def AcceptWaveform(self, data):
        self.audio.append(data)
        return False

    def PartialResult(self):
        return json.dumps({'partial': 'camera'})

    def FinalResult(self):
        self.ends += 1
        return json.dumps(next(self.phrases))

    def Reset(self):
        self.resets += 1


def quiet(rec, chunks=22):
    for _ in range(chunks):
        rec.process_chunk(SILENCE)


def test_silence_finalises_without_waiting_for_shutdown_and_no_duplicate():
    engine = WaitingEngine([result('camera up')])
    rec = VoiceRecognizer(engine=engine)
    rec.process_chunk(pcm(5000))
    quiet(rec, 21)
    assert [e.kind for e in events(rec)] == ['heard']
    quiet(rec, 1)
    assert [e.text for e in events(rec)] == ['camera up']
    quiet(rec, 100)
    assert events(rec) == []
    assert engine.ends == engine.resets == 1


def test_consecutive_phrases_and_short_pause_between_words():
    engine = WaitingEngine([result('camera up'), result('camera centre')])
    rec = VoiceRecognizer(engine=engine)
    rec.process_chunk(pcm(5000))
    quiet(rec, 10)  # A word gap must not split a command.
    rec.process_chunk(pcm(5000))
    assert engine.ends == 0
    quiet(rec)
    rec.process_chunk(pcm(5000))
    quiet(rec)
    assert [e.text for e in events(rec) if e.kind == 'command'] == ['camera up', 'camera centre']


def test_preroll_retains_quiet_word_onset_and_is_bounded():
    engine = WaitingEngine([])
    rec = VoiceRecognizer(engine=engine)
    for _ in range(100):
        rec.process_chunk(pcm(50))
    assert engine.audio == []
    rec.process_chunk(pcm(5000))
    assert engine.audio == [pcm(50) * 5 + pcm(5000)]
    assert len(engine.audio[0]) == SpeechEndpoint.pre_roll_bytes


@pytest.mark.parametrize('levels, expected', [
    ([20] * 50 + [32768] * 14, 20),
    ([32768] * 64, 500),
    ([0] * 64, 20),
    ([], 100),
])
def test_calibration_resists_spikes_and_cannot_make_gate_unreachable(levels, expected):
    endpoint = SpeechEndpoint()
    endpoint.calibrate(levels)
    assert endpoint.noise_rms == expected
    audio, _ = endpoint.feed(pcm(3000))
    assert audio


def test_quiet_speech_after_quiet_calibration_is_not_discarded():
    rec = VoiceRecognizer(engine=WaitingEngine([result('camera up')]))
    rec.endpoint.calibrate([20] * 64)
    rec.process_chunk(pcm(150))
    quiet(rec)
    assert [e.text for e in events(rec) if e.kind == 'command'] == ['camera up']


@pytest.mark.parametrize('payload', [
    result('camera up', .69), result('up'), result('camera camera up'),
    result('[unk] camera up'), {'text': 'camera up'},
])
def test_forced_endpoint_keeps_wake_word_and_confidence_gates(payload):
    rec = VoiceRecognizer(engine=WaitingEngine([payload]))
    rec.process_chunk(pcm(5000))
    quiet(rec)
    assert not [e for e in events(rec) if e.kind == 'command']


def test_clipped_continuous_audio_has_bounded_phrase_duration():
    engine = WaitingEngine([{'text': '[unk]'}])
    rec = VoiceRecognizer(engine=engine)
    for _ in range(250):
        rec.process_chunk(pcm(-32768))
    assert pcm_rms(pcm(-32768)) == 32768
    assert engine.ends == 1
    assert not rec.endpoint.active
    assert not [e for e in events(rec) if e.kind == 'command']


def test_natural_result_does_not_reappear_at_silence_endpoint():
    engine = FakeEngine([result('camera up')], final=result('camera up'))
    rec = VoiceRecognizer(engine=engine)
    rec.process_chunk(pcm(5000))
    quiet(rec)
    assert [e.text for e in events(rec)] == ['camera up']


def test_shutdown_discards_unfinished_phrase_instead_of_emitting_command():
    stop = Event()
    engine = WaitingEngine([result('camera shoot')])
    rec = VoiceRecognizer(engine=engine)

    class Source:
        reads = 0
        def read_chunk(self):
            self.reads += 1
            if self.reads == 2:
                stop.set()
            return pcm(5000)

    rec.run(Source(), stop)
    assert engine.ends == 0
    assert engine.resets == 1
    assert not [e for e in events(rec) if e.kind == 'command']


def test_background_sample_is_not_sent_to_engine():
    engine = WaitingEngine([])
    rec = VoiceRecognizer(engine=engine)

    class Source:
        def read_chunk(self):
            return pcm(80)

    rec.calibrate(Source(), seconds=.1)
    assert rec.endpoint.noise_rms == 80
    assert engine.audio == []
    assert events(rec) == []
