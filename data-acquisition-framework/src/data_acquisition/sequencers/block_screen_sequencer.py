from logging import Logger
from typing import Callable, Generic, Optional, Sequence, TypeVar

from ..eventful_screen import EventfulScreen
from .errors import EmptyInitialScreenSequenceError, ScreenSequencerStopIteration
from .screen_sequencer import ScreenSequencer

T = TypeVar("T")


class BlockScreenSequencer(ScreenSequencer[T], Generic[T]):
    def __init__(
        self,
        *,
        sequencers: Sequence[ScreenSequencer[T]],
        block_start_callback: Callable[[int], None] = lambda _: None,
        block_end_callback: Callable[[int], None] = lambda _: None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        :param sequencers: A sequence of screen sequencers. Each sequencer is a separate block.
        :param block_start_callback: A callback function that is called when a block starts. Takes the block number (1-indexed) as an argument.
        :param block_end_callback: A callback function that is called when a block ends. Takes the block number (1-indexed) as an argument.
        """

        if len(sequencers) == 0:
            raise EmptyInitialScreenSequenceError("Sequencer sequence is empty.")

        super().__init__(logger=logger)

        self._sequencers = sequencers
        self._block_start_callback = block_start_callback
        self._block_end_callback = block_end_callback
        self._sequencer_index = 0
        self._was_first_sequence_started = False

    def _get_next(self) -> EventfulScreen[T]:
        if self._sequencer_index >= len(self._sequencers):
            raise ScreenSequencerStopIteration

        block_number = self._sequencer_index + 1

        current_sequencer = self._sequencers[self._sequencer_index]
        if self._was_first_sequence_started:
            current_sequencer.pass_previous_result(self._previous_result)
        else:
            self._was_first_sequence_started = True
            self._block_start_callback(block_number)

        try:
            result = self._sequencers[self._sequencer_index].get_next()
            return result
        except StopIteration:
            self._block_end_callback(block_number)
            self._sequencer_index += 1
            self._was_first_sequence_started = False

            return self._get_next()
