from dataclasses import dataclass
from enum import Enum, auto

import pygame

from .event_type import EventType


class Key(Enum):
    ALT_LEFT = auto()
    ALT_RIGHT = auto()
    CONTROL_LEFT = auto()
    CONTROL_RIGHT = auto()
    ENTER = auto()
    ESCAPE = auto()
    SHIFT_LEFT = auto()
    SHIFT_RIGHT = auto()
    SPACE = auto()
    A = auto()
    B = auto()
    C = auto()


@dataclass(frozen=True)
class KeyPressEventType(EventType):
    key: Key


KEY_MAPPING = {
    Key.ALT_LEFT: pygame.K_LALT,
    Key.ALT_RIGHT: pygame.K_RALT,
    Key.CONTROL_LEFT: pygame.K_LCTRL,
    Key.CONTROL_RIGHT: pygame.K_RCTRL,
    Key.ENTER: pygame.K_RETURN,
    Key.ESCAPE: pygame.K_ESCAPE,
    Key.SHIFT_LEFT: pygame.K_LSHIFT,
    Key.SHIFT_RIGHT: pygame.K_RSHIFT,
    Key.SPACE: pygame.K_SPACE,
    "A": pygame.K_a,
    "B": pygame.K_b,
    "C": pygame.K_c,
}
