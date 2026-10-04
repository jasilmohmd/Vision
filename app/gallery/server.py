"""Phone-friendly Flask gallery and stoppable local server."""
from threading import Thread
from flask import Flask, Response, abort, jsonify, render_template, send_from_directory
from werkzeug.serving import make_server
from app.storage import PHOTO_NAME


def create_gallery(store, live_frame=None):
    app = Flask(__name__)

    @app.get('/')
    def index():
        photos = sorted(store.list_photos(), key=lambda item: int(PHOTO_NAME.fullmatch(item['filename']).group(1)), reverse=True)
        return render_template('index.html', photos=photos, live_available=live_frame is not None)

    @app.get('/api/photos')
    def list_photos():
        return jsonify(list(reversed(store.list_photos())))

    @app.get('/photos/<filename>')
    def photo(filename):
        if not PHOTO_NAME.fullmatch(filename):
            abort(404)
        return send_from_directory(store.directory, filename, mimetype='image/jpeg')

    @app.get('/live')
    def live():
        if live_frame is None:
            abort(404)
        return render_template('live.html')

    @app.get('/live/frame.jpg')
    def live_image():
        if live_frame is None:
            abort(404)
        jpeg = live_frame()
        if jpeg is None:
            return Response('Waiting for camera', status=503,
                            headers={'Cache-Control': 'no-store', 'Retry-After': '1'})
        return Response(jpeg, mimetype='image/jpeg',
                        headers={'Cache-Control': 'no-store'})

    return app


class GalleryServer:
    def __init__(self, store, host='0.0.0.0', port=8080, live_frame=None):
        self.server = make_server(host, port, create_gallery(store, live_frame), threaded=True)
        self.port = self.server.server_port
        self.thread = Thread(target=self.server.serve_forever, name='gallery', daemon=True)

    def start(self):
        self.thread.start()

    def close(self):
        if self.thread.is_alive():
            self.server.shutdown()
            self.thread.join(timeout=2)
        self.server.server_close()
