from logging import Logger
from typing import Optional

from ..gui import Gui
from ..gui.event_types import EventType
from .event import Event


class GuiEvent(Event):
    def __init__(
        self, *, gui: Gui, event_type: EventType, logger: Optional[Logger] = None
    ):
        super().__init__(logger=logger)

        self._gui = gui
        self._event_type = event_type

    def _start_listening(self) -> None:
        self._event_id = self._gui.subscribe_to_event_and_get_id(
            event=self._event_type, callback=self._trigger_callbacks
        )

    def _stop_listening(self) -> None:
        self._gui.unsubscribe_from_event_by_id(self._event_id)
