from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.eventful_screen import EventfulScreen
from src.data_acquisition.sequencers import (
    IncorrectMethodCallOrderError,
    ScreenSequencerStopIteration,
)
from src.data_acquisition.sequencers.screen_sequencer import ScreenSequencer


class ExampleSequencer(ScreenSequencer[None]):
    ELEMENT_COUNT = 5

    def __init__(self) -> None:
        super().__init__()

        self._has_next_called = False
        self._get_next_called = False
        self._idx = type(self).ELEMENT_COUNT

    @property
    def get_next_called(self) -> bool:
        return self._get_next_called

    def _get_next(self) -> EventfulScreen[None]:
        if self._idx <= 0:
            raise ScreenSequencerStopIteration

        self._get_next_called = True

        self._idx -= 1

        return EventfulScreen(screen=MagicMock(), event_manager=MagicMock())


class TestScreenSequencer(TestCase):
    def _set_up_and_init_sequencer(self) -> ExampleSequencer:
        sequencer = ExampleSequencer()

        sequencer.get_next()

        return sequencer

    def test_calls_get_next_of_subclass(self) -> None:
        sequencer = ExampleSequencer()

        sequencer.get_next()

        self.assertTrue(sequencer.get_next_called)

    def test_throws_if_previous_result_passed_before_getting_first_screen(self) -> None:
        sequencer = ExampleSequencer()

        with self.assertRaises(IncorrectMethodCallOrderError):
            sequencer.pass_previous_result(None)

    def test_throws_if_previous_result_not_passed_before_get_next(self) -> None:
        sequencer = self._set_up_and_init_sequencer()

        with self.assertRaises(IncorrectMethodCallOrderError):
            sequencer.get_next()

    def test_throws_if_previous_result_passed_multiple_times(self) -> None:
        sequencer = self._set_up_and_init_sequencer()

        sequencer.pass_previous_result(None)

        with self.assertRaises(IncorrectMethodCallOrderError):
            sequencer.pass_previous_result(None)

    def test_throws_if_get_next_called_when_emptied(self) -> None:
        sequencer = ExampleSequencer()

        for _ in range(ExampleSequencer.ELEMENT_COUNT):
            sequencer.get_next()
            sequencer.pass_previous_result(None)

        with self.assertRaises(StopIteration):
            sequencer.get_next()
