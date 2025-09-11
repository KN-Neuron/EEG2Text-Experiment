from logging import Logger
from typing import Callable, Generic, Optional, Sequence, TypeVar

from ..event_manager import EventManager
from ..eventful_screen import EventfulScreen
from ..gui import Gui
from ..screens import TextScreen
from .errors import EmptyInitialScreenSequenceError, ScreenSequencerStopIteration
from .simple_screen_sequencer import SimpleScreenSequencer

T = TypeVar("T")


class TextScreenSequencer(SimpleScreenSequencer[T], Generic[T]):
    def __init__(
        self,
        *,
        gui: Gui,
        event_manager: EventManager[T],
        texts: Sequence[str],
        screen_show_callback: Callable[[str], None] = lambda _: None,
        logger: Optional[Logger] = None,
    ) -> None:
        if not texts:
            raise EmptyInitialScreenSequenceError("Text sequence is empty.")

        super().__init__(
            gui=gui, screen_show_callback=screen_show_callback, logger=logger
        )
        self._event_manager = event_manager
        self._texts = texts
        self._idx = 0

    def _get_next(self) -> EventfulScreen[T]:
        if self._idx >= len(self._texts):
            raise ScreenSequencerStopIteration

        text = self._texts[self._idx]

        screen = TextScreen(gui=self._gui, text=text)
        cloned_event_manager = self._event_manager.clone()
        result = EventfulScreen(
            screen=screen,
            event_manager=cloned_event_manager,
            screen_show_callback=lambda: self._screen_show_callback(text),
        )

        self._idx += 1

        return result
