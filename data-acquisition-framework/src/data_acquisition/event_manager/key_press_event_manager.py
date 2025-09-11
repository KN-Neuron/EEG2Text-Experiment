from logging import Logger
from typing import Optional

from ..events import KeyPressEvent
from ..gui import Gui
from ..gui.event_types import Key
from .simple_event_manager import SimpleEventManager


class KeyPressEventManager(SimpleEventManager[None]):
    def __init__(
        self,
        *,
        gui: Gui,
        key: Key,
        logger: Optional[Logger] = None,
    ) -> None:
        self._gui = gui

        self._key = key
        self._key_press_event = KeyPressEvent(gui=gui, key=key, logger=logger)

        super().__init__(events=[self._key_press_event], logger=logger)

    def _setup(self) -> None:
        self._key_press_event.subscribe(lambda: self._trigger_callbacks(None))

    def _clone(self) -> "KeyPressEventManager":
        return KeyPressEventManager(
            gui=self._gui,
            key=self._key,
        )
