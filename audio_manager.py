# audio_manager.py

import logging
from pathlib import Path
import time
from typing import Optional
import tempfile
import os
from pydub import AudioSegment


class AudioManager:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        # Folder na pliki generowane (cache/tts)
        self.audio_dir = Path("audio_cache")
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        try:
            import pygame
            # Init z wyższą częstotliwością dla lepszej jakości
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.pygame = pygame
            self.logger.info("Pygame mixer initialized")
        except ImportError:
            self.logger.error("pygame not installed: pip install pygame")
            raise

        try:
            from audiostretchy.stretch import stretch_audio
            self.stretch_available = True
            self.logger.info("Audio stretching with audiostretchy available (High Quality)")
        except ImportError:
            self.stretch_available = False
            self.logger.warning("audiostretchy not installed. Using pydub (Low Quality - Pitch changes).")
            self.logger.warning("To fix: pip install audiostretchy")

    def get_audio(self, text: str, audio_path: Optional[str],
                  target_duration: float) -> Path:
        """
        Pobiera plik audio, dostosowuje jego długość do target_duration
        i zwraca ścieżkę do gotowego pliku.
        """
        source_file = None

        # 1. Próba znalezienia pliku zdefiniowanego w JSON
        if audio_path:
            # Sprawdź czy ścieżka istnieje tak jak podana (np. "audio/1.mp3")
            if Path(audio_path).exists():
                source_file = Path(audio_path)
            # Sprawdź w folderze data (jeśli user tam trzyma)
            elif (Path("data") / audio_path).exists():
                source_file = Path("data") / audio_path
            else:
                self.logger.warning(f"Audio file defined but not found: {audio_path}. Trying TTS.")

        # 2. Jeśli nie znaleziono pliku, generuj TTS
        if not source_file:
            source_file = self._generate_tts(text)

        # 3. Dostosuj czas trwania (jeśli target_duration jest podany)
        final_file = self._adjust_duration(source_file, target_duration)
        return final_file

    def _generate_tts(self, text: str) -> Path:
        try:
            from gtts import gTTS
            # Używamy fragmentu tekstu jako nazwy pliku dla cache
            safe_filename = "".join([c for c in text if c.isalnum()]).rstrip()[:30]
            temp_file = self.audio_dir / f"tts_{safe_filename}.mp3"

            if temp_file.exists():
                return temp_file

            tts = gTTS(text=text, lang='pl', slow=False)
            tts.save(str(temp_file))
            self.logger.info(f"Generated TTS audio: {temp_file}")
            return temp_file
        except ImportError:
            self.logger.warning("gTTS not installed, creating silent audio")
            silence = AudioSegment.silent(duration=3000)
            temp_file = self.audio_dir / "silence_fallback.wav"
            silence.export(str(temp_file), format="wav")
            return temp_file

    def _adjust_duration(self, source_file: Path, target_duration: float) -> Path:
        if not target_duration or target_duration <= 0:
            return source_file

        try:
            audio = AudioSegment.from_file(source_file)
            original_duration = len(audio) / 1000.0

            # Jeśli różnica jest mniejsza niż 0.3s, nie zmieniaj (brzmi naturalniej)
            if abs(original_duration - target_duration) < 0.3:
                self.logger.info(
                    f"Duration match ({original_duration:.2f}s vs {target_duration:.2f}s). Keeping original.")
                return source_file

            # Zabezpieczenie przed ekstremalnym przyspieszaniem (max 3x, min 0.5x)
            ratio = target_duration / original_duration
            if ratio < 0.33: target_duration = original_duration * 0.33
            if ratio > 2.0: target_duration = original_duration * 2.0

            if self.stretch_available:
                return self._time_stretch_audiostretchy(source_file, target_duration)
            else:
                return self._speed_change_pydub(source_file, target_duration)
        except Exception as e:
            self.logger.error(f"Error adjusting duration: {e}. Returning original.")
            return source_file

    def _time_stretch_audiostretchy(self, source_file: Path, target_duration: float) -> Path:
        from audiostretchy.stretch import stretch_audio

        # Nazwa pliku cache zawierająca docelowy czas
        cache_file = self.audio_dir / f"str_{source_file.stem}_{target_duration:.2f}s.wav"
        if cache_file.exists():
            return cache_file

        audio = AudioSegment.from_file(source_file)
        original_duration = len(audio) / 1000.0

        # audiostretchy: ratio < 1 = szybciej (krócej), ratio > 1 = wolniej (dłużej)
        stretch_ratio = target_duration / original_duration

        self.logger.info(
            f"Time-stretching (HQ): {original_duration:.2f}s -> {target_duration:.2f}s (ratio: {stretch_ratio:.2f})")

        temp_input_name = ""
        temp_output_name = ""
        try:
            # audiostretchy wymaga ścieżek do plików, nie obiektów
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_in, \
                    tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_out:
                temp_input_name = temp_in.name
                temp_output_name = temp_out.name

            # Eksport do tymczasowego wav
            audio.export(temp_input_name, format='wav')

            # Przetwarzanie
            stretch_audio(temp_input_name, temp_output_name, ratio=stretch_ratio)

            # Zapis do cache
            processed = AudioSegment.from_file(temp_output_name)
            processed.export(str(cache_file), format='wav')

            return cache_file
        except Exception as e:
            self.logger.error(f"audiostretchy failed: {e}, falling back to pydub")
            return self._speed_change_pydub(source_file, target_duration)
        finally:
            # Sprzątanie
            if temp_input_name and os.path.exists(temp_input_name): os.unlink(temp_input_name)
            if temp_output_name and os.path.exists(temp_output_name): os.unlink(temp_output_name)

    def _speed_change_pydub(self, source_file: Path, target_duration: float) -> Path:
        """Zmienia prędkość zmieniając frame_rate (zmienia tonację - efekt wiewiórki)."""
        cache_file = self.audio_dir / f"speed_{source_file.stem}_{target_duration:.2f}s.wav"
        if cache_file.exists():
            return cache_file

        audio = AudioSegment.from_file(source_file)
        original_duration = len(audio) / 1000.0

        # Pydub: speed_factor > 1 = szybciej
        speed_factor = original_duration / target_duration

        self.logger.warning(
            f"Speed changing (LQ): {original_duration:.2f}s -> {target_duration:.2f}s (factor: {speed_factor:.2f}x)")

        new_frame_rate = int(audio.frame_rate * speed_factor)
        modified_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": new_frame_rate
        })
        # Reset frame rate to standard so player handles it correctly
        modified_audio = modified_audio.set_frame_rate(44100)

        modified_audio.export(str(cache_file), format='wav')
        return cache_file

    def start_playing(self, audio_file: Path):
        try:
            if not audio_file or not audio_file.exists():
                self.logger.error(f"Cannot play: File not found {audio_file}")
                return

            if self.pygame.mixer.music.get_busy():
                self.pygame.mixer.music.stop()

            self.pygame.mixer.music.load(str(audio_file))
            self.pygame.mixer.music.play()
            self.logger.info(f"Started playing: {audio_file.name}")
        except Exception as e:
            self.logger.error(f"Error starting audio: {e}")

    def is_playing(self) -> bool:
        if not self.pygame.mixer.get_init():
            return False
        return self.pygame.mixer.music.get_busy()

    def stop(self):
        if self.pygame.mixer.get_init():
            self.pygame.mixer.music.stop()