import random
from logging import Logger
from pathlib import Path

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.gui import Gui
from data_acquisition.sequencers import BlockScreenSequencer, ScreenSequencer

from .config import Config
from .constants import TEST_BLOCK_SIZE
# --- MODIFICATION START ---
from .reading_time_analyzer import ReadingTimeAnalyzer
# --- MODIFICATION END ---
from .sentence_sequencer import SentenceSequencer
from .sentences import SentenceSet, load_sentences


class AppSequencerBuilder:
    def __init__(
        self,
        *,
        gui: Gui,
        config: Config,
        headset: EEGHeadset,
        participant_id: str,
        logger: Logger,
        # --- MODIFICATION START ---
        reading_time_analyzer: ReadingTimeAnalyzer,
        # --- MODIFICATION END ---
    ):
        self._gui = gui
        self._config = config
        self._headset = headset
        self._participant_id = participant_id
        self._logger = logger
        # --- MODIFICATION START ---
        self._reading_time_analyzer = reading_time_analyzer
        # --- MODIFICATION END ---

    def set_up_app_sequencer(self) -> ScreenSequencer[None]:
        self._set_up_save_directory()

        sentences = load_sentences()
        sequencers = self._build_mixed_sequencers(sentences)

        return BlockScreenSequencer(
            sequencers=sequencers,
            block_start_callback=lambda _: self._headset.start(),
            block_end_callback=lambda block_number: self._headset.stop_and_save_at_path(
                self._eeg_save_dir / f"{block_number}_raw.fif"
            ),
            logger=self._logger,
        )

    def _set_up_save_directory(self) -> None:
        self._eeg_save_dir = Path("data") / self._participant_id
        self._eeg_save_dir.mkdir(parents=True, exist_ok=True)

    def _build_mixed_sequencers(
        self, sentences: SentenceSet
    ) -> list[ScreenSequencer[None]]:
        # This function creates multiple sequencers. We need to pass the analyzer to each one.
        # We can create a dictionary of common arguments to avoid repetition.
        common_args = {
            "gui": self._gui,
            "eeg_headset": self._headset,
            "config": self._config,
            "logger": self._logger,
            "reading_time_analyzer": self._reading_time_analyzer, # Pass the analyzer
        }


        sequencers = []

        # Add test blocks first
        test_normal = SentenceSequencer(
            **common_args,
            sentences=sentences.test_normal,
            block_type="normal",
            is_test_block=True,
        )
        sequencers.append(test_normal)

        test_sentiment = SentenceSequencer(
            **common_args,
            sentences=sentences.test_sentiment,
            block_type="sentiment",
            is_test_block=True,
        )
        sequencers.append(test_sentiment)

        if sentences.test_audio:
            test_audio = SentenceSequencer(
                **common_args,
                sentences=sentences.test_audio,
                block_type="audio",
                is_test_block=True,
            )
            sequencers.append(test_audio)

        block_types = ["normal", "sentiment"]
        if sentences.audio:
            block_types.append("audio")

        total_blocks = self._config.block_count - 3
        sentences_per_block = self._config.sentence_count

        normal_sentences = sentences.normal.copy()
        sentiment_sentences = sentences.sentiment.copy()
        audio_sentences = sentences.audio.copy() if sentences.audio else []

        for i in range(total_blocks):
            block_type = block_types[i % len(block_types)]

            if block_type == "normal" and normal_sentences:
                block_sentences = normal_sentences[:sentences_per_block]
                normal_sentences = normal_sentences[sentences_per_block:]
            elif block_type == "sentiment" and sentiment_sentences:
                block_sentences = sentiment_sentences[:sentences_per_block]
                sentiment_sentences = sentiment_sentences[sentences_per_block:]
            elif block_type == "audio" and audio_sentences:
                block_sentences = audio_sentences[:sentences_per_block]
                audio_sentences = audio_sentences[sentences_per_block:]
            else:
                continue

            sequencer = SentenceSequencer(
                **common_args,
                sentences=block_sentences,
                block_type=block_type,
            )

            sequencers.append(sequencer)

        return sequencers

