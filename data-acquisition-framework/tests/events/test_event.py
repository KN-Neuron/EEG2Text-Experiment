from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.events import Event, IncorrectMethodCallOrderError


class ExampleGuiEvent(Event):
    def _start_listening(self) -> None:
        pass

    def _stop_listening(self) -> None:
        pass

    def clone(self) -> Event:
        return MagicMock()


class TestEvent(TestCase):
    def test_throws_if_start_listening_called_if_already_listening(self) -> None:
        event = ExampleGuiEvent()

        event.start_listening()

        with self.assertRaises(IncorrectMethodCallOrderError):
            event.start_listening()

    def test_throws_if_stop_listening_called_if_not_listening_yet(self) -> None:
        event = ExampleGuiEvent()

        with self.assertRaises(IncorrectMethodCallOrderError):
            event.stop_listening()

    def test_doesnt_throw_if_methods_called_in_correct_order(self) -> None:
        event = ExampleGuiEvent()

        event.start_listening()
        event.stop_listening()
