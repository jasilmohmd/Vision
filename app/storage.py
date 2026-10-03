"""Sequential JPEG numbering and atomically updated metadata (single writer)."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from threading import RLock

PHOTO_NAME = re.compile(r'IMG_(\d{4,})\.jpg$')


class PhotoStore:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index = self.directory / 'index.json'
        self.lock = RLock()

    def list_photos(self):
        with self.lock:
            if not self.index.exists():
                return []
            data = json.loads(self.index.read_text(encoding='utf-8'))
            if not isinstance(data, list) or any(not isinstance(item, dict) or not isinstance(item.get('filename'), str) or not PHOTO_NAME.fullmatch(item.get('filename', '')) for item in data):
                raise ValueError('Invalid photo index; refusing to overwrite metadata')
            return data

    def save(self, jpeg: bytes, command: str):
        if not jpeg.startswith(b'\xff\xd8') or not jpeg.endswith(b'\xff\xd9'):
            raise ValueError('Expected JPEG data')
        with self.lock:
            metadata = self.list_photos()
            numbers = [int(match.group(1)) for file in self.directory.iterdir()
                       if (match := PHOTO_NAME.fullmatch(file.name))]
            numbers += [int(PHOTO_NAME.fullmatch(item['filename']).group(1)) for item in metadata]
            number = max(numbers, default=0) + 1
            while True:
                filename = f'IMG_{number:04d}.jpg'
                path = self.directory / filename
                try:
                    with path.open('xb') as output:
                        output.write(jpeg)
                    break
                except FileExistsError:
                    number += 1
            entry = dict(filename=filename, timestamp=datetime.now(timezone.utc).isoformat(), command=command)
            temporary = self.index.with_suffix('.json.tmp')
            try:
                temporary.write_text(json.dumps([*metadata, entry], indent=2) + '\n', encoding='utf-8')
                temporary.replace(self.index)
            except Exception:
                path.unlink(missing_ok=True)
                raise
            return entry
