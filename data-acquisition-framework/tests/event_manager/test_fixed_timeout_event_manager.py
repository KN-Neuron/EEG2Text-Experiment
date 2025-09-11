from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.data_acquisition.event_manager import FixedTimeoutEventManager

from .mocks.events import MockTimeoutEvent


@patch(
    "src.data_acquisition.event_manager.fixed_timeout_event_manager.TimeoutEvent",
    new=MockTimeoutEvent,
)
class TestFixedTimeoutEventManager(TestCase):
    _timeout_millis = 1000
    _expected_result = None
    _created_event_instances_count = 1
    _created_event_instances_count_after_clone = 2

    def setUp(self) -> None:
        MockTimeoutEvent.reset_instances()

    def _create_fixed_timeout_event_manager(self) -> FixedTimeoutEventManager:
        return FixedTimeoutEventManager(
            gui=MagicMock(), timeout_millis=self._timeout_millis
        )

    def test_triggers_callback_on_timeout(self) -> None:
        timeout_event_manager = self._create_fixed_timeout_event_manager()

        callback_mock = MagicMock()

        timeout_event_manager.register_callback(callback_mock)
        timeout_event_manager.start()

        self.assertEqual(
            MockTimeoutEvent.get_instance_count(), self._created_event_instances_count
        )
        MockTimeoutEvent.trigger_callback_for_all_instances()

        timeout_event_manager.stop()

        callback_mock.assert_called_once_with(self._expected_result)

    @patch(
        "src.data_acquisition.event_manager.fixed_timeout_event_manager.TimeoutEvent",
        autospec=True,
    )
    def test_clone_returns_new_object(self, _TimeoutEventMagicMock: MagicMock) -> None:
        timeout_event_manager = self._create_fixed_timeout_event_manager()
        cloned_timeout_event_manager = timeout_event_manager.clone()

        self.assertIsNot(
            timeout_event_manager,
            cloned_timeout_event_manager,
        )

    @patch(
        "src.data_acquisition.event_manager.fixed_timeout_event_manager.TimeoutEvent",
        autospec=True,
    )
    def test_clone_creates_new_instance_of_timeout_event(
        self, TimeoutEventMagicMock: MagicMock
    ) -> None:
        timeout_event_mock = MagicMock()
        TimeoutEventMagicMock.side_effect = timeout_event_mock

        timeout_event_manager = self._create_fixed_timeout_event_manager()
        cloned_timeout_event_manager = timeout_event_manager.clone()

        self.assertIsNot(
            timeout_event_manager,
            cloned_timeout_event_manager,
        )

        self.assertEqual(
            MockTimeoutEvent.get_instance_count(),
            self._created_event_instances_count_after_clone,
        )
