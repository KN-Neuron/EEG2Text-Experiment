from typing import Optional, Sequence
from unittest import TestCase
from unittest.mock import ANY, MagicMock, patch

from src.data_acquisition.sequencers import (
    EmptyInitialScreenSequenceError,
    TextScreenSequencer,
)


class TestTextScreenSequencer(TestCase):
    _DEFAULT_TEST_TEXT_SEQUENCE = ["a", "b", "c", "d"]

    def _create_sequencer(
        self, texts: Optional[Sequence[str]] = None
    ) -> TextScreenSequencer[None]:
        if texts is None:
            texts = self._DEFAULT_TEST_TEXT_SEQUENCE

        return TextScreenSequencer(
            gui=MagicMock(), event_manager=MagicMock(), texts=texts
        )

    def test_creates_as_many_screens_as_texts(self) -> None:
        test_text_sequences = [["a"] * 2, ["b"] * 50, ["c"] * 111]

        for text_sequence in test_text_sequences:
            with self.subTest(text_sequence=text_sequence):
                sequencer = self._create_sequencer(text_sequence)

                for _ in range(len(text_sequence)):
                    sequencer.get_next()
                    sequencer.pass_previous_result(None)

                with self.assertRaises(StopIteration):
                    sequencer.get_next()

    @patch("src.data_acquisition.sequencers.text_screen_sequencer.TextScreen")
    def test_creates_text_screens(self, TextScreenMagicMock: MagicMock) -> None:
        sequencer = self._create_sequencer()

        sequencer.get_next()

        TextScreenMagicMock.assert_called_once_with(
            gui=ANY, text=self._DEFAULT_TEST_TEXT_SEQUENCE[0]
        )

    def test_clones_event_manager_on_get(self) -> None:
        event_manager_mock = MagicMock()

        sequencer = TextScreenSequencer[None](
            gui=MagicMock(),
            event_manager=event_manager_mock,
            texts=self._DEFAULT_TEST_TEXT_SEQUENCE,
        )

        event_manager_mock.reset_mock()

        sequencer.get_next()

        event_manager_mock.clone.assert_called()

    def test_throws_if_passed_empty_sequence(self) -> None:
        with self.assertRaises(EmptyInitialScreenSequenceError):
            self._create_sequencer([])
