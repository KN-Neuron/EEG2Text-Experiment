from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.data_acquisition.event_manager import CorrectIncorrectEventManager
from src.data_acquisition.gui.event_types import Key

from .mocks.events import MockKeyPressEvent


@patch(
    "src.data_acquisition.event_manager.correct_incorrect_event_manager.KeyPressEvent",
    new=MockKeyPressEvent,
)
class TestCorrectIncorrectEventManager(TestCase):
    _CORRECT_RESPONSE_KEY = Key.SHIFT_LEFT
    _INCORRECT_RESPONSE_KEY = Key.SHIFT_RIGHT

    def setUp(self) -> None:
        MockKeyPressEvent.reset_instances()

    def _create_correct_incorrect_timeout_event_manager(
        self,
    ) -> CorrectIncorrectEventManager:
        return CorrectIncorrectEventManager(
            gui=MagicMock(),
            correct_response_key=self._CORRECT_RESPONSE_KEY,
            incorrect_response_key=self._INCORRECT_RESPONSE_KEY,
        )

    def test_triggers_callback_on_key_press(self) -> None:
        test_cases = [
            (self._CORRECT_RESPONSE_KEY, True),
            (self._INCORRECT_RESPONSE_KEY, False),
        ]

        for key, expected_result in test_cases:
            with self.subTest(key=key, expected_result=expected_result):
                MockKeyPressEvent.reset_instances()

                correct_incorrect_event_manager = (
                    self._create_correct_incorrect_timeout_event_manager()
                )

                callback_mock = MagicMock()

                correct_incorrect_event_manager.register_callback(callback_mock)
                correct_incorrect_event_manager.start()

                created_event_instances_per_key_count = 1
                events_for_key = MockKeyPressEvent.get_instance_for_key(key)
                self.assertEqual(
                    len(events_for_key), created_event_instances_per_key_count
                )
                events_for_key[0].trigger_callbacks()

                correct_incorrect_event_manager.stop()

                callback_mock.assert_called_once_with(expected_result)

    def test_clone_returns_new_object(self) -> None:
        correct_incorrect_event_manager = (
            self._create_correct_incorrect_timeout_event_manager()
        )
        cloned_correct_incorrect_event_manager = correct_incorrect_event_manager.clone()

        self.assertIsNot(
            correct_incorrect_event_manager,
            cloned_correct_incorrect_event_manager,
        )

    def test_clone_creates_new_instance_of_key_press_event(self) -> None:
        correct_incorrect_event_manager = (
            self._create_correct_incorrect_timeout_event_manager()
        )
        cloned_correct_incorrect_event_manager = correct_incorrect_event_manager.clone()

        self.assertIsNot(
            correct_incorrect_event_manager,
            cloned_correct_incorrect_event_manager,
        )

        created_event_instances_per_key_count = 2

        correct_response_event_instances = MockKeyPressEvent.get_instance_for_key(
            self._CORRECT_RESPONSE_KEY
        )
        self.assertIsNotNone(correct_response_event_instances)
        self.assertEqual(
            len(correct_response_event_instances),
            created_event_instances_per_key_count,
        )

        incorrect_response_event_instances = MockKeyPressEvent.get_instance_for_key(
            self._INCORRECT_RESPONSE_KEY
        )
        self.assertIsNotNone(incorrect_response_event_instances)
        self.assertEqual(
            len(incorrect_response_event_instances),
            created_event_instances_per_key_count,
        )
