# src/audio_screen.py

from io import BytesIO
from logging import Logger
from pathlib import Path

from data_acquisition.eeg_headset import EEGHeadset
from data_acquisition.event_manager import KeyPressEventManager
from data_acquisition.eventful_screen import EventfulScreen
from data_acquisition.gui import Gui
from data_acquisition.screens import TextScreen
# You need pydub for this: pip install pydub
# Also install audiostretchy: pip install audiostretchy
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from .config import Config
from .constants import (SENTENCE_SCREEN_BACKGROUND_COLOR,
                        SENTENCE_SCREEN_TEXT_COLOR)


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
        target_duration_seconds: float | None = None,
    ):
        self._gui = gui
        self._eeg_headset = eeg_headset
        self._config = config
        self._audio_path = audio_path
        self._text = text
        self._logger = logger
        self._is_audio_played = False
        self._target_duration_seconds = target_duration_seconds

    def create_screen(self) -> EventfulScreen[None]:
        import pygame

        # We will display the sentence text on screen while the audio plays
        display_text = self._text

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
                audio = AudioSegment.from_file(found_path)
                original_duration_sec = len(audio) / 1000.0

                # Use stretch_ratio for time stretching (ratio >1 slows down, <1 speeds up)
                stretch_ratio = 1.0
                if self._target_duration_seconds and self._target_duration_seconds > 0:
                    stretch_ratio = self._target_duration_seconds / original_duration_sec
                    self._logger.info(
                        f"Original audio duration: {original_duration_sec:.2f}s, Target: {self._target_duration_seconds:.2f}s. Calculated stretch ratio: {stretch_ratio:.2f}x"
                    )
                else:
                    self._logger.info(
                        f"Playing at normal speed. Original duration: {original_duration_sec:.2f}s"
                    )

                # Clamp ratio to audiostretchy's supported range (0.25 to 4.0)
                if not 0.25 <= stretch_ratio <= 4.0:
                    new_ratio = max(0.25, min(stretch_ratio, 4.0))
                    self._logger.warning(
                        f"Stretch ratio {stretch_ratio:.2f}x is outside the supported range (0.25x - 4.0x). Clamping to {new_ratio:.2f}x."
                    )
                    stretch_ratio = new_ratio

                import os

                from audiostretchy.stretch import stretch_audio

                # Temporary files for audiostretchy
                temp_input_path = "temp_input.wav"
                temp_output_path = "temp_output.wav"
                audio.export(temp_input_path, format="wav")

                # Apply time stretching
                stretch_audio(temp_input_path, temp_output_path, ratio=stretch_ratio)
                self._logger.info(f"Applied time stretch at {stretch_ratio:.2f}x without pitch change.")

                # Load the stretched audio back into pydub
                modified_audio = AudioSegment.from_file(temp_output_path)

                # Clean up temp files
                os.remove(temp_input_path)
                os.remove(temp_output_path)

                mem_file = BytesIO()
                modified_audio.export(mem_file, format="wav")
                mem_file.seek(0)

                if not pygame.mixer.get_init():
                    self._logger.info("Initializing pygame mixer")
                    # Initialize with the modified audio's properties
                    pygame.mixer.init(frequency=modified_audio.frame_rate, size=-16, channels=modified_audio.channels, buffer=2048)

                pygame.mixer.music.load(mem_file)
                pygame.mixer.music.set_volume(1)
                pygame.mixer.music.play()
                self._is_audio_played = True
                self._logger.info(f"Playing stretched audio: {found_path} at {stretch_ratio:.2f}x ratio.")

            except (pygame.error, CouldntDecodeError) as e:
                self._logger.error(f"Error processing or playing audio {found_path}: {str(e)}")
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

