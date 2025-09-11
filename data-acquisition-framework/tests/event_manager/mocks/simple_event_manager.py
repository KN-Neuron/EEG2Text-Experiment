from typing import Sequence
from unittest.mock import MagicMock

from src.data_acquisition.event_manager import SimpleEventManager
from src.data_acquisition.events import Event


class MockSimpleEventManager(SimpleEventManager[None]):
    def __init__(self, *, events: Sequence[Event]) -> None:
        super().__init__(events=events)

        self._was_setup_called = False
        self._was_clone_called = False

    @property
    def was_setup_called(self) -> bool:
        return self._was_setup_called

    @property
    def was_clone_called(self) -> bool:
        return self._was_clone_called

    def _clone(self) -> "MockSimpleEventManager":
        self._was_clone_called = True

        return MagicMock()

    def _setup(self) -> None:
        self._was_setup_called = True
