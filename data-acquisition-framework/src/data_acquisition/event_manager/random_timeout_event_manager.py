import random
from logging import Logger
from typing import Optional

from ..events import TimeoutEvent
from ..gui import Gui
from .simple_event_manager import SimpleEventManager


class RandomTimeoutEventManager(SimpleEventManager[None]):
    def __init__(
        self,
        *,
        gui: Gui,
        timeout_min_millis: int,
        timeout_max_millis: int,
        logger: Optional[Logger] = None,
    ) -> None:
        self._gui = gui

        self._timeout_min_millis = timeout_min_millis
        self._timeout_max_millis = timeout_max_millis
        random_timeout_event_millis = random.randint(
            timeout_min_millis, timeout_max_millis
        )
        self._random_timeout_event = TimeoutEvent(
            gui=gui,
            timeout_millis=random_timeout_event_millis,
            logger=logger,
        )
        super().__init__(events=[self._random_timeout_event], logger=logger)

    def _setup(self) -> None:
        self._random_timeout_event.subscribe(lambda: self._trigger_callbacks(None))

    def _clone(self) -> "RandomTimeoutEventManager":
        return RandomTimeoutEventManager(
            gui=self._gui,
            timeout_min_millis=self._timeout_min_millis,
            timeout_max_millis=self._timeout_max_millis,
        )
