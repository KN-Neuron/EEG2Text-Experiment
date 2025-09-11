from logging import Logger
from typing import Optional

from ..events import KeyPressEvent
from ..gui import Gui
from ..gui.event_types import Key
from .simple_event_manager import SimpleEventManager


class CorrectIncorrectEventManager(SimpleEventManager[bool]):
    def __init__(
        self,
        *,
        gui: Gui,
        correct_response_key: Key,
        incorrect_response_key: Key,
        logger: Optional[Logger] = None,
    ) -> None:
        self._gui = gui

        self._correct_response_key = correct_response_key
        self._correct_event = KeyPressEvent(
            gui=gui, key=correct_response_key, logger=logger
        )

        self._incorrect_response_key = incorrect_response_key
        self._incorrect_event = KeyPressEvent(
            gui=gui, key=incorrect_response_key, logger=logger
        )

        super().__init__(
            events=[self._correct_event, self._incorrect_event], logger=logger
        )

    def _setup(self) -> None:
        self._correct_event.subscribe(lambda: self._trigger_callbacks(True))
        self._incorrect_event.subscribe(lambda: self._trigger_callbacks(False))

    def _clone(self) -> "CorrectIncorrectEventManager":
        return CorrectIncorrectEventManager(
            gui=self._gui,
            correct_response_key=self._correct_response_key,
            incorrect_response_key=self._incorrect_response_key,
        )
