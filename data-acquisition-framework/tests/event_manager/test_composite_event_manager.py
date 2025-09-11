from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.event_manager import CompositeEventManager

from .mocks.event_manager import MockEventManager


class TestCompositeEventManager(TestCase):
    _SUBMANAGERS_COUNT = 3

    def setUp(self) -> None:
        self._submanagers = [
            MockEventManager() for _ in range(type(self)._SUBMANAGERS_COUNT)
        ]
        self._composite_event_manager = CompositeEventManager(
            event_managers=self._submanagers
        )

    def test_starts_all_submanagers(self) -> None:
        self._composite_event_manager.start()

        for submanager in self._submanagers:
            self.assertTrue(submanager.was_start_called)

    def test_stops_all_submanagers(self) -> None:
        self._composite_event_manager.start()

        self._composite_event_manager.stop()

        for submanager in self._submanagers:
            self.assertTrue(submanager.was_stop_called)

    def test_triggers_callback_on_any_submanager_callback(self) -> None:
        callback = MagicMock(name="callback")

        self._composite_event_manager.register_callback(callback)

        self._composite_event_manager.start()

        for submanager in self._submanagers:
            with self.subTest(submanager=submanager):
                callback.call_count = 0

                submanager.trigger_callback()

                callback.assert_called_once()

    def test_clone_returns_new_object(self) -> None:
        cloned_composite_event_manager = self._composite_event_manager.clone()

        self.assertIsNot(
            self._composite_event_manager,
            cloned_composite_event_manager,
        )

    def test_clone_clones_submanagers(self) -> None:
        self._composite_event_manager.clone()

        for submanager in self._submanagers:
            self.assertTrue(submanager.was_clone_called)
