from logging import Logger
from typing import Optional

from ..events import TimeoutEvent
from ..gui import Gui
from .simple_event_manager import SimpleEventManager


class FixedTimeoutEventManager(SimpleEventManager[None]):
    def __init__(
        self,
        *,
        gui: Gui,
        timeout_millis: int,
        logger: Optional[Logger] = None,
    ) -> None:
        self._timeout_millis = timeout_millis
        self._timeout_event = TimeoutEvent(
            gui=gui, timeout_millis=timeout_millis, logger=logger
        )

        super().__init__(events=[self._timeout_event], logger=logger)

        self._gui = gui

    def _setup(self) -> None:
        self._timeout_event.subscribe(lambda: self._trigger_callbacks(None))

    def _clone(self) -> "FixedTimeoutEventManager":
        return FixedTimeoutEventManager(
            gui=self._gui,
            timeout_millis=self._timeout_millis,
        )
