import itertools
from copy import copy
from logging import Logger
from pathlib import Path

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import KeyPressEventManager
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.screens import TextScreen
from data_acquisition.sequencers import (
    BlockScreenSequencer,
    PredefinedScreenSequencer,
    ScreenSequencer,
)

from .config import Config
from .constants import (
    NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
    NON_SENTENCE_SCREEN_TEXT_COLOR,
    START_EXPRIMENT_SCREEN_ADVANCE_KEY,
    START_EXPRIMENT_SCREEN_TEXT,
)
from .sentence_sequencer import SentenceSequencer
from .sentences import Sentences, load_sentences


class AppSequencerBuilder:
    def __init__(
        self,
        *,
        gui: Gui,
        config: Config,
        headset: EEGHeadset,
        participant_id: str,
        logger: Logger,
    ):
        self._gui = gui
        self._config = config
        self._headset = headset
        self._participant_id = participant_id
        self._logger = logger

    def set_up_app_sequencer(self) -> ScreenSequencer[None]:
        self._set_up_save_directory()

        sentences = load_sentences()
        sequencers = self._build_sequencers_from_sentences(sentences)

        start_experiment_screen_sequencer = (
            self._build_start_experiment_screen_sequencer()
        )
        sequencers[0] = BlockScreenSequencer(
            sequencers=[start_experiment_screen_sequencer, sequencers[0]]
        )

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
        self._eeg_save_dir.mkdir(parents=True)

    def _build_sequencers_from_sentences(
        self, sentences: Sentences
    ) -> list[ScreenSequencer[None]]:
        sequencers: list[ScreenSequencer[None]] = []

        sentences_in_blocks = itertools.islice(
            itertools.cycle([sentences.polish, sentences.english]),
            self._config.block_count,
        )

        for idx, sentences_in_block in enumerate(sentences_in_blocks):
            config = copy(self._config)
            config.do_show_continue_screen = idx != 0

            sequencer = SentenceSequencer(
                gui=self._gui,
                eeg_headset=self._headset,
                config=config,
                sentences=sentences_in_block,
                logger=self._logger,
            )

            sequencers.append(sequencer)

        return sequencers

    def _build_start_experiment_screen_sequencer(
        self,
    ) -> PredefinedScreenSequencer[None]:
        screen = TextScreen(
            gui=self._gui,
            text=START_EXPRIMENT_SCREEN_TEXT,
            text_color=NON_SENTENCE_SCREEN_TEXT_COLOR,
            background_color=NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        event_manager = KeyPressEventManager(
            gui=self._gui, key=START_EXPRIMENT_SCREEN_ADVANCE_KEY
        )
        event_manager.register_callback(
            lambda _: self._logger.info(
                "experiment start - participant pressed start key"
            )
        )

        eventful_screen = EventfulScreen(screen=screen, event_manager=event_manager)

        return PredefinedScreenSequencer(screens=[eventful_screen], logger=self._logger)
