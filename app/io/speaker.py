"""Optional eSpeak output; disabled/unavailable output is a no-op."""
import logging
from queue import Queue, Empty, Full
import shutil
import subprocess
from threading import Event, Thread


class Speaker:
    def __init__(self, enabled=False):
        self.executable = shutil.which('espeak-ng') or shutil.which('espeak') if enabled else None
        self.stopped = Event()
        self.messages = Queue(maxsize=8)
        self.thread = None
        if self.executable:
            self.thread = Thread(target=self._run, name='speaker', daemon=True)
            self.thread.start()

    def say(self, text):
        if self.executable and not self.stopped.is_set():
            try:
                self.messages.put_nowait(text)
            except Full:
                logging.warning('Speaker queue full; reply skipped')

    def _run(self):
        while not self.stopped.is_set():
            try:
                text = self.messages.get(timeout=.1)
            except Empty:
                continue
            try:
                result = subprocess.run([self.executable, text], timeout=10, capture_output=True)
                if result.returncode:
                    logging.warning('Speaker unavailable; disabling TTS')
                    self.executable = None
                    return
            except (OSError, subprocess.TimeoutExpired):
                self.executable = None
                return

    def close(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=1)
