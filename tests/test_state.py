from dataclasses import replace
from threading import Event
from unittest.mock import Mock
import pytest
from app.config import Config
from app.control.controller import Controller
from app.state import Mode, StateMachine
from app.voice.commands import parse
from app.voice.recognizer import VoiceEvent
from app.io.camera_client import CameraOffline

@pytest.fixture
def rig():
    camera, lights, store, speaker = Mock(), Mock(), Mock(), Mock()
    camera.move.side_effect = lambda pan, tilt: dict(pan=pan, tilt=tilt)
    camera.capture.return_value = b'jpeg'
    store.save.return_value = dict(filename='IMG_0001.jpg')
    lights.steady_state = 'ready'
    def send(state):
        if state in ('ready', 'tracking', 'nosubject', 'sleep'):
            lights.steady_state = state
    lights.send.side_effect = send
    now = [0.0]
    config = replace(Config(), centre_timeout_s=.05)
    control = Controller(camera, config, clock=lambda: now[0])
    state = StateMachine(control, camera, lights, store, speaker, config, clock=lambda: now[0], timer_interval=.005, burst_interval=.005)
    yield state, camera, lights, store, speaker, now
    state.close()

def command(state, phrase):
    state.handle(parse('camera ' + phrase), 'camera ' + phrase)

def finish(state):
    state.worker.join(2)
    assert not state.worker.is_alive()

def test_tracking_missing_subject_and_sleep(rig):
    state, camera, lights, store, speaker, now = rig
    command(state, 'track person')
    state.tick((.5, -.5))
    camera.move.assert_called_with(94, 86)
    now[0] = 1
    state.tick(None)
    now[0] = 3.01
    state.tick(None)
    assert lights.steady_state == 'nosubject'
    now[0] = 3.2
    state.tick((0, 0))
    assert lights.steady_state == 'tracking'
    command(state, 'stop tracking')
    assert state.mode == Mode.IDLE
    command(state, 'sleep')
    command(state, 'shoot')
    command(state, 'track cat')
    assert state.mode == Mode.SLEEP
    camera.capture.assert_not_called()
    command(state, 'wake')
    assert state.mode == Mode.IDLE

def test_save_before_ack_and_restore_tracking(rig):
    state, camera, lights, store, speaker, now = rig
    parent = Mock()
    parent.attach_mock(camera, 'camera')
    parent.attach_mock(store, 'store')
    command(state, 'track face')
    state.tick((0, 0))
    command(state, 'shoot')
    finish(state)
    names = [call[0] for call in parent.mock_calls]
    assert names.index('camera.capture') < names.index('store.save') < names.index('camera.ack')
    store.save.assert_called_with(b'jpeg', 'camera shoot')
    assert state.mode == Mode.TRACKING and state.target == 'face'
    assert lights.send.call_args.args == ('saved',)
    speaker.say.assert_called_once_with('Photo 1 saved')

@pytest.mark.parametrize('action,count', [('burst', 3), ('timer', 1)])
def test_burst_and_timer(rig, action, count):
    state, camera, lights, store, speaker, now = rig
    command(state, action)
    finish(state)
    assert camera.capture.call_count == count
    assert camera.ack.call_count == count
    if action == 'timer':
        assert sum(call.args == ('heard',) for call in lights.send.call_args_list) == 3
    assert state.mode == Mode.IDLE

def test_save_failure_does_not_ack(rig):
    state, camera, lights, store, speaker, now = rig
    store.save.side_effect = OSError('full')
    command(state, 'shoot')
    finish(state)
    camera.ack.assert_not_called()
    speaker.say.assert_not_called()
    lights.send.assert_any_call('error')
    assert state.mode == Mode.IDLE

def test_ack_failure_retries_before_next_capture(rig):
    state, camera, lights, store, speaker, now = rig
    camera.ack.side_effect = [CameraOffline('offline'), None, None]
    command(state, 'shoot')
    finish(state)
    assert state.pending_ack
    parent = Mock()
    parent.attach_mock(camera, 'camera')
    command(state, 'shoot')
    finish(state)
    names = [call[0] for call in parent.mock_calls]
    assert names[:2] == ['camera.ack', 'camera.capture']
    assert store.save.call_count == 2 and not state.pending_ack

def test_cancel_timer_and_busy_commands(rig):
    state, camera, lights, store, speaker, now = rig
    state.timer_interval = .2
    command(state, 'timer')
    worker = state.worker
    command(state, 'burst')
    assert state.worker is worker
    command(state, 'sleep')
    finish(state)
    assert state.mode == Mode.SLEEP
    camera.capture.assert_not_called()

def test_tracking_shoot_waits_for_timeout_without_blocking(rig):
    state, camera, lights, store, speaker, now = rig
    command(state, 'track person')
    command(state, 'shoot')
    assert state.worker.is_alive()
    state.tick((1, 0))
    camera.move.assert_called_with(94, 90)
    finish(state)
    camera.capture.assert_called_once()

def test_low_confidence_flashes_error(rig):
    state, camera, lights, store, speaker, now = rig
    state.handle_event(VoiceEvent('low_confidence'))
    lights.send.assert_called_with('error')
    camera.move.assert_not_called()
