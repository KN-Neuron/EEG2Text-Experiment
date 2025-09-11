from unittest.mock import MagicMock

from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.sequencers.screen_sequencer import ScreenSequencer


class ExampleScreenSequencer(ScreenSequencer[None]):
    def __init__(self, *, element_count: int) -> None:
        super().__init__()

        self._element_count = element_count
        self._idx = element_count

    @property
    def element_count(self) -> int:
        return self._element_count

    def _get_next(self) -> EventfulScreen[None]:
        if self._idx <= 0:
            raise StopIteration

        self._idx -= 1

        return MagicMock()
