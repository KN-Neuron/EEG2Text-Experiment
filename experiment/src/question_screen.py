from logging import Logger
from typing import Callable

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import KeyPressEventManager
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.gui.event_types import Key
from data_acquisition.screens import TextScreen

from .config import Config
from .constants import (SENTENCE_SCREEN_BACKGROUND_COLOR,
                        SENTENCE_SCREEN_TEXT_COLOR)


class QuestionScreen:
    def __init__(
        self,
        *,
        gui: Gui,
        eeg_headset: EEGHeadset,
        config: Config,
        question: str,
        options: list[str],
        correct_answer_index: int,
        logger: Logger,
        on_answer_callback: Callable[[bool], None] = None,
    ):
        self._gui = gui
        self._eeg_headset = eeg_headset
        self._config = config
        self._question = question
        self._options = options
        self._correct_answer_index = correct_answer_index
        self._logger = logger
        self._on_answer_callback = on_answer_callback

    def create_screen(self) -> EventfulScreen[None]:
        # Format the question and options
        display_text = f"{self._question}\n\n"
        for i, option in enumerate(self._options):
            key = chr(ord("A") + i)
            display_text += f"{key}. {option}\n"

        display_text += "\nWciśnij odpowiednią literę (A, B, C), by wybrać odpowiedź"

        # Create text screen for the question
        question_screen = TextScreen(
            gui=self._gui,
            text=display_text,
            text_color=SENTENCE_SCREEN_TEXT_COLOR,
            background_color=SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        # Create event managers for each option key
        event_managers = []
        for i in range(len(self._options)):
            # key = getattr(Key, chr(ord("A") + i))
            key = chr(ord("A") + i)
            event_manager = KeyPressEventManager(
                gui=self._gui, key=key, logger=self._logger
            )

            # Add callback to check if answer is correct
            def create_callback(selected_index):
                def callback(_):
                    is_correct = selected_index == self._correct_answer_index
                    self._logger.info(
                        f"Question answered: {'Correct' if is_correct else 'Incorrect'}"
                    )
                    if self._on_answer_callback:
                        self._on_answer_callback(is_correct)
                    self._eeg_headset.annotate(
                        f"{self._config.question_screen_end_annotation}_{selected_index}_{is_correct}"
                    )

                return callback

            event_manager.register_callback(create_callback(i))
            event_managers.append(event_manager)

        # Create composite event manager
        from data_acquisition.event_manager import CompositeEventManager

        composite_event_manager = CompositeEventManager(
            event_managers=event_managers,
            logger=self._logger,
        )

        # Create and return eventful screen
        screen = EventfulScreen(
            screen=question_screen,
            event_manager=composite_event_manager,
            screen_show_callback=lambda: self._eeg_headset.annotate(
                self._config.question_screen_start_annotation
            ),
        )

        return screen
