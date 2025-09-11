from typing import Sequence
from unittest import TestCase
from unittest.mock import MagicMock

from src.data_acquisition.sequencers import EmptyInitialScreenSequenceError
from src.data_acquisition.sequencers.block_screen_sequencer import BlockScreenSequencer
from tests.sequencers.mocks.example_screen_sequencer import ExampleScreenSequencer


class TestBlockScreenSequencer(TestCase):
    _ELEMENT_COUNT_SEQUENCES = (
        (1,),
        (2, 3),
        (50, 50, 50),
    )

    def _create_sequencer_blocks(self) -> Sequence[Sequence[ExampleScreenSequencer]]:
        sequencer_blocks = tuple(
            tuple(
                ExampleScreenSequencer(element_count=element_count)
                for element_count in sequence
            )
            for sequence in self._ELEMENT_COUNT_SEQUENCES
        )

        return sequencer_blocks

    def test_empties_all_sequencers(self) -> None:
        test_sequencers_blocks = self._create_sequencer_blocks()

        for sequencer_block in test_sequencers_blocks:
            with self.subTest(sequencer_block=sequencer_block):
                sequencer = BlockScreenSequencer(sequencers=sequencer_block)

                all_element_count = sum(
                    sequencer.element_count for sequencer in sequencer_block
                )

                for _ in range(all_element_count):
                    sequencer.get_next()
                    sequencer.pass_previous_result(None)

                with self.assertRaises(StopIteration):
                    sequencer.get_next()

    def test_calls_block_start_callback(self) -> None:
        test_sequencers_blocks = self._create_sequencer_blocks()

        for sequencer_block in test_sequencers_blocks:
            with self.subTest(sequencer_block=sequencer_block):
                mock_block_start_callback = MagicMock()

                block_sequencer = BlockScreenSequencer(
                    sequencers=sequencer_block,
                    block_start_callback=mock_block_start_callback,
                )

                for block_idx, sequencer in enumerate(sequencer_block):
                    block_sequencer.get_next()
                    block_sequencer.pass_previous_result(None)

                    expected_call_count = block_idx + 1
                    expected_block_number = block_idx + 1
                    self.assertEqual(
                        mock_block_start_callback.call_count, expected_call_count
                    )
                    mock_block_start_callback.assert_called_with(expected_block_number)

                    remaining_element_count = sequencer.element_count - 1
                    for _ in range(remaining_element_count):
                        block_sequencer.get_next()
                        block_sequencer.pass_previous_result(None)

                    self.assertEqual(
                        mock_block_start_callback.call_count, expected_call_count
                    )

    def test_calls_block_end_callback(self) -> None:
        test_sequencers_blocks = self._create_sequencer_blocks()

        for sequencer_block in test_sequencers_blocks:
            with self.subTest(sequencer_block=sequencer_block):
                mock_block_end_callback = MagicMock()

                block_sequencer = BlockScreenSequencer(
                    sequencers=sequencer_block,
                    block_end_callback=mock_block_end_callback,
                )

                for block_idx, subsequencer in enumerate(sequencer_block):
                    block_sequencer.get_next()
                    block_sequencer.pass_previous_result(None)

                    expected_block_number = block_idx

                    expected_call_count_after_starting_next_block = block_idx
                    self.assertEqual(
                        mock_block_end_callback.call_count,
                        expected_call_count_after_starting_next_block,
                    )
                    if block_idx > 0:
                        mock_block_end_callback.assert_called_with(
                            expected_block_number
                        )

                    for _ in range(subsequencer.element_count - 1):
                        block_sequencer.get_next()
                        block_sequencer.pass_previous_result(None)

                try:
                    block_sequencer.get_next()
                except StopIteration:
                    pass

                expected_call_count_after_last_block = len(sequencer_block)
                expected_block_number = len(sequencer_block)
                self.assertEqual(
                    mock_block_end_callback.call_count,
                    expected_call_count_after_last_block,
                )
                mock_block_end_callback.assert_called_with(expected_block_number)

    def test_throws_if_passed_empty_sequence(self) -> None:
        with self.assertRaises(EmptyInitialScreenSequenceError):
            BlockScreenSequencer(sequencers=[])
