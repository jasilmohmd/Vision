import struct
from threading import Thread
from time import monotonic
from app.voice.ble_source import BlePcmBuffer


def packet(index, samples):
    return struct.pack('<I', index) + samples


def test_gap_duplicate_and_wrap_preserve_sample_positions():
    buffer = BlePcmBuffer()
    buffer.feed(packet(0xfffffffe, b'\x01\x00\x02\x00'))
    buffer.feed(packet(1, b'\x03\x00'))  # One missing sample across uint32 wrap.
    buffer.feed(packet(1, b'\x03\x00'))  # Duplicate must not replay speech.
    assert buffer.data == b'\x01\x00\x02\x00\x00\x00\x03\x00'
    assert buffer.received_samples == 3
    assert buffer.missing_samples == 1
    assert buffer.out_of_order == 1


def test_malformed_packets_do_not_make_watchdog_healthy():
    buffer = BlePcmBuffer()
    for data in (b'', bytes(5), bytes(7), bytes(246)):
        buffer.feed(data)
    assert buffer.invalid_packets == 4
    assert buffer.last_received_at is None


def test_reconnect_discards_old_audio_and_sequence():
    buffer = BlePcmBuffer()
    buffer.feed(packet(100, b'\x01\x00'))
    buffer.reset_session()
    buffer.feed(packet(0, b'\x02\x00'))
    assert buffer.data == b'\x02\x00'
    assert buffer.missing_samples == 0


def test_large_gap_is_bounded_and_close_wakes_consumer():
    buffer = BlePcmBuffer()
    buffer.feed(packet(0, b'\x01\x00'))
    buffer.feed(packet(100000, b'\x02\x00'))
    assert buffer.data == b'\x02\x00'
    assert buffer.missing_samples == 99999
    results = []
    reader = Thread(target=lambda: results.append(buffer.read_chunk()))
    reader.start()
    buffer.close()
    reader.join(.5)
    assert not reader.is_alive()
    assert results == [b'']


def test_partial_playout_keeps_received_samples_and_reports_padding():
    buffer = BlePcmBuffer()
    buffer.data.extend(b'\x07\x00')
    buffer.next_playout = monotonic()
    assert buffer.read_chunk() == b'\x07\x00' + bytes(1022)
    assert buffer.padded_samples == 511
    assert buffer.silence_chunks == 1


def test_reconnect_during_paced_read_returns_only_new_session_audio():
    buffer = BlePcmBuffer()
    buffer.data.extend(bytes(3072))
    buffer.next_playout = monotonic() + 10
    results = []
    reader = Thread(target=lambda: results.append(buffer.read_chunk()))
    reader.start()
    buffer.reset_session()
    for i in range(13):
        buffer.feed(packet(i * 120, b'\x05\x00' * 120))
    reader.join(.5)
    buffer.close()
    assert not reader.is_alive()
    assert results == [b'\x05\x00' * 512]
