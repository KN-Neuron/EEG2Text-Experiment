from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.events import KeyPressEvent
from src.data_acquisition.gui.event_types import Key


class TestKeyPressEvent(TestCase):
    def setUp(self) -> None:
        self.key_press_event = KeyPressEvent(gui=MagicMock(), key=Key.SHIFT_LEFT)

    def test_clone_returns_new_object(self) -> None:
        cloned_key_press_event = self.key_press_event.clone()

        self.assertIsNot(self.key_press_event, cloned_key_press_event)
