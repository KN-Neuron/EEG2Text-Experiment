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
        self.audio_dir = Path("src/assets/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.pygame = pygame
            self.logger.info("Pygame mixer initialized")
        except ImportError:
            self.logger.error("pygame not installed: pip install pygame")
            raise
        try:
            from audiostretchy.stretch import stretch_audio
            self.stretch_available = True
            self.logger.info("Audio stretching with audiostretchy available")
        except ImportError:
            self.stretch_available = False
            self.logger.warning("audiostretchy not installed, using pydub speed change (changes pitch)")
            self.logger.warning("Install audiostretchy for pitch-preserving stretch: pip install audiostretchy")

    def get_audio(self, text: str, audio_path: Optional[str],
                  target_duration: float) -> Path:
        if audio_path:
            audio_filename = Path(audio_path).name
            source_file = self.audio_dir / audio_filename
            if not source_file.exists():
                self.logger.error(f"Audio file not found: {source_file}, generating TTS.")
                source_file = self._generate_tts(text)
        else:
            source_file = self._generate_tts(text)
        
        stretched_file = self._adjust_duration(source_file, target_duration)
        return stretched_file

    def _generate_tts(self, text: str) -> Path:
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='pl', slow=False)
            safe_filename = "".join([c for c in text if c.isalpha() or c.isdigit()]).rstrip()[:50]
            temp_file = self.audio_dir / f"tts_{safe_filename}_{abs(hash(text)) % 10000}.mp3"
            tts.save(str(temp_file))
            self.logger.info(f"Generated TTS audio: {temp_file}")
            return temp_file
        except ImportError:
            self.logger.warning("gTTS not installed, creating silent audio")
            silence = AudioSegment.silent(duration=3000)
            temp_file = self.audio_dir / f"silent_{abs(hash(text)) % 10000}.wav"
            silence.export(str(temp_file), format="wav")
            return temp_file

    def _adjust_duration(self, source_file: Path, target_duration: float) -> Path:
        audio = AudioSegment.from_file(source_file)
        original_duration = len(audio) / 1000.0
        
        if target_duration <= 0:
            self.logger.warning(f"Invalid target duration {target_duration:.2f}s. Using original.")
            return source_file

        if abs(original_duration - target_duration) < 0.5:
            self.logger.info(f"Duration close enough: {original_duration:.2f}s vs {target_duration:.2f}s. Using original.")
            return source_file
            
        if self.stretch_available:
            return self._time_stretch_audiostretchy(source_file, target_duration)
        else:
            return self._speed_change_pydub(source_file, target_duration)

    def _time_stretch_audiostretchy(self, source_file: Path, target_duration: float) -> Path:
        from audiostretchy.stretch import stretch_audio
        audio = AudioSegment.from_file(source_file)
        original_duration = len(audio) / 1000.0
        
        # FIX: The ratio needs to be inverted for audiostretchy
        # For audiostretchy, ratio < 1 makes audio faster, ratio > 1 makes it slower
        stretch_ratio = target_duration / original_duration
        
        self.logger.info(
            f"Time-stretching with audiostretchy: {original_duration:.2f}s -> {target_duration:.2f}s "
            f"(ratio: {stretch_ratio:.2f})"
        )
        
        cache_file = self.audio_dir / f"stretched_{source_file.stem}_{target_duration:.1f}s.wav"
        if cache_file.exists():
            self.logger.info(f"Found cached stretched file: {cache_file}")
            return cache_file
        
        temp_input_name = ""
        temp_output_name = ""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_input, \
                 tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_output:
                temp_input_name = temp_input.name
                temp_output_name = temp_output.name

            audio.export(temp_input_name, format='wav')
            
            # Use the corrected ratio for the stretch_audio function
            stretch_audio(temp_input_name, temp_output_name, ratio=stretch_ratio)
            
            stretched = AudioSegment.from_file(temp_output_name)
            stretched.export(str(cache_file), format='wav')
            self.logger.info(f"Successfully stretched audio to {cache_file}")
            return cache_file
        except Exception as e:
            self.logger.error(f"audiostretchy failed: {e}, falling back to pydub speed change")
            return self._speed_change_pydub(source_file, target_duration)
        finally:
            if temp_input_name and os.path.exists(temp_input_name):
                os.unlink(temp_input_name)
            if temp_output_name and os.path.exists(temp_output_name):
                os.unlink(temp_output_name)

    def _speed_change_pydub(self, source_file: Path, target_duration: float) -> Path:
        audio = AudioSegment.from_file(source_file)
        original_duration = len(audio) / 1000.0
        
        # For pydub speed change, this ratio is correct
        # Higher speed_factor = faster audio
        speed_factor = original_duration / target_duration
        
        self.logger.warning(
            f"Speed changing with pydub (pitch will change): {original_duration:.2f}s -> {target_duration:.2f}s "
            f"(speed: {speed_factor:.2f}x)"
        )
        
        cache_file = self.audio_dir / f"speed_{source_file.stem}_{target_duration:.1f}s.wav"
        if cache_file.exists():
            self.logger.info(f"Found cached speed-changed file: {cache_file}")
            return cache_file

        modified_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed_factor)
        }).set_frame_rate(audio.frame_rate)
        
        modified_audio.export(str(cache_file), format='wav')
        self.logger.info(f"Successfully speed-changed audio to {cache_file}")
        return cache_file

    def start_playing(self, audio_file: Path):
        try:
            self.pygame.mixer.music.load(str(audio_file))
            self.pygame.mixer.music.play()
            self.logger.info(f"Started playing: {audio_file.name}")
        except Exception as e:
            self.logger.error(f"Error starting audio: {e}")
            raise

    def play_audio_blocking(self, audio_file: Path):
        self.start_playing(audio_file)
        while self.is_playing():
            time.sleep(0.1)
        self.logger.info(f"Finished playing: {audio_file.name}")

    def is_playing(self) -> bool:
        if not self.pygame.mixer.get_init():
            return False
        return self.pygame.mixer.music.get_busy()

    def stop(self):
        if self.pygame.mixer.get_init():
            self.pygame.mixer.music.stop()
            self.logger.info("Audio stopped.")