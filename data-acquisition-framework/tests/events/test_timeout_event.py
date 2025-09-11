from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.events import TimeoutEvent


class TestTimeoutEvent(TestCase):
    def setUp(self) -> None:
        self._timeout_event = TimeoutEvent(gui=MagicMock(), timeout_millis=1000)

    def test_clone_returns_new_object(self) -> None:
        cloned_timeout_event = self._timeout_event.clone()

        self.assertIsNot(self._timeout_event, cloned_timeout_event)
