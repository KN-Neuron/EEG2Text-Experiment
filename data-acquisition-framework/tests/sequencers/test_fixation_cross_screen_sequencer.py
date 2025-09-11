from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.data_acquisition.sequencers.fixation_cross_screen_sequencer import (
    FixationCrossScreenSequencer,
)
from tests.sequencers.mocks.example_screen_sequencer import ExampleScreenSequencer


class TestFixationCrossScreenSequencer(TestCase):
    @patch(
        "src.data_acquisition.sequencers.fixation_cross_screen_sequencer.FixationCrossScreen",
    )
    def test_returns_fixation_cross_screen_before_every_screen(
        self, FixationCrossMagicMock: MagicMock
    ) -> None:
        screen_count = 2
        screen_with_fixation_cross_count = 2 * screen_count

        test_sequencer = ExampleScreenSequencer(element_count=screen_count)
        fixation_cross_sequencer = FixationCrossScreenSequencer(
            gui=MagicMock(),
            subsequencer=test_sequencer,
            fixation_screen_event_manager=MagicMock(),
        )

        for i in range(screen_with_fixation_cross_count):
            fixation_cross_sequencer.get_next()

            if i % 2 == 0:
                FixationCrossMagicMock.assert_called_once()
                FixationCrossMagicMock.reset_mock()
            else:
                FixationCrossMagicMock.assert_not_called()

            fixation_cross_sequencer.pass_previous_result(None)

        with self.assertRaises(StopIteration):
            fixation_cross_sequencer.get_next()

    @patch(
        "src.data_acquisition.sequencers.fixation_cross_screen_sequencer.FixationCrossScreen",
    )
    def test_returns_fixation_screen_after_reset(
        self, FixationCrossMagicMock: MagicMock
    ) -> None:
        screen_count = 2

        test_sequencer = ExampleScreenSequencer(element_count=screen_count)
        fixation_cross_sequencer = FixationCrossScreenSequencer(
            gui=MagicMock(),
            subsequencer=test_sequencer,
            fixation_screen_event_manager=MagicMock(),
        )

        fixation_cross_sequencer.get_next()
        fixation_cross_sequencer.pass_previous_result(None)
        FixationCrossMagicMock.assert_called_once()
        FixationCrossMagicMock.reset_mock()

        fixation_cross_sequencer.reset()
        fixation_cross_sequencer.get_next()
        fixation_cross_sequencer.pass_previous_result(None)
        FixationCrossMagicMock.assert_called_once()
        FixationCrossMagicMock.reset_mock()

        fixation_cross_sequencer.get_next()
        fixation_cross_sequencer.pass_previous_result(None)
        FixationCrossMagicMock.assert_not_called()
        FixationCrossMagicMock.reset_mock()
