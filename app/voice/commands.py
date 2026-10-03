"""Exact wake-word grammar and typed commands; no control side effects."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    action: str
    target: str | None = None
    direction: str | None = None
    small: bool = False


_COMMANDS = {f'track {target}': Command('track', target=target)
             for target in ('person', 'face', 'dog', 'cat')}
_COMMANDS['stop tracking'] = Command('stop_tracking')
for direction in ('left', 'right', 'up', 'down'):
    _COMMANDS[direction] = Command('move', direction=direction)
    _COMMANDS[f'a bit {direction}'] = Command('move', direction=direction, small=True)
for action in ('centre', 'shoot', 'burst', 'timer', 'sleep', 'wake'):
    _COMMANDS[action] = Command(action)
COMMAND_PHRASES = tuple(f'camera {phrase}' for phrase in _COMMANDS)
GRAMMAR = [*COMMAND_PHRASES, '[unk]']


def parse(text: str) -> Command | None:
    """Accept exactly one supported phrase, with a leading camera wake word."""
    normalized = ' '.join(text.lower().split())
    if not normalized.startswith('camera '):
        return None
    return _COMMANDS.get(normalized[len('camera '):])
