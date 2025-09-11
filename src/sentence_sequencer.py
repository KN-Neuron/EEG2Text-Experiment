from logging import Logger

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import (
    CompositeEventManager,
    EventManager,
    FixedTimeoutEventManager,
    KeyPressEventManager,
    RandomTimeoutEventManager,
)
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.gui.event_types import Key
from data_acquisition.screens import BlankScreen, FixationCrossScreen, TextScreen
from data_acquisition.sequencers import SimpleScreenSequencer

from .config import Config
from .constants import (
    NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
    NON_SENTENCE_SCREEN_TEXT_COLOR,
)


class SentenceSequencer(SimpleScreenSequencer[None]):
    def __init__(
        self,
        *,
        gui: Gui,
        eeg_headset: EEGHeadset,
        config: Config,
        sentences: list[str],
        logger: Logger,
    ):
        super().__init__(gui=gui, logger=logger)

        self._sentences = sentences
        self._eeg_headset = eeg_headset
        self._config = config
        self._logger = logger

        self._continue_screen_event_manager = KeyPressEventManager(
            gui=self._gui, key=config.continue_screen_advance_key, logger=logger
        )
        self._continue_screen_event_manager.register_callback(
            lambda _: self._logger.info("pause end - participant pressed continue key")
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

        self._pause_screen = TextScreen(
            gui=self._gui,
            text=config.pause_screen_text,
            text_color=NON_SENTENCE_SCREEN_TEXT_COLOR,
            background_color=NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
        )
        self._continue_screen = TextScreen(
            gui=self._gui,
            text=config.continue_screen_text,
            text_color=NON_SENTENCE_SCREEN_TEXT_COLOR,
            background_color=NON_SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        self._was_first_screen_shown = False
        self._was_fixation_cross_shown = False
        self._was_paused = False
        self._was_relax_screen_shown = False
        self._index = 0

    def _build_sentence_screen_event_manager(
        self,
        *,
        advance_key: Key,
        timeout_millis: int,
    ) -> None:
        key_event_manager = KeyPressEventManager(
            gui=self._gui, key=advance_key, logger=self._logger
        )
        key_event_manager.register_callback(
            lambda _: self._logger.info(
                "sentence end - participant pressed continue key"
            )
        )

        timeout_event_manager = FixedTimeoutEventManager(
            gui=self._gui, timeout_millis=timeout_millis, logger=self._logger
        )
        timeout_event_manager.register_callback(
            lambda _: self._logger.info("sentence end - timeout")
        )

        self._sentence_screen_event_manager = CompositeEventManager(
            event_managers=[key_event_manager, timeout_event_manager],
            logger=self._logger,
        )
        self._sentence_screen_event_manager.register_callback(
            lambda _: self._eeg_headset.annotate(
                self._config.sentence_screen_end_annotation
            )
        )

    def _build_fixation_cross_screen_event_manager(
        self, *, timeout_range_start_millis: int, timeout_range_end_millis: int
    ) -> None:
        self._fixation_cross_screen_event_manager = RandomTimeoutEventManager(
            gui=self._gui,
            timeout_min_millis=timeout_range_start_millis,
            timeout_max_millis=timeout_range_end_millis,
            logger=self._logger,
        )
        self._fixation_cross_screen_event_manager.register_callback(
            lambda _: self._logger.info("fixation cross end")
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
            self._relax_screen_end_callback
        )

    def _relax_screen_end_callback(self, _: None) -> None:
        self._eeg_headset.annotate(self._config.relax_screen_end_annotation)
        self._logger.info("relax end")

    def _get_next(self) -> EventfulScreen[None]:
        if not self._was_first_screen_shown and self._config.do_show_continue_screen:
            return self._get_continue_screen()
        self._was_first_screen_shown = True

        if self._was_paused:
            return self._get_pause_screen()

        if self._index >= self._config.sentence_count:
            return self._get_relax_screen()

        if not self._was_fixation_cross_shown:
            return self._get_fixation_cross_screen()

        return self._get_sentence_screen()

    def _get_continue_screen(self) -> EventfulScreen[None]:
        self._was_first_screen_shown = True

        continue_screen = self._continue_screen

        screen = EventfulScreen(
            screen=continue_screen,
            event_manager=self._continue_screen_event_manager.clone(),
            screen_show_callback=lambda: self._logger.info("pause start"),
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
            raise StopIteration

        self._was_relax_screen_shown = True

        relax_screen = BlankScreen(gui=self._gui)

        relax_screen_event_manager = self._relax_screen_event_manager.clone()

        screen = EventfulScreen(
            screen=relax_screen,
            event_manager=relax_screen_event_manager,
            screen_show_callback=self._relax_screen_start_callback,
        )

        return screen

    def _relax_screen_start_callback(self) -> None:
        self._eeg_headset.annotate(self._config.relax_screen_start_annotation)
        self._logger.info("relax start")

    def _get_fixation_cross_screen(self) -> EventfulScreen[None]:
        self._was_fixation_cross_shown = True

        screen = FixationCrossScreen(gui=self._gui)
        event_manager = self._get_event_manager_with_pause(
            self._fixation_cross_screen_event_manager
        )
        screen = EventfulScreen(
            screen=screen,
            event_manager=event_manager,
            screen_show_callback=lambda: self._logger.info("fixation cross start"),
        )

        return screen

    def _get_sentence_screen(self) -> EventfulScreen[None]:
        self._was_fixation_cross_shown = False
        self._index += 1

        text = self._sentences.pop()

        screen = TextScreen(gui=self._gui, text=text)
        event_manager = self._get_event_manager_with_pause(
            self._sentence_screen_event_manager
        )
        screen = EventfulScreen(
            screen=screen,
            event_manager=event_manager,
            screen_show_callback=lambda: self._sentence_screen_show_callback(text),
        )

        return screen

    def _sentence_screen_show_callback(self, text: str) -> None:
        self._eeg_headset.annotate(self._config.sentence_screen_start_annotation)
        self._logger.info(f"sentence start - {text}")

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
