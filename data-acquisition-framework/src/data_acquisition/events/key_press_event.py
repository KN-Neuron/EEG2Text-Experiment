from logging import Logger
from typing import Optional, cast

from ..gui import Gui
from ..gui.event_types import Key, KeyPressEventType
from .gui_event import GuiEvent


class KeyPressEvent(GuiEvent):
    def __init__(self, *, gui: Gui, key: Key, logger: Optional[Logger] = None) -> None:
        event_type = KeyPressEventType(key=key)
        super().__init__(gui=gui, event_type=event_type, logger=logger)

    def clone(self) -> "KeyPressEvent":
        return KeyPressEvent(
            gui=self._gui, key=cast(KeyPressEventType, self._event_type).key
        )
