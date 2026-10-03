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
        self.lock = Lock()

    def send(self, state):
        if state not in LIGHT_COLORS:
            raise ValueError(f'Unknown light state: {state}')
        with self.lock:
            self.socket.sendto(state.encode('ascii'), self.address)
            if state in STEADY_STATES:
                self.steady_state = state
        # Firmware/mock owns the nonblocking 300 ms flash and return to steady.

    def close(self):
        self.socket.close()
