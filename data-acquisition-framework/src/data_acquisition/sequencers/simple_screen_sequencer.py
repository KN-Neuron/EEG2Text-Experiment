from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable, Generic, Optional, TypeVar

from ..eventful_screen import EventfulScreen
from ..gui import Gui
from .screen_sequencer import ScreenSequencer

T = TypeVar("T")


class SimpleScreenSequencer(ScreenSequencer[T], Generic[T], ABC):
    def __init__(
        self,
        *,
        gui: Gui,
        screen_show_callback: Callable[[str], None] = lambda _: None,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(logger=logger)

        self._gui = gui
        self._screen_show_callback = screen_show_callback

    @abstractmethod
    def _get_next(self) -> EventfulScreen[T]:
        pass
