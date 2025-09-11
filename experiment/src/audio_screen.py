from logging import Logger
from pathlib import Path

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import KeyPressEventManager
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.screens import TextScreen

from .config import Config
from .constants import SENTENCE_SCREEN_BACKGROUND_COLOR, SENTENCE_SCREEN_TEXT_COLOR


class AudioScreen:
    def __init__(
        self,
        *,
        gui: Gui,
        eeg_headset: EEGHeadset,
        config: Config,
        audio_path: str,
        text: str,
        logger: Logger,
    ):
        self._gui = gui
        self._eeg_headset = eeg_headset
        self._config = config
        self._audio_path = audio_path
        self._text = text
        self._logger = logger
        self._is_audio_played = False

    def create_screen(self) -> EventfulScreen[None]:
        import pygame

        display_text = "Słuchaj uważnie...\n\nWciśnij spację po wysłuchaniu."

        audio_screen = TextScreen(
            gui=self._gui,
            text=display_text,
            text_color=SENTENCE_SCREEN_TEXT_COLOR,
            background_color=SENTENCE_SCREEN_BACKGROUND_COLOR,
        )

        key_event_manager = KeyPressEventManager(
            gui=self._gui,
            key=self._config.sentence_screen_advance_key,
            logger=self._logger,
        )

        def end_audio_callback(_):
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            self._eeg_headset.annotate(self._config.sentence_screen_end_annotation)
            self._logger.info("Audio playback ended by user")

        key_event_manager.register_callback(end_audio_callback)

        def play_audio():
            self._eeg_headset.annotate(
                f"{self._config.sentence_screen_start_annotation}_audio"
            )

            direct_path = Path(self._audio_path)
            module_path = Path(__file__).parent / "assets" / self._audio_path
            cwd_path = Path.cwd() / "assets" / self._audio_path

            paths_to_try = [direct_path, module_path, cwd_path]

            found_path = None
            for path in paths_to_try:
                if path.exists():
                    found_path = path
                    self._logger.info(f"Found audio file at: {found_path}")
                    break

            if not found_path:
                self._logger.error(f"Audio file not found: {self._audio_path}")
                self._logger.error(f"Tried paths: {[str(p) for p in paths_to_try]}")
                self._is_audio_played = False
                audio_screen.set_text(
                    f"Nie można znaleźć pliku audio.\n{self._audio_path}\nWciśnij spację, aby kontynuować."
                )
                return

            try:
                if not pygame.mixer.get_init():
                    self._logger.info("Initializing pygame mixer")
                    pygame.mixer.init(
                        frequency=44100, size=-16, channels=2, buffer=2048
                    )

                pygame.mixer.music.load(str(found_path))
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play()
                self._is_audio_played = True
                self._logger.info(f"Playing audio: {found_path}")
            except pygame.error as e:
                self._logger.error(f"Pygame error playing audio {found_path}: {str(e)}")
                self._is_audio_played = False
                audio_screen.set_text(
                    f"Błąd odtwarzania pliku audio.\n{str(e)}\nWciśnij spację, aby kontynuować."
                )
            except Exception as e:
                self._logger.error(f"Unexpected error playing audio: {str(e)}")
                self._is_audio_played = False
                audio_screen.set_text(
                    f"Nieoczekiwany błąd.\n{str(e)}\nWciśnij spację, aby kontynuować."
                )

        screen = EventfulScreen(
            screen=audio_screen,
            event_manager=key_event_manager,
            screen_show_callback=play_audio,
        )

        return screen
