"""UDP light states; transient flashes preserve the remembered steady state."""
from threading import Lock
import socket

STEADY_STATES = {'ready', 'tracking', 'nosubject', 'reconnect', 'sleep'}
FLASH_STATES = {'heard', 'saved', 'error'}
LIGHT_COLORS = dict(ready='soft green', heard='blue flash', tracking='cyan',
                    nosubject='amber blink', saved='white flash', error='red double blink',
                    reconnect='purple blink', sleep='off')


class LightClient:
    def __init__(self, host, port=5006):
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.steady_state = 'ready'
        self.reconnecting = False
        self.lock = Lock()

    def send(self, state):
        if state not in LIGHT_COLORS:
            raise ValueError(f'Unknown light state: {state}')
        with self.lock:
            if state in STEADY_STATES:
                self.steady_state = state
            wire_state = 'reconnect' if self.reconnecting and self.steady_state != 'sleep' else state
            self.socket.sendto(wire_state.encode('ascii'), self.address)
        # Firmware/mock owns the nonblocking 300 ms flash and return to steady.

    def set_reconnecting(self, enabled):
        with self.lock:
            if self.reconnecting == enabled:
                return
            self.reconnecting = enabled
            state = 'reconnect' if enabled and self.steady_state != 'sleep' else self.steady_state
            self.socket.sendto(state.encode('ascii'), self.address)

    def close(self):
        self.socket.close()
