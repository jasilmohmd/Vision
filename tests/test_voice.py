from array import array
from collections import deque
import json
from queue import Empty
import socket
from threading import Event
from time import monotonic

import pytest

from app.voice.audio_source import SILENCE, LaptopMicSource, UdpAudioSource
from app.voice.commands import COMMAND_PHRASES, GRAMMAR, Command, parse
from app.voice.recognizer import VoiceRecognizer

SPEECH = array('h', [5000] * 512).tobytes()


@pytest.mark.parametrize('phrase', COMMAND_PHRASES)
def test_every_contract_phrase_parses(phrase):
    assert parse(phrase) is not None
    assert parse('  ' + phrase.upper().replace(' ', '  ') + ' ') == parse(phrase)


def test_grammar_and_command_semantics():
    assert len(COMMAND_PHRASES) == 19
    assert GRAMMAR == [*COMMAND_PHRASES, '[unk]']
    assert parse('camera track face') == Command('track', target='face')
    assert parse('camera a bit up') == Command('move', direction='up', small=True)
    assert parse('camera stop tracking') == Command('stop_tracking')
    assert parse('camera centre') == Command('centre')


@pytest.mark.parametrize('text', ['', '[unk]', 'shoot', 'please camera shoot',
                                  'cameras shoot', 'camera shoot now',
                                  'camera shoot camera sleep', 'camera center'])
def test_rejects_missing_wake_word_or_extra_words(text):
    assert parse(text) is None


class FakeEngine:
    def __init__(self, results=(), partials=(), final=None):
        self.results = deque(results)
        self.partials = deque(partials)
        self.current = None
        self.final = final or {'text': ''}
        self.words_enabled = False

    def SetWords(self, value):
        self.words_enabled = value

    def AcceptWaveform(self, data):
        if self.partials:
            self.current = self.partials.popleft()
            return False
        self.current = self.results.popleft()
        return True

    def PartialResult(self):
        return json.dumps({'partial': self.current})

    def Result(self):
        return json.dumps(self.current)

    def FinalResult(self):
        return json.dumps(self.final)

    def Reset(self):
        self.current = None
        self.final = {'text': ''}


def result(text, conf=1):
    return {'text': text, 'result': [{'word': word, 'conf': conf} for word in text.split()]}


def events(rec):
    output = []
    while True:
        try:
            output.append(rec.events.get_nowait())
        except Empty:
            return output


def test_heard_once_per_utterance_then_confident_command():
    engine = FakeEngine([result('camera shoot'), result('camera wake')],
                        ['a cameraman', 'camera', 'camera shoot'])
    rec = VoiceRecognizer(engine=engine)
    assert engine.words_enabled is True
    for _ in range(4):
        rec.process_chunk(SPEECH)
    received = events(rec)
    assert [event.kind for event in received] == ['heard', 'command']
    assert received[-1].command == Command('shoot')
    assert received[-1].confidence == 1
    engine.partials.append('camera')
    rec.process_chunk(SPEECH)
    rec.process_chunk(SPEECH)
    assert [event.kind for event in events(rec)] == ['heard', 'command']


@pytest.mark.parametrize('payload', [
    result('camera shoot', .69), result('camera shoot', float('nan')),
    result('camera shoot', 1.1), result('shoot'), result('hello there'),
    result('camera unsupported'), {'text': 'camera shoot'},
    {'text': 'camera shoot', 'result': [{'word': 'camera', 'conf': 1}]},
    {'text': 'camera shoot', 'result': [{'word': 'camera', 'conf': True}, {'word': 'shoot', 'conf': 1}]},
    {'text': 'camera shoot', 'result': [{'word': 'camera', 'conf': 1}, {'word': 'shoot', 'conf': .1}]},
])
def test_low_confidence_and_incomplete_word_evidence(payload):
    rec = VoiceRecognizer(engine=FakeEngine([payload]))
    rec.process_chunk(SPEECH)
    assert [event.kind for event in events(rec)] == ['low_confidence']


def test_threshold_inclusive_and_ignored_empty_unknown():
    rec = VoiceRecognizer(engine=FakeEngine([result('camera shoot', .7),
                                             {'text': ''}, {'text': '[unk]'}]))
    for _ in range(3):
        rec.process_chunk(SPEECH)
    output = events(rec)
    assert len(output) == 1 and output[0].kind == 'command'


def test_flush_filters_the_last_result():
    rec = VoiceRecognizer(engine=FakeEngine(final=result('camera sleep')))
    rec.flush()
    assert events(rec)[0].command == Command('sleep')
    with pytest.raises(ValueError):
        rec.process_chunk(b'x')
    with pytest.raises(ValueError):
        VoiceRecognizer(confidence_threshold=float('nan'), engine=FakeEngine())


def test_worker_does_not_dispatch_audio_received_after_stop():
    stop = Event()
    class Source:
        def read_chunk(self):
            stop.set()
            return SILENCE
    rec = VoiceRecognizer(engine=FakeEngine([result('camera shoot')]))
    rec.run(Source(), stop)
    assert events(rec) == []


def wait_packets(source, count):
    deadline = monotonic() + 2
    with source.condition:
        while source.received_packets < count and monotonic() < deadline:
            source.condition.wait(deadline - monotonic())
    assert source.received_packets >= count


def test_udp_packet_validation_loss_fill_and_recovery():
    with UdpAudioSource(host='127.0.0.1', port=0, jitter_packets=1) as source:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(b'bad', source.address)
            first = b'\x01\x00' * 512
            sender.sendto(first, source.address)
            wait_packets(source, 1)
            assert source.read_chunk() == first
            assert source.invalid_packets == 1
            assert source.read_chunk() == SILENCE
            assert source.silence_chunks == 1
            second = b'\x02\x00' * 512
            sender.sendto(second, source.address)
            wait_packets(source, 2)
            assert source.read_chunk() == second
    assert source.read_chunk() == b''
    assert not source.thread.is_alive()
    source.close()


def test_udp_buffer_bounds_and_arrival_order():
    with UdpAudioSource(host='127.0.0.1', port=0, jitter_packets=2, max_packets=3) as source:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for index in range(5):
                sender.sendto(bytes([index, 0]) * 512, source.address)
            wait_packets(source, 5)
        assert len(source.packets) == 3 and source.dropped_packets == 2
        assert source.read_chunk() == bytes([2, 0]) * 512
        assert source.read_chunk() == bytes([3, 0]) * 512
        assert source.read_chunk() == bytes([4, 0]) * 512


def test_udp_initial_timeout_and_shutdown_wakeup():
    from concurrent.futures import ThreadPoolExecutor
    source = UdpAudioSource(host='127.0.0.1', port=0)
    assert source.read_chunk() == b''
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(source.read_chunk)
        source.close()
        assert future.result(timeout=1) == b''


def test_laptop_mic_format_overflow_and_cleanup(monkeypatch):
    import sounddevice as sd
    class Stream:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.started = self.closed = False
        def start(self):
            self.started = True
        def read(self, count):
            assert count == 512
            return bytearray(SILENCE), True
        def stop(self):
            self.started = False
        def close(self):
            self.closed = True
    monkeypatch.setattr(sd, 'RawInputStream', Stream)
    with LaptopMicSource(device=3) as source:
        assert source.stream.options == dict(samplerate=16000, channels=1,
                                           dtype='int16', blocksize=512, device=3)
        assert source.read_chunk() == SILENCE
        assert source.overflow_count == 1
    source.close()
    assert source.stream.closed and source.read_chunk() == b''


def test_missing_vosk_model_has_setup_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match='download_models'):
        VoiceRecognizer(tmp_path / 'missing')
