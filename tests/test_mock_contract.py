from time import monotonic, sleep
from unittest.mock import Mock
import socket
import cv2
import numpy as np
import pytest
import requests
from app.io.camera_client import CameraClient, CameraOffline
from app.io.light_client import LightClient
from app.io.speaker import Speaker
from app.gallery.server import GalleryServer, create_gallery
from app.storage import PhotoStore
from app.vision.stream import MjpegStream
from tools.mock_camera import MockCamera
from tools.mock_voice_unit import LightMonitor

@pytest.fixture
def mock_camera():
    camera = MockCamera(synthetic=True)
    camera.start(control_port=0, stream_port=0)
    yield camera
    camera.close()

def test_full_http_contract_and_held_jpeg(mock_camera):
    port = mock_camera.servers[0].server_port
    client = CameraClient('127.0.0.1', port)
    try:
        assert client.status()['held_photo'] is False
        assert client.move(200, -1) == dict(pan=170, tilt=40)
        assert mock_camera.crop().shape == (240, 320, 3)
        first = client.capture()
        assert client.status()['held_photo'] is True
        image = cv2.imdecode(np.frombuffer(first, np.uint8), cv2.IMREAD_COLOR)
        assert image.shape == (720, 1280, 3)
        mock_camera.frame[:] = 255
        assert client.capture() == first
        client.ack()
        assert client.status()['held_photo'] is False
        assert client.capture() != first
        response = requests.get(f'http://127.0.0.1:{port}/move', params={'pan': 'oops', 'tilt': 90}, timeout=2)
        assert response.status_code == 400
    finally:
        client.close()

def test_crop_moves_and_mjpeg_decode(mock_camera):
    mock_camera.pan, mock_camera.tilt = 90, 90
    centre = mock_camera.crop()
    mock_camera.pan = 10
    assert not np.array_equal(centre, mock_camera.crop())
    stream = MjpegStream(f'http://127.0.0.1:{mock_camera.servers[1].server_port}/stream')
    stream.start()
    try:
        deadline = monotonic() + 3
        while stream.latest()[0] == 0 and monotonic() < deadline:
            sleep(.02)
        number, frame, timestamp = stream.latest()
        assert number > 0 and frame.shape == (240, 320, 3)
    finally:
        stream.close()
    assert not stream.thread.is_alive()

def test_camera_retries_and_timeout():
    session = Mock()
    session.get.side_effect = requests.Timeout('timeout')
    client = CameraClient('localhost', session=session)
    with pytest.raises(CameraOffline):
        client.capture()
    assert session.get.call_count == 3
    assert session.get.call_args.kwargs['timeout'] == 2

def test_malformed_jpeg_retried():
    from unittest.mock import MagicMock
    session = MagicMock()
    response = session.get.return_value.__enter__.return_value
    response.headers = {'Content-Type': 'image/jpeg'}
    response.content = b'bad'
    with pytest.raises(CameraOffline):
        CameraClient('localhost', session=session).capture()
    assert session.get.call_count == 3

def test_udp_light_contract_remembers_steady():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 0))
    sock.settimeout(1)
    light = LightClient('127.0.0.1', sock.getsockname()[1])
    try:
        light.send('tracking')
        light.send('saved')
        assert [sock.recvfrom(64)[0], sock.recvfrom(64)[0]] == [b'tracking', b'saved']
        assert light.steady_state == 'tracking'
        with pytest.raises(ValueError):
            light.send('invalid')
    finally:
        light.close()
        sock.close()

def test_mock_flash_restores_steady(capsys):
    monitor = LightMonitor(port=0)
    light = LightClient('127.0.0.1', monitor.socket.getsockname()[1])
    monitor.start()
    try:
        light.send('tracking')
        light.send('saved')
        sleep(.4)
    finally:
        monitor.close()
        light.close()
    output = capsys.readouterr().out
    assert 'saved (white flash)' in output and 'tracking (cyan) restored' in output

def test_gallery_newest_first_and_photo_link(tmp_path):
    camera = MockCamera(synthetic=True)
    store = PhotoStore(tmp_path)
    jpeg = camera.jpeg(camera.frame)
    store.save(jpeg, 'camera shoot')
    store.save(jpeg, 'camera burst')
    client = create_gallery(store).test_client()
    html = client.get('/').get_data(as_text=True)
    assert html.index('IMG_0002.jpg') < html.index('IMG_0001.jpg')
    assert client.get('/api/photos').json[0]['filename'] == 'IMG_0002.jpg'
    response = client.get('/photos/IMG_0001.jpg')
    assert response.data == jpeg and response.content_type == 'image/jpeg'
    assert client.get('/photos/index.json').status_code == 404
    assert client.get('/photos/IMG_9999.jpg').status_code == 404
    camera.close()

def test_optional_speaker_noop(monkeypatch):
    monkeypatch.setattr('app.io.speaker.shutil.which', lambda _: None)
    for enabled in (True, False):
        speaker = Speaker(enabled)
        speaker.say('Photo 1 saved')
        speaker.close()


def test_recognized_command_to_http_capture_gallery_and_udp_saved(mock_camera, tmp_path):
    from app.config import Config
    from app.control.controller import Controller
    from app.state import StateMachine, Mode
    from app.voice.commands import parse
    from app.voice.recognizer import VoiceEvent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 0))
    sock.settimeout(1)
    lights = LightClient('127.0.0.1', sock.getsockname()[1])
    camera = CameraClient('127.0.0.1', mock_camera.servers[0].server_port)
    speaker = Speaker(False)
    store = PhotoStore(tmp_path)
    gallery = GalleryServer(store, host='127.0.0.1', port=0)
    gallery.start()
    state = StateMachine(Controller(camera, Config()), camera, lights, store, speaker, Config())
    try:
        before = mock_camera.crop()
        state.handle_event(VoiceEvent('command', parse('camera track person'), 'camera track person'))
        state.tick((.5, 0))
        assert mock_camera.pan == 94
        assert not np.array_equal(before, mock_camera.crop())
        state.tick((0, 0))
        state.handle_event(VoiceEvent('command', parse('camera shoot'), 'camera shoot'))
        state.worker.join(2)
        assert not state.worker.is_alive() and state.mode == Mode.TRACKING
        assert camera.status()['held_photo'] is False
        url = f'http://127.0.0.1:{gallery.port}'
        photos = requests.get(url + '/api/photos', timeout=2).json()
        assert len(photos) == 1 and photos[0]['command'] == 'camera shoot'
        image = requests.get(url + '/photos/IMG_0001.jpg', timeout=2)
        assert image.status_code == 200
        assert cv2.imdecode(np.frombuffer(image.content, np.uint8), cv2.IMREAD_COLOR).shape == (720, 1280, 3)
        assert [sock.recvfrom(64)[0] for _ in range(3)] == [b'ready', b'tracking', b'saved']
    finally:
        state.close()
        gallery.close()
        camera.close()
        lights.close()
        speaker.close()
        sock.close()
