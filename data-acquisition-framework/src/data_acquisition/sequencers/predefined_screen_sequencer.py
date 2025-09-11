from logging import Logger
from typing import Optional, Sequence, TypeVar

from ..eventful_screen import EventfulScreen
from .errors import ScreenSequencerStopIteration
from .screen_sequencer import ScreenSequencer

T = TypeVar("T")


class PredefinedScreenSequencer(ScreenSequencer[T]):
    def __init__(
        self,
        *,
        screens: Sequence[EventfulScreen[T]],
        logger: Optional[Logger] = None,
    ) -> None:
        """
        :param screens: A sequence of screens to be returned by the sequencer.
        """

        super().__init__(logger=logger)

        self._screens = screens
        self._idx = 0

    def _get_next(self) -> EventfulScreen[T]:
        if self._idx >= len(self._screens):
            raise ScreenSequencerStopIteration

        result = self._screens[self._idx]

        self._idx += 1

        return result
