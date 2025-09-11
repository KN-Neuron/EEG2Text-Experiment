from unittest import TestCase
from unittest.mock import MagicMock

from .mocks.simple_event_manager import MockSimpleEventManager


class TestSimpleEventManager(TestCase):
    def setUp(self) -> None:
        self._event_mocks = [MagicMock() for _ in range(3)]
        self._event_manager = MockSimpleEventManager(events=self._event_mocks)

    def test_starts_all_events(self) -> None:
        self._event_manager.start()

        for event_mock in self._event_mocks:
            event_mock.start_listening.assert_called_once()

    def test_calls_setup(self) -> None:
        self._event_manager.start()

        self.assertTrue(self._event_manager.was_setup_called)

    def test_stops_all_events(self) -> None:
        self._event_manager.start()

        self._event_manager.stop()

        for event_mock in self._event_mocks:
            event_mock.stop_listening.assert_called_once()
