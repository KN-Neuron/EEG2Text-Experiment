from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.data_acquisition.event_manager import RandomTimeoutEventManager

from .mocks.events import MockTimeoutEvent


@patch(
    "src.data_acquisition.event_manager.random_timeout_event_manager.TimeoutEvent",
    new=MockTimeoutEvent,
)
class TestRandomTimeoutEventManager(TestCase):
    _timeout_min_millis = 100
    _timeout_max_millis = 1_000_000
    _expected_result = None
    _created_event_instances_count = 1
    _created_event_instances_count_after_clone = 2

    def setUp(self) -> None:
        MockTimeoutEvent.reset_instances()

    def _create_random_timeout_event_manager(self) -> RandomTimeoutEventManager:
        return RandomTimeoutEventManager(
            gui=MagicMock(),
            timeout_min_millis=self._timeout_min_millis,
            timeout_max_millis=self._timeout_max_millis,
        )

    def test_triggers_callback_on_timeout(self) -> None:
        timeout_event_manager = self._create_random_timeout_event_manager()

        callback_mock = MagicMock()

        timeout_event_manager.register_callback(callback_mock)
        timeout_event_manager.start()

        self.assertEqual(
            MockTimeoutEvent.get_instance_count(), self._created_event_instances_count
        )
        MockTimeoutEvent.trigger_callback_for_all_instances()

        timeout_event_manager.stop()

        callback_mock.assert_called_once_with(self._expected_result)

    def test_creates_event_with_timeout_in_given_range(self) -> None:
        test_count = 10_000
        incorrect_timeouts: list[int] = []

        for _ in range(test_count):
            MockTimeoutEvent.reset_instances()

            self._create_random_timeout_event_manager()

            event_timeout = MockTimeoutEvent.get_first_instance_timeout()

            if not (
                self._timeout_min_millis <= event_timeout <= self._timeout_max_millis
            ):
                incorrect_timeouts.append(event_timeout)

        self.assertEqual(
            len(incorrect_timeouts),
            0,
            msg=f"Timeouts not within range: {incorrect_timeouts}",
        )

    def test_timeout_range_is_inclusive(self) -> None:
        MockTimeoutEvent.reset_instances()

        RandomTimeoutEventManager(
            gui=MagicMock(),
            timeout_min_millis=0,
            timeout_max_millis=1,
        )

        event_timeout = MockTimeoutEvent.get_first_instance_timeout()
        self.assertIn(event_timeout, (0, 1))

    @patch(
        "src.data_acquisition.event_manager.random_timeout_event_manager.TimeoutEvent",
        autospec=True,
    )
    def test_clone_returns_new_object(self, _TimeoutEventMagicMock: MagicMock) -> None:
        timeout_event_manager = self._create_random_timeout_event_manager()
        cloned_timeout_event_manager = timeout_event_manager.clone()

        self.assertIsNot(
            timeout_event_manager,
            cloned_timeout_event_manager,
        )

    @patch(
        "src.data_acquisition.event_manager.random_timeout_event_manager.TimeoutEvent",
        autospec=True,
    )
    def test_clone_creates_new_instance_of_timeout_event(
        self, TimeoutEventMagicMock: MagicMock
    ) -> None:
        timeout_event_mock = MagicMock()
        TimeoutEventMagicMock.side_effect = timeout_event_mock

        timeout_event_manager = self._create_random_timeout_event_manager()
        cloned_timeout_event_manager = timeout_event_manager.clone()

        self.assertIsNot(
            timeout_event_manager,
            cloned_timeout_event_manager,
        )

        self.assertEqual(
            MockTimeoutEvent.get_instance_count(),
            self._created_event_instances_count_after_clone,
        )
