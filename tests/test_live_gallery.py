from unittest.mock import Mock
from app.gallery.server import create_gallery


def test_live_view_is_optional():
    client = create_gallery(Mock()).test_client()
    assert client.get('/live').status_code == 404
    assert client.get('/live/frame.jpg').status_code == 404


def test_live_frame_is_read_only_and_not_cached():
    store = Mock()
    provider = Mock(return_value=b'jpeg-frame')
    client = create_gallery(store, provider).test_client()
    assert b'camera stop tracking' in client.get('/live').data
    response = client.get('/live/frame.jpg')
    assert response.status_code == 200
    assert response.mimetype == 'image/jpeg'
    assert response.data == b'jpeg-frame'
    assert response.headers['Cache-Control'] == 'no-store'
    store.save.assert_not_called()


def test_live_camera_startup_retries_without_serving_fake_frame():
    client = create_gallery(Mock(), lambda: None).test_client()
    response = client.get('/live/frame.jpg')
    assert response.status_code == 503
    assert response.headers['Retry-After'] == '1'
