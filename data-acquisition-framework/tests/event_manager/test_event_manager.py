from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.event_manager import EventManager
from src.data_acquisition.event_manager.errors import (
    EventManagerError,
    IncorrectMethodCallOrderError,
)


class ExampleEventManager(EventManager[None]):
    def _start(self) -> None:
        self._trigger_callbacks(None)

    def _stop(self) -> None:
        pass

    def clone(self) -> "ExampleEventManager":
        return MagicMock()


class TestEventManager(TestCase):
    def setUp(self) -> None:
        self._event_manager = ExampleEventManager()

    def test_triggers_callback_correctly(self) -> None:
        callback = MagicMock()
        self._event_manager.register_callback(callback)

        self._event_manager.start()

        callback.assert_called_once_with(None)

    def test_deregisters_callback_correctly(self) -> None:
        callback = MagicMock()
        self._event_manager.register_callback(MagicMock())
        self._event_manager.register_callback(callback)

        self._event_manager.deregister_callback(callback)

        self._event_manager.start()

        callback.assert_not_called()

    def test_throws_if_started_with_no_callback_set(self) -> None:
        with self.assertRaises(EventManagerError):
            self._event_manager.start()

    def test_throws_if_deregistering_callback_not_set(self) -> None:
        not_registered_callback = MagicMock()

        with self.assertRaises(EventManagerError):
            self._event_manager.deregister_callback(not_registered_callback)

    def test_throws_if_start_called_if_already_started(self) -> None:
        self._event_manager.register_callback(lambda _: None)

        self._event_manager.start()

        with self.assertRaises(IncorrectMethodCallOrderError):
            self._event_manager.start()

    def test_throws_if_stop_called_if_not_started_yet(self) -> None:
        self._event_manager.register_callback(lambda _: None)

        with self.assertRaises(IncorrectMethodCallOrderError):
            self._event_manager.stop()

    def test_doesnt_throw_if_methods_called_in_correct_order(self) -> None:
        self._event_manager.register_callback(lambda _: None)

        self._event_manager.start()
        self._event_manager.stop()
