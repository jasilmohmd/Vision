import socket
from deploy.check_mock_network import check
from tools.mock_camera import MockCamera


def test_diagnostic_stream_only_does_not_capture_or_move():
    camera=MockCamera(synthetic=True)
    camera.start(control_port=0,stream_port=0)
    try:
        report=check('127.0.0.1',camera.servers[0].server_port,camera.servers[1].server_port,seconds=.2)
        assert report['ok'] and report['frames']>0 and report['bytes']>0
        assert not report['errors']
        assert camera.held is None and (camera.pan,camera.tilt)==(90,90)
    finally:
        camera.close()


def test_network_failure_is_reported():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
        report=check('127.0.0.1',port,port,seconds=.1,timeout=.1)
    assert not report['ok'] and report['frames']==0 and report['errors']
