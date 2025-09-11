from typing import Callable
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.data_acquisition.event_manager import KeyPressEventManager
from src.data_acquisition.gui.event_types import Key

from .mocks.events import MockKeyPressEvent

TestForAllKeysCallback = Callable[[KeyPressEventManager, Key], None]


@patch(
    "src.data_acquisition.event_manager.key_press_event_manager.KeyPressEvent",
    new=MockKeyPressEvent,
)
class TestKeyPressEventManager(TestCase):
    _expected_result = None
    _created_event_instances_per_key_count = 1
    _created_event_instances_per_key_count_after_clone = 2

    def setUp(self) -> None:
        MockKeyPressEvent.reset_instances()

    def _test_for_all_keys(self, callback: TestForAllKeysCallback) -> None:
        for key in Key:
            with self.subTest(key=key):
                MockKeyPressEvent.reset_instances()

                key_press_event_manager = KeyPressEventManager(
                    gui=MagicMock(),
                    key=key,
                )

                callback(key_press_event_manager, key)

    def _test_triggers_callback_on_key_press(
        self, key_press_event_manager: KeyPressEventManager, key: Key
    ) -> None:
        callback_mock = MagicMock()

        key_press_event_manager.register_callback(callback_mock)
        key_press_event_manager.start()

        events_for_key = MockKeyPressEvent.get_instance_for_key(key)
        self.assertEqual(
            len(events_for_key), self._created_event_instances_per_key_count
        )
        events_for_key[0].trigger_callbacks()

        key_press_event_manager.stop()

        callback_mock.assert_called_once_with(self._expected_result)

    def test_triggers_callback_on_key_press(self) -> None:
        self._test_for_all_keys(self._test_triggers_callback_on_key_press)

    def _test_clone_returns_new_object(
        self, key_press_event_manager: KeyPressEventManager, _key: Key
    ) -> None:
        cloned_key_press_event_manager = key_press_event_manager.clone()

        self.assertIsNot(
            key_press_event_manager,
            cloned_key_press_event_manager,
        )

    def test_clone_returns_new_object(self) -> None:
        self._test_for_all_keys(self._test_clone_returns_new_object)

    def _test_clone_creates_new_instance_of_key_press_event(
        self, key_press_event_manager: KeyPressEventManager, key: Key
    ) -> None:
        cloned_key_press_event_manager = key_press_event_manager.clone()

        self.assertIsNot(
            key_press_event_manager,
            cloned_key_press_event_manager,
        )

        event_instances = MockKeyPressEvent.get_instance_for_key(key)
        self.assertIsNotNone(event_instances)
        self.assertEqual(
            len(event_instances),
            self._created_event_instances_per_key_count_after_clone,
        )

    def test_clone_creates_new_instance_of_key_press_event(self) -> None:
        self._test_for_all_keys(
            self._test_clone_creates_new_instance_of_key_press_event
        )
