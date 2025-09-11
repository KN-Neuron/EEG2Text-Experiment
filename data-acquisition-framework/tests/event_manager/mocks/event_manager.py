from unittest.mock import MagicMock

from src.data_acquisition.event_manager import EventManager


class MockEventManager(EventManager[None]):
    def __init__(self) -> None:
        super().__init__()

        self._was_start_called = False
        self._was_stop_called = False
        self._was_clone_called = False

    @property
    def was_start_called(self) -> bool:
        return self._was_start_called

    @property
    def was_stop_called(self) -> bool:
        return self._was_stop_called

    @property
    def was_clone_called(self) -> bool:
        return self._was_clone_called

    def _start(self) -> None:
        self._was_start_called = True

    def _stop(self) -> None:
        self._was_stop_called = True

    def clone(self) -> "MockEventManager":
        self._was_clone_called = True

        return MagicMock()

    def trigger_callback(self) -> None:
        self._trigger_callbacks(None)
