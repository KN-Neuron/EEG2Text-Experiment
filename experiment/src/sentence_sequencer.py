import random
from logging import Logger
# --- MODIFICATION START ---
from time import perf_counter

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import (CompositeEventManager,
                                            EventManager,
                                            FixedTimeoutEventManager,
                                            KeyPressEventManager,
                                            RandomTimeoutEventManager)
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.gui.event_types import Key
from data_acquisition.screens import (BlankScreen, FixationCrossScreen,
                                      TextScreen)
from data_acquisition.sequencers import SimpleScreenSequencer

from .audio_screen import AudioScreen
from .config import Config
from .constants import (NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
                        NON_SENTENCE_SCREEN_TEXT_COLOR,
                        SENTENCE_SCREEN_BACKGROUND_COLOR,
                        SENTENCE_SCREEN_TEXT_COLOR)
from .question_screen import QuestionScreen
from .reading_time_analyzer import ReadingTimeAnalyzer
from .sentences import Sentence

# --- MODIFICATION END ---




class SentenceSequencer(SimpleScreenSequencer[None]):
    def __init__(
        self,
        *,
        gui: Gui,
        eeg_headset: EEGHeadset,
        config: Config,
        sentences: list[Sentence],
        block_type: str,
        reading_time_analyzer: ReadingTimeAnalyzer,
        session_reading_times: dict[str, float],
        is_test_block: bool = False,
        logger: Logger,
    ):
        super().__init__(gui=gui, logger=logger)

        self._sentences = sentences
        self._eeg_headset = eeg_headset
        self._config = config
        self._block_type = block_type
        self._reading_time_analyzer = reading_time_analyzer
        self._session_reading_times = session_reading_times
        self._sentence_start_time: float | None = None
        self._is_test_block = is_test_block
        self._logger = logger

        self._correct_answers = 0
        self._total_questions = 0

        if block_type == "normal":
            instruction_text = config.normal_reading_instruction_text
        elif block_type == "sentiment":
            instruction_text = config.sentiment_reading_instruction_text
        elif block_type == "audio":
            instruction_text = config.audio_instruction_text
        else:
            instruction_text = config.continue_screen_text

        self._continue_screen = TextScreen(
            gui=self._gui,
            text=instruction_text,
            text_color=NON_SENTENCE_SCREEN_TEXT_COLOR,
            background_color=NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        self._pause_screen = TextScreen(
            gui=self._gui,
            text=config.pause_screen_text,
            text_color=NON_SENTENCE_SCREEN_TEXT_COLOR,
            background_color=NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        self._continue_screen_event_manager = KeyPressEventManager(
            gui=self._gui, key=config.continue_screen_advance_key, logger=logger
        )
        self._build_sentence_screen_event_manager(
            advance_key=config.sentence_screen_advance_key,
            timeout_millis=config.sentence_screen_timeout_millis,
        )
        self._build_fixation_cross_screen_event_manager(
            timeout_range_start_millis=config.fixation_cross_timeout_range_start_millis,
            timeout_range_end_millis=config.fixation_cross_timeout_range_end_millis,
        )
        self._build_pause_unpause_event_manager(key=config.pause_unpause_key)
        self._build_relax_screen_event_manager(
            timeout_millis=config.relax_screen_timeout_millis
        )

        self._was_first_screen_shown = False
        self._was_fixation_cross_shown = False
        self._was_paused = False
        self._was_relax_screen_shown = False
        self._index = 0
        self._current_sentence = None
        self._show_question = False

        self._setup_questions()

    def _setup_questions(self):

        self._sentences_with_questions = set()

        if self._is_test_block:

            self._sentences_with_questions = set(range(len(self._sentences)))
            return

        total_sentences = len(self._sentences)

        if self._block_type == "normal":
            question_count = int(total_sentences * self._config.normal_question_ratio)
        elif self._block_type == "sentiment":
            question_count = int(
                total_sentences * self._config.sentiment_question_ratio
            )
        else:
            question_count = int(total_sentences * self._config.audio_question_ratio)

        question_indices = random.sample(
            range(total_sentences), min(question_count, total_sentences)
        )
        self._sentences_with_questions = set(question_indices)

        self._logger.info(
            f"Block will have {len(self._sentences_with_questions)} questions out of {total_sentences} sentences"
        )

    def _on_sentence_end(self, _: None) -> None:
        """Callback to handle the end of a sentence screen."""
        self._eeg_headset.annotate(self._config.sentence_screen_end_annotation)
        
        if (
            self._sentence_start_time
            and self._current_sentence
            and self._current_sentence.category == "normal"
        ):
            end_time = perf_counter()
            duration = end_time - self._sentence_start_time
            sentence_text = self._current_sentence.text

            self._logger.info(f"Recorded reading time for '{sentence_text}': {duration:.2f}s")
            self._session_reading_times[sentence_text] = duration

        self._sentence_start_time = None

    def _build_sentence_screen_event_manager(
        self,
        *,
        advance_key: Key,
        timeout_millis: int,
    ) -> None:
        key_event_manager = KeyPressEventManager(
            gui=self._gui, key=advance_key, logger=self._logger
        )
        timeout_event_manager = FixedTimeoutEventManager(
            gui=self._gui, timeout_millis=timeout_millis, logger=self._logger
        )

        self._sentence_screen_event_manager = CompositeEventManager(
            event_managers=[key_event_manager, timeout_event_manager],
            logger=self._logger,
        )
        self._sentence_screen_event_manager.register_callback(self._on_sentence_end)

    def _build_fixation_cross_screen_event_manager(
        self, *, timeout_range_start_millis: int, timeout_range_end_millis: int
    ) -> None:
        self._fixation_cross_screen_event_manager = RandomTimeoutEventManager(
            gui=self._gui,
            timeout_min_millis=timeout_range_start_millis,
            timeout_max_millis=timeout_range_end_millis,
            logger=self._logger,
        )

    def _build_pause_unpause_event_manager(self, *, key: Key) -> None:
        self._pause_unpause_event_manager = KeyPressEventManager(
            gui=self._gui, key=key, logger=self._logger
        )

    def _build_relax_screen_event_manager(self, *, timeout_millis: int) -> None:
        self._relax_screen_event_manager = FixedTimeoutEventManager(
            gui=self._gui, timeout_millis=timeout_millis, logger=self._logger
        )

        self._relax_screen_event_manager.register_callback(
            lambda _: self._eeg_headset.annotate(
                self._config.relax_screen_end_annotation
            )
        )

    def _get_next(self) -> EventfulScreen[None]:
        if not self._was_first_screen_shown and self._config.do_show_continue_screen:
            return self._get_continue_screen()
        self._was_first_screen_shown = True

        if self._was_paused:
            return self._get_pause_screen()

        if self._index >= len(self._sentences):
            return self._get_relax_screen()

        if (
            self._show_question
            and self._current_sentence
            and self._current_sentence.question
        ):
            self._show_question = False
            return self._get_question_screen()

        if not self._was_fixation_cross_shown:
            return self._get_fixation_cross_screen()

        return self._get_sentence_screen()

    def _get_continue_screen(self) -> EventfulScreen[None]:
        self._was_first_screen_shown = True

        continue_screen = self._continue_screen

        screen = EventfulScreen(
            screen=continue_screen,
            event_manager=self._continue_screen_event_manager.clone(),
        )

        return screen

    def _get_pause_screen(self) -> EventfulScreen[None]:
        self._was_paused = False

        self._index -= 1

        pause_event_manager = self._pause_unpause_event_manager.clone()
        pause_event_manager.register_callback(
            lambda _: self._eeg_headset.annotate(
                self._config.pause_screen_end_annotation
            )
        )

        screen = EventfulScreen(
            screen=self._pause_screen,
            event_manager=pause_event_manager,
            screen_show_callback=lambda: self._eeg_headset.annotate(
                self._config.pause_screen_start_annotation
            ),
        )

        return screen

    def _get_relax_screen(self) -> EventfulScreen[None]:
        if self._was_relax_screen_shown:
            if self._is_test_block:
                self._logger.info(
                    f"Test block results: {self._correct_answers}/{self._total_questions} correct answers"
                )
            raise StopIteration

        self._was_relax_screen_shown = True

        relax_screen = BlankScreen(gui=self._gui)

        screen = EventfulScreen(
            screen=relax_screen,
            event_manager=self._relax_screen_event_manager.clone(),
            screen_show_callback=lambda: self._eeg_headset.annotate(
                self._config.relax_screen_start_annotation
            ),
        )

        return screen

    def _get_fixation_cross_screen(self) -> EventfulScreen[None]:
        self._was_fixation_cross_shown = True
        self._was_thinking_screen_shown = False

        screen = FixationCrossScreen(gui=self._gui)
        event_manager = self._get_event_manager_with_pause(
            self._fixation_cross_screen_event_manager
        )
        screen = EventfulScreen(screen=screen, event_manager=event_manager)

        return screen

    def _get_sentence_screen(self) -> EventfulScreen[None]:
        self._was_fixation_cross_shown = False

        if self._index < len(self._sentences):
            self._current_sentence = self._sentences[self._index]
            self._index += 1

            self._show_question = (self._index - 1) in self._sentences_with_questions

            if (
                self._current_sentence.category == "audio"
                and self._current_sentence.audio_path
            ):
                return self._get_audio_screen()
            else:

                text = self._current_sentence.text
                screen = TextScreen(
                    gui=self._gui,
                    text=text,
                    text_color=SENTENCE_SCREEN_TEXT_COLOR,
                    background_color=SENTENCE_SCREEN_BACKGROUND_COLOR,
                )
                event_manager = self._get_event_manager_with_pause(
                    self._sentence_screen_event_manager
                )

                def start_callback():
                    """Callback to handle the start of a sentence screen."""
                    self._eeg_headset.annotate(
                        f"{self._config.sentence_screen_start_annotation}_{self._current_sentence.category}"
                    )
                    # If it's a normal sentence, record the start time
                    if self._current_sentence.category == "normal":
                        self._sentence_start_time = perf_counter()

                eventful_screen = EventfulScreen(
                    screen=screen,
                    event_manager=event_manager,
                    screen_show_callback=start_callback,
                )

                self._logger.info(
                    f"Showing screen with {self._current_sentence.category} sentence: {text}"
                )
                return eventful_screen
        else:

            return self._get_relax_screen()

    def _get_audio_screen(self) -> EventfulScreen[None]:
        # --- MODIFICATION START ---
        sentence_text = self._current_sentence.text
        target_duration = None

        if sentence_text in self._session_reading_times:
            target_duration = self._session_reading_times[sentence_text]
            self._logger.info(
                f"Found session reading time for sentence: {target_duration:.2f}s"
            )

        if not target_duration:
            target_duration = self._reading_time_analyzer.get_avg_reading_time(
                sentence_text
            )
            if target_duration:
                self._logger.info(
                    f"Found average reading time for sentence: {target_duration:.2f}s"
                )
        
        if not target_duration:
            target_duration = (
                self._reading_time_analyzer.estimate_reading_time_from_wpm(
                    sentence_text
                )
            )
            self._logger.info(
                f"No reading time data found. Estimating duration: {target_duration:.2f}s"
            )

        audio_screen = AudioScreen(
            gui=self._gui,
            eeg_headset=self._eeg_headset,
            config=self._config,
            audio_path=self._current_sentence.audio_path,
            text=self._current_sentence.text,
            logger=self._logger,
            target_duration_seconds=target_duration, 
        )

        return audio_screen.create_screen()


    def _get_question_screen(self) -> EventfulScreen[None]:
        def on_answer(is_correct):
            if self._is_test_block:
                self._total_questions += 1
                if is_correct:
                    self._correct_answers += 1

        question_screen = QuestionScreen(
            gui=self._gui,
            eeg_headset=self._eeg_headset,
            config=self._config,
            question=self._current_sentence.question,
            options=self._current_sentence.options,
            correct_answer_index=self._current_sentence.correct_answer_index,
            logger=self._logger,
            on_answer_callback=on_answer,
        )

        return question_screen.create_screen()

    def _get_event_manager_with_pause(
        self, event_manager: EventManager[None]
    ) -> EventManager[None]:
        pause_event_manager = self._pause_unpause_event_manager.clone()
        pause_event_manager.register_callback(self._mark_as_paused)

        pause_screen_event_manager = CompositeEventManager(
            event_managers=[pause_event_manager, event_manager.clone()],
            logger=self._logger,
        )

        return pause_screen_event_manager

    def _mark_as_paused(self, _: None) -> None:
        self._was_paused = True
