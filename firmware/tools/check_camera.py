"""Exercise the real S3 camera contract; requires requests, no app imports."""
import argparse
import ipaddress
from pathlib import Path
import sys
import time
from threading import Condition, Event, Thread

import requests


def jpeg_dimensions(data):
    if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        raise ValueError("incomplete JPEG")
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset < len(data):
        if data[offset] != 0xFF:
            raise ValueError("invalid JPEG marker")
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            continue
        if marker in (0xDA, 0xD9) or offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset:offset + 2], "big")
        if length < 2 or offset + length > len(data):
            raise ValueError("truncated JPEG segment")
        if marker in sof:
            if length < 8:
                raise ValueError("invalid JPEG dimensions")
            height = int.from_bytes(data[offset + 3:offset + 5], "big")
            width = int.from_bytes(data[offset + 5:offset + 7], "big")
            if not width or not height:
                raise ValueError("empty JPEG dimensions")
            return width, height
        offset += length
    raise ValueError("JPEG has no supported frame header")


def frames(response):
    buffer = bytearray()
    for chunk in response.iter_content(chunk_size=1024):
        buffer.extend(chunk)
        while True:
            start = buffer.find(b"\xff\xd8")
            if start < 0:
                buffer[:] = buffer[-1:]
                break
            end = buffer.find(b"\xff\xd9", start + 2)
            if end < 0:
                del buffer[:start]
                break
            jpeg = bytes(buffer[start:end + 2])
            del buffer[:end + 2]
            yield jpeg
        if len(buffer) > 2_000_000:
            raise ValueError("stream frame exceeds 2 MB")
    raise ValueError("MJPEG stream ended")


def require(condition, message):
    if not condition:
        raise ValueError(message)


class LiveFrames:
    """Consume video continuously during control requests, like the real app."""
    def __init__(self, response):
        self.response = response
        self.condition = Condition()
        self.stop = Event()
        self.frame = None
        self.number = self.consumed = 0
        self.error = None
        self.thread = Thread(target=self.read, daemon=True)
        self.thread.start()

    def read(self):
        try:
            for frame in frames(self.response):
                if self.stop.is_set():
                    return
                with self.condition:
                    self.frame = frame
                    self.number += 1
                    self.condition.notify_all()
        except Exception as error:
            if not self.stop.is_set():
                with self.condition:
                    self.error = error
                    self.condition.notify_all()

    def next_frame(self, fresh=False):
        deadline = time.monotonic() + 20
        with self.condition:
            if fresh:
                self.consumed = self.number
            while self.number <= self.consumed:
                if self.error:
                    raise ValueError(f"stream reader failed: {self.error}")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise ValueError("no new stream frame within 20 seconds")
                self.condition.wait(remaining)
            self.consumed = self.number
            return self.frame

    def close(self):
        self.stop.set()
        self.response.close()
        self.thread.join(timeout=2)


def check(ip, output):
    base = f"http://{ip}"
    output.mkdir(parents=True, exist_ok=True)
    step = "status/connectivity"
    session = requests.Session()
    session.trust_env = False
    moved = False
    captured = False
    reader = None

    def get(path, **kwargs):
        response = session.get(base + path, timeout=(3, 20), **kwargs)
        response.raise_for_status()
        return response

    def passed(label, started):
        print(f"PASS {label} ({time.monotonic() - started:.2f}s)", flush=True)

    try:
        started = time.monotonic()
        status = get("/status").json()
        required = {"pan", "tilt", "uptime_s", "held_photo", "rssi", "free_heap", "free_psram", "reset_reason"}
        require(required <= status.keys(), "missing status fields")
        require(type(status["held_photo"]) is bool, "held_photo must be boolean")
        for key in required - {"held_photo"}:
            require(type(status[key]) is int, f"{key} must be integer")
        require(status["free_psram"] > 0, "no free PSRAM reported")
        require(not status["held_photo"], "unacknowledged photo exists; save it or /ack before testing")
        print(f"Status: {status}", flush=True)
        passed(step, started)

        step = "small servo pattern/readback (85-95 degrees)"
        started = time.monotonic()
        for pan, tilt in ((85, 90), (95, 90), (90, 85), (90, 95), (90, 90)):
            moved = True
            response = get("/move", params={"pan": pan, "tilt": tilt}).json()
            require(response == {"pan": pan, "tilt": tilt}, "move returned wrong targets")
            time.sleep(0.3)
            observed = get("/status").json()
            require((observed["pan"], observed["tilt"]) == (pan, tilt), "status targets differ")
            if "actual_pan" in observed and "actual_tilt" in observed:
                require((observed["actual_pan"], observed["actual_tilt"]) == (pan, tilt), "servo command slew did not settle")
        passed(step, started)

        step = "QVGA stream"
        started = time.monotonic()
        with session.get(f"{base}:81/stream", stream=True, timeout=(3, 20)) as stream:
            stream.raise_for_status()
            require("multipart/x-mixed-replace" in stream.headers.get("Content-Type", ""), "not MJPEG multipart")
            reader = LiveFrames(stream)
            frame = reader.next_frame()
            require(jpeg_dimensions(frame) == (320, 240), "stream is not QVGA")
            (output / "stream.jpg").write_bytes(frame)
            passed(step, started)

            step = "servo responsiveness while streaming (85-95 degrees)"
            started = time.monotonic()
            for pan, tilt in ((85, 90), (95, 90), (90, 85), (90, 95), (90, 90)):
                move_started = time.monotonic()
                response = get("/move", params={"pan": pan, "tilt": tilt}).json()
                latency = time.monotonic() - move_started
                require(response == {"pan": pan, "tilt": tilt}, "streaming move returned wrong targets")
                print(f"  move pan={pan} tilt={tilt}: {latency:.2f}s", flush=True)
                require(latency < 2, "move acknowledgement exceeded the app's 2s timeout")
                time.sleep(0.3)
                observed = get("/status").json()
                require((observed["pan"], observed["tilt"]) == (pan, tilt), "streaming targets differ")
                require((observed.get("actual_pan"), observed.get("actual_tilt")) == (pan, tilt),
                        "commanded servo slew did not settle while streaming")
                if "move_in_progress" in observed:
                    require(observed["move_in_progress"] is False, "servo task still reports movement pending")
                    elapsed_ms = (observed["move_settled_ms"] - observed["move_received_ms"]) & 0xffffffff
                    print(f"  commanded slew completion: {elapsed_ms}ms (no physical feedback)", flush=True)
                require(jpeg_dimensions(reader.next_frame(fresh=True)) == (320, 240),
                        "stream stopped during servo movement")
            passed(step, started)

            step = "capture while stream connection remains open"
            started = time.monotonic()
            response = get("/capture")
            captured = True
            require(response.headers.get("Content-Type", "").split(";")[0] == "image/jpeg", "capture content type is not JPEG")
            photo = response.content
            width, height = jpeg_dimensions(photo)
            require(width * height > 320 * 240, "capture did not switch to higher resolution")
            (output / "capture.jpg").write_bytes(photo)
            require(get("/status").json()["held_photo"] is True, "photo not retained")
            passed(f"{step}: {width}x{height}, {len(photo)} bytes", started)

            step = "capture retry returns identical held JPEG"
            started = time.monotonic()
            require(get("/capture").content == photo, "capture retry changed held photo")
            passed(step, started)

            step = "ack frees retained photo"
            started = time.monotonic()
            require(get("/ack").json() == {"ok": True}, "ack response differs")
            captured = False
            require(get("/status").json()["held_photo"] is False, "photo still held after ack")
            passed(step, started)

            step = "same stream connection survives capture"
            started = time.monotonic()
            for _ in range(3):
                require(jpeg_dimensions(reader.next_frame(fresh=True)) == (320, 240), "stream size changed after capture")
            passed(step, started)
            reader.close()
            reader = None

        step = "fresh stream after capture/ack"
        started = time.monotonic()
        with session.get(f"{base}:81/stream", stream=True, timeout=(3, 20)) as reopened:
            reopened.raise_for_status()
            require(jpeg_dimensions(next(frames(reopened))) == (320, 240), "fresh stream is not QVGA")
        end = get("/status").json()
        require(end["uptime_s"] >= status["uptime_s"], "board uptime decreased")
        require(end["reset_reason"] == status["reset_reason"], "reset reason changed")
        passed(step, started)
        print(f"PASS camera checks; JPEGs saved under {output.resolve()}", flush=True)
        print("Physical motion, image quality and absence of jitter still need your observation.")
        return 0
    except (requests.RequestException, ValueError, KeyError, TypeError, OSError, StopIteration) as exc:
        print(f"FAIL {step}: {exc}", file=sys.stderr, flush=True)
        print("Check Serial, board IP, shared 2.4 GHz Wi-Fi and client isolation.", file=sys.stderr)
        return 1
    finally:
        if reader is not None:
            reader.close()
        if moved:
            try:
                get("/move", params={"pan": 90, "tilt": 90})
            except requests.RequestException:
                print("WARN could not restore centre", file=sys.stderr)
        if captured:
            print("NOTE photo remains held for recovery; /ack releases it after saving.", file=sys.stderr)
        session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ip", required=True, type=ipaddress.IPv4Address)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / ".build" / "camera_checks")
    args = parser.parse_args()
    return check(str(args.ip), args.output_dir)


if __name__ == "__main__":
    sys.exit(main())
