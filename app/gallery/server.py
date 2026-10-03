"""Phone-friendly Flask gallery and stoppable local server."""
from threading import Thread
from flask import Flask, abort, jsonify, render_template, send_from_directory
from werkzeug.serving import make_server
from app.storage import PHOTO_NAME


def create_gallery(store):
    app = Flask(__name__)

    @app.get('/')
    def index():
        photos = sorted(store.list_photos(), key=lambda item: int(PHOTO_NAME.fullmatch(item['filename']).group(1)), reverse=True)
        return render_template('index.html', photos=photos)

    @app.get('/api/photos')
    def list_photos():
        return jsonify(list(reversed(store.list_photos())))

    @app.get('/photos/<filename>')
    def photo(filename):
        if not PHOTO_NAME.fullmatch(filename):
            abort(404)
        return send_from_directory(store.directory, filename, mimetype='image/jpeg')

    return app


class GalleryServer:
    def __init__(self, store, host='0.0.0.0', port=8080):
        self.server = make_server(host, port, create_gallery(store), threaded=True)
        self.port = self.server.server_port
        self.thread = Thread(target=self.server.serve_forever, name='gallery', daemon=True)

    def start(self):
        self.thread.start()

    def close(self):
        if self.thread.is_alive():
            self.server.shutdown()
            self.thread.join(timeout=2)
        self.server.server_close()
