import json
import logging
import socket
import sys
from unittest.mock import Mock

from app.io.camera_client import CameraOffline
from app.io.light_client import LightClient
from app.runtime import AudioWatchdog, CameraRecovery, JsonFormatter, configure_logging
from app.voice.audio_source import CHUNK_BYTES, UdpAudioSource


def test_audio_watchdog_warns_once_then_reports_recovery(caplog):
    now = [0.0]
    watchdog = AudioWatchdog(clock=lambda: now[0])
    with caplog.at_level(logging.INFO):
        now[0] = 5
        watchdog.poll(None)
        assert not caplog.records
        now[0] = 5.1
        watchdog.poll(None)
        now[0] = 10
        watchdog.poll(None)
        assert len(caplog.records) == 1
        watchdog.poll(10)
        assert 'resumed' in caplog.records[-1].message
        now[0] = 16
        watchdog.poll(10)
        assert len(caplog.records) == 3


def test_valid_silent_packets_update_health_but_bad_packets_do_not():
    with UdpAudioSource(host='127.0.0.1', port=0) as source, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        assert source.last_received_at is None
        sender.sendto(bytes(CHUNK_BYTES), source.address)
        with source.condition:
            assert source.condition.wait_for(lambda: source.received_packets == 1, timeout=2)
        received = source.last_received_at
        sender.sendto(b'bad packet', source.address)
        with source.condition:
            assert source.condition.wait_for(lambda: source.invalid_packets == 1, timeout=2)
        assert source.last_received_at == received


def test_camera_recovery_backoff_and_position_resync():
    now = [0.0]
    camera, controller, lights, speaker = Mock(), Mock(), Mock(), Mock()
    camera.status.side_effect = [CameraOffline('offline'), CameraOffline('offline'), {'pan': 70, 'tilt': 85}, {'pan': 90, 'tilt': 90}]
    recovery = CameraRecovery(camera, controller, lights, speaker, clock=lambda: now[0])
    assert not recovery.poll(False)
    camera.status.assert_not_called()
    assert not recovery.poll(True)
    now[0] = .1
    assert not recovery.poll(True)
    assert camera.status.call_count == 1
    now[0] = .2
    assert not recovery.poll(True)
    now[0] = .59
    assert not recovery.poll(True)
    assert camera.status.call_count == 2
    now[0] = .61
    assert recovery.poll(True)
    controller.sync.assert_called_with(70, 85)
    lights.set_reconnecting.assert_called_with(False)
    assert not recovery.poll(False)
    assert recovery.poll(True)
    controller.sync.assert_called_with(90, 90)
    assert speaker.say.call_count == 2


def test_reconnect_mask_preserves_tracking_sleep_and_wake():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(('127.0.0.1', 0))
        receiver.settimeout(1)
        lights = LightClient(*receiver.getsockname())
        try:
            lights.send('tracking')
            assert receiver.recv(64) == b'tracking'
            lights.set_reconnecting(True)
            assert receiver.recv(64) == b'reconnect'
            lights.send('nosubject')
            assert receiver.recv(64) == b'reconnect'
            lights.send('saved')
            assert receiver.recv(64) == b'reconnect'
            lights.set_reconnecting(False)
            assert receiver.recv(64) == b'nosubject'
            lights.set_reconnecting(True)
            assert receiver.recv(64) == b'reconnect'
            lights.send('sleep')
            assert receiver.recv(64) == b'sleep'
            lights.send('ready')
            assert receiver.recv(64) == b'reconnect'
            lights.set_reconnecting(False)
            assert receiver.recv(64) == b'ready'
        finally:
            lights.close()


def test_json_logs_rotate_and_preserve_exception(tmp_path):
    handler = configure_logging(tmp_path)
    try:
        record = logging.LogRecord('vision', logging.ERROR, __file__, 1, 'failure %s', ('example',), None)
        data = json.loads(JsonFormatter().format(record))
        assert data['level'] == 'ERROR' and data['message'] == 'failure example'
        assert data['timestamp'].endswith('+00:00')
        try:
            raise ValueError('diagnostic traceback')
        except ValueError:
            record.exc_info = sys.exc_info()
        assert 'ValueError: diagnostic traceback' in json.loads(JsonFormatter().format(record))['exception']
        handler.handle(record)
        handler.doRollover()
        handler.handle(record)
        assert handler.backupCount == 7 and handler.interval == 86400 and handler.utc
        assert len(list(tmp_path.glob('vision.jsonl*'))) == 2
        assert json.loads((tmp_path / 'vision.jsonl').read_text())['message'] == 'failure example'
    finally:
        logging.getLogger().removeHandler(handler)
        handler.close()
