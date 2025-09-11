from logging import Logger
from typing import Optional, cast

from ..gui import Gui
from ..gui.event_types import TimeoutEventType
from .gui_event import GuiEvent


class TimeoutEvent(GuiEvent):
    def __init__(
        self, *, gui: Gui, timeout_millis: int, logger: Optional[Logger] = None
    ) -> None:
        event_type = TimeoutEventType(timeout_millis=timeout_millis)
        super().__init__(gui=gui, event_type=event_type, logger=logger)

    def clone(self) -> "TimeoutEvent":
        return TimeoutEvent(
            gui=self._gui,
            timeout_millis=cast(TimeoutEventType, self._event_type).timeout_millis,
        )
