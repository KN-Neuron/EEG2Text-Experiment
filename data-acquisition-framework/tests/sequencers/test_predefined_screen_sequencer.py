from typing import cast
from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.eventful_screen import EventfulScreen
from src.data_acquisition.sequencers.predefined_screen_sequencer import (
    PredefinedScreenSequencer,
)


class TestPredefinedScreenSequencer(TestCase):
    def test_returns_given_sequence_of_screens(self) -> None:
        screen_count = 15
        screens = [
            cast(
                EventfulScreen[None],
                EventfulScreen(screen=MagicMock(), event_manager=MagicMock()),
            )
            for _ in range(screen_count)
        ]

        predefined_screen_sequencer = PredefinedScreenSequencer(screens=screens)

        for expected_screen in screens:
            actual_screen = predefined_screen_sequencer.get_next()

            self.assertIs(expected_screen, actual_screen)

            predefined_screen_sequencer.pass_previous_result(None)
