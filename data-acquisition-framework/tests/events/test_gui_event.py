from typing import Sequence
from unittest import TestCase
from unittest.mock import ANY, MagicMock

from src.data_acquisition.events import GuiEvent
from src.data_acquisition.gui import Gui
from src.data_acquisition.gui.event_types import (
    EventType,
    Key,
    KeyPressEventType,
    TimeoutEventType,
)


class ExampleGuiEvent(GuiEvent):
    def __init__(self, *, gui: Gui, event_type: EventType) -> None:
        super().__init__(gui=gui, event_type=event_type)

    def clone(self) -> "ExampleGuiEvent":
        return ExampleGuiEvent(gui=MagicMock(), event_type=MagicMock())

    @property
    def event_id(self) -> int:
        return self._event_id


class TestGuiEvent(TestCase):
    def setUp(self) -> None:
        self._test_event_types: Sequence[EventType] = [
            KeyPressEventType(Key.SHIFT_LEFT),
            KeyPressEventType(Key.SHIFT_RIGHT),
            TimeoutEventType(1000),
        ]

    def test_subscribes_to_gui_event_on_start_listening(self) -> None:
        for event_type in self._test_event_types:
            with self.subTest(event_type=event_type):
                gui_mock = MagicMock()

                gui_event = ExampleGuiEvent(gui=gui_mock, event_type=event_type)

                gui_event.start_listening()

                gui_mock.subscribe_to_event_and_get_id.assert_called_once_with(
                    event=event_type, callback=ANY
                )

    def test_unsubscribes_from_gui_event_on_stop_listening(self) -> None:
        for event_type in self._test_event_types:
            with self.subTest(event_type=event_type):
                gui_mock = MagicMock()

                gui_event = ExampleGuiEvent(gui=gui_mock, event_type=event_type)

                gui_event.start_listening()
                gui_event.stop_listening()

                gui_mock.unsubscribe_from_event_by_id.assert_called_once_with(
                    gui_event.event_id
                )
