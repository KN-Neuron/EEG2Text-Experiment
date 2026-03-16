# gui.py - Pygame GUI for single-word EEG2Text paradigm
#
# Fullscreen, minimalistyczne GUI oparte na Pygame.
# Obsługuje: wyświetlanie słów, beepy, RSVP zdań, przerwy, instrukcje.

from __future__ import annotations

import logging
import math
import struct
import time
import wave
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pygame


class ExperimentGUI:
    def __init__(self, logger: logging.Logger, debug_mode: bool = False):
        self.logger = logger
        self.debug_mode = debug_mode

        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        # Fullscreen
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h

        if debug_mode:
            # Windowed w debug
            self.screen_width = 1280
            self.screen_height = 800
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height)
            )
        else:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.FULLSCREEN
            )
            pygame.mouse.set_visible(False)

        pygame.display.set_caption(
            "EEG2Text Experiment" + (" [DEBUG]" if debug_mode else "")
        )

        self.logger.info(f"Screen: {self.screen_width}x{self.screen_height}")

        # Kolory
        self.BG = (211, 211, 211)           # #D3D3D3 — szare tło
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.DARK_TEXT = (44, 62, 80)        # #2C3E50
        self.GRAY_TEXT = (85, 85, 85)        # #555555
        self.LIGHT_GRAY = (153, 153, 153)    # #999999
        self.GREEN = (46, 125, 50)           # #2E7D32
        self.DOT_INACTIVE = (204, 204, 204)  # #CCCCCC
        self.DOT_ACTIVE = (46, 125, 50)

        # Skalowanie czcionek
        base = min(self.screen_width, self.screen_height) // 25
        self.base_font_size = base

        self.font_word = pygame.font.SysFont('Arial', base * 3, bold=True)
        self.font_sentence = pygame.font.SysFont('Arial', base, bold=True)
        self.font_instruction = pygame.font.SysFont('Arial', int(base * 0.85), bold=True)
        self.font_small = pygame.font.SysFont('Arial', int(base * 0.7))
        self.font_fixation = pygame.font.SysFont('Arial', base * 4, bold=True)
        self.font_countdown = pygame.font.SysFont('Arial', base * 2, bold=True)
        self.font_progress = pygame.font.SysFont('Arial', int(base * 0.5))
        self.font_title = pygame.font.SysFont('Arial', base + 7, bold=True)

        # Beep sound (generowany w pamięci)
        self._beep_cache = {}

        self.clock = pygame.time.Clock()
        self.running = True

    # ──────────── BEEP ────────────

    def _get_beep_sound(self, frequency: int = 800, duration_ms: int = 100):
        """Generuje beep jako pygame.mixer.Sound (cache)."""
        key = (frequency, duration_ms)
        if key in self._beep_cache:
            return self._beep_cache[key]

        sample_rate = 44100
        n_samples = int(sample_rate * duration_ms / 1000.0)
        amplitude = 0.3

        # Stereo buffer (2 kanały)
        buf = np.zeros((n_samples, 2), dtype=np.int16)

        for i in range(n_samples):
            t = i / sample_rate
            # Envelope
            fade = int(sample_rate * 0.01)
            if i < fade:
                env = i / fade
            elif i > n_samples - fade:
                env = (n_samples - i) / fade
            else:
                env = 1.0
            val = int(amplitude * env * math.sin(2 * math.pi * frequency * t) * 32767)
            buf[i][0] = val
            buf[i][1] = val

        sound = pygame.sndarray.make_sound(buf)
        self._beep_cache[key] = sound
        return sound

    def play_beep(self, frequency: int = 800, duration_ms: int = 100):
        """Odtwarza beep."""
        try:
            sound = self._get_beep_sound(frequency, duration_ms)
            sound.play()
        except Exception as e:
            self.logger.error(f"Beep error: {e}")

    # ──────────── EVENT HANDLING ────────────

    def _pump_events(self):
        """Przetwarza eventy — wykrywa quit/escape."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                raise KeyboardInterrupt("Window closed")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                raise KeyboardInterrupt("Escape pressed")

    def _wait_for_key(self, keys: List[int]) -> int:
        """Czeka na jedno z podanych klawiszy. Zwraca naciśnięty klawisz."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    raise KeyboardInterrupt("Window closed")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        raise KeyboardInterrupt("Escape pressed")
                    if event.key in keys:
                        return event.key
            self.clock.tick(60)
        return -1

    def wait_for_space(self):
        """Czeka na spację."""
        self._wait_for_key([pygame.K_SPACE])

    def _wait_ms(self, duration_ms: int):
        """Czeka podaną liczbę ms, przetwarzając eventy."""
        end_time = pygame.time.get_ticks() + duration_ms
        while pygame.time.get_ticks() < end_time:
            self._pump_events()
            self.clock.tick(60)

    # ──────────── RENDERING HELPERS ────────────

    def _fill_bg(self, color: Optional[Tuple[int, int, int]] = None):
        """Wypełnia ekran kolorem tła."""
        self.screen.fill(color or self.BG)

    def _draw_text_centered(self, text: str, font: pygame.font.Font,
                            color: Tuple[int, int, int], y: Optional[int] = None,
                            max_width: Optional[int] = None):
        """Rysuje tekst wycentrowany. Obsługuje wieloliniowy tekst i zawijanie."""
        if max_width is None:
            max_width = int(self.screen_width * 0.85)

        lines = self._wrap_text(text, font, max_width)
        total_height = len(lines) * font.get_linesize()

        if y is None:
            start_y = (self.screen_height - total_height) // 2
        else:
            start_y = y - total_height // 2

        for i, line in enumerate(lines):
            surf = font.render(line, True, color)
            rect = surf.get_rect(centerx=self.screen_width // 2,
                                 top=start_y + i * font.get_linesize())
            self.screen.blit(surf, rect)

    def _wrap_text(self, text: str, font: pygame.font.Font,
                   max_width: int) -> List[str]:
        """Łamie tekst na linie pasujące do max_width. Obsługuje \\n."""
        result = []
        for paragraph in text.split('\n'):
            if not paragraph.strip():
                result.append('')
                continue
            words = paragraph.split()
            if not words:
                result.append('')
                continue
            current_line = words[0]
            for word in words[1:]:
                test = current_line + ' ' + word
                if font.size(test)[0] <= max_width:
                    current_line = test
                else:
                    result.append(current_line)
                    current_line = word
            result.append(current_line)
        return result

    def _draw_progress(self, text: str):
        """Rysuje tekst postępu w prawym dolnym rogu."""
        surf = self.font_progress.render(text, True, self.LIGHT_GRAY)
        rect = surf.get_rect(bottomright=(self.screen_width - 20, self.screen_height - 20))
        self.screen.blit(surf, rect)

    # ──────────── EKRANY ────────────

    def show_welcome(self):
        self._fill_bg()
        self._draw_text_centered(
            "Witaj w badaniu EEG2Text\n\nNaciśnij SPACJĘ by rozpocząć",
            self.font_instruction, self.BLACK
        )
        pygame.display.flip()
        self.wait_for_space()

    def show_colored_instruction(self, title: str, text: str,
                                 color: Tuple[int, int, int] = (232, 244, 248)):
        self._fill_bg(color)

        # Tytuł na górze
        title_y = self.screen_height // 8
        self._draw_text_centered(title, self.font_title, self.DARK_TEXT, y=title_y)

        # Treść na środku
        self._draw_text_centered(text, self.font_instruction, self.BLACK)

        # Podpis na dole
        bottom_y = self.screen_height - 60
        self._draw_text_centered(
            "Naciśnij SPACJĘ by kontynuować",
            self.font_small, self.GRAY_TEXT, y=bottom_y
        )

        pygame.display.flip()
        self.wait_for_space()

    def show_fixation(self, duration_ms: int):
        self._fill_bg()
        self._draw_text_centered("+", self.font_fixation, self.BLACK)
        pygame.display.flip()
        self._wait_ms(duration_ms)

    def show_blank(self, duration_ms: int):
        self._fill_bg()
        pygame.display.flip()
        self._wait_ms(duration_ms)

    # ──────────── SŁOWA ────────────

    def show_word(self, word: str, progress_text: Optional[str] = None):
        """Wyświetla pojedyncze słowo na środku ekranu."""
        self._fill_bg()
        self._draw_text_centered(word, self.font_word, self.BLACK)
        if progress_text:
            self._draw_progress(progress_text)
        pygame.display.flip()

    def show_word_timed(self, word: str, duration_ms: int,
                        progress_text: Optional[str] = None):
        """Wyświetla słowo na określony czas."""
        self.show_word(word, progress_text)
        self._wait_ms(duration_ms)

    def show_word_wait_space(self, word: str, progress_text: Optional[str] = None):
        """Wyświetla słowo i czeka na spację."""
        self.show_word(word, progress_text)
        self.wait_for_space()

    def show_beep_indicator(self, beep_number: int, total_beeps: int):
        """Pusty ekran z kropką fixation + postęp beepów."""
        self._fill_bg()

        cx, cy = self.screen_width // 2, self.screen_height // 2

        # Mała kropka fixation
        dot_surf = self.font_countdown.render("·", True, (136, 136, 136))
        dot_rect = dot_surf.get_rect(center=(cx, cy))
        self.screen.blit(dot_surf, dot_rect)

        # Kropki postępu beepów na dole
        dot_y = self.screen_height - 60
        dot_spacing = 30
        total_width = (total_beeps - 1) * dot_spacing
        start_x = cx - total_width // 2

        for i in range(total_beeps):
            x = start_x + i * dot_spacing
            if i < beep_number:
                pygame.draw.circle(self.screen, self.DOT_ACTIVE, (x, dot_y), 8)
            else:
                pygame.draw.circle(self.screen, self.DOT_INACTIVE, (x, dot_y), 5)

        pygame.display.flip()

    # ──────────── ZDANIA ────────────

    def show_sentence_rsvp(self, words: List[str], word_duration_ms: int,
                           progress_text: Optional[str] = None):
        """Wyświetla zdanie słowo po słowie (RSVP)."""
        for word in words:
            self._fill_bg()
            self._draw_text_centered(word, self.font_sentence, self.BLACK)
            if progress_text:
                self._draw_progress(progress_text)
            pygame.display.flip()
            self._wait_ms(word_duration_ms)

    def show_sentence_full(self, sentence: str, progress_text: Optional[str] = None):
        """Wyświetla całe zdanie i czeka na spację."""
        self._fill_bg()
        self._draw_text_centered(sentence, self.font_sentence, self.BLACK)
        if progress_text:
            self._draw_progress(progress_text)
        pygame.display.flip()
        self.wait_for_space()

    # ──────────── PRZERWY / ZAKOŃCZENIE ────────────

    def show_rest(self, duration_ms: int):
        end_time = time.time() + duration_ms / 1000.0

        while time.time() < end_time:
            seconds_left = max(0, int(round(end_time - time.time())))

            self._fill_bg()
            self._draw_text_centered(
                f"Czas na odpoczynek\n\n{seconds_left} sekund pozostało\n\n"
                f"Zrelaksuj się, możesz pomrugać...",
                self.font_instruction, self.BLACK
            )
            pygame.display.flip()

            # Czekaj ~500ms ale przetwarzaj eventy
            wait_end = pygame.time.get_ticks() + 500
            while pygame.time.get_ticks() < wait_end:
                self._pump_events()
                self.clock.tick(60)

        # "Przygotuj się"
        self._fill_bg()
        self._draw_text_centered(
            "Przygotuj się...\n\nNastępna część zaraz się rozpocznie",
            self.font_instruction, self.BLACK
        )
        pygame.display.flip()
        self._wait_ms(2000)

    def show_completion(self):
        self._fill_bg((232, 245, 233))  # Jasny zielony

        self._draw_text_centered(
            "EKSPERYMENT ZAKOŃCZONY!",
            self.font_title, self.GREEN,
            y=self.screen_height // 2 - 50
        )
        self._draw_text_centered(
            "Dziękujemy za Twój udział!\n\nDane EEG zostały zapisane.\n\n"
            "Naciśnij SPACJĘ by wyjść.",
            self.font_instruction, self.BLACK,
            y=self.screen_height // 2 + 80
        )
        pygame.display.flip()
        self.wait_for_space()

    def show_message(self, text: str, duration_ms: Optional[int] = None):
        self._fill_bg()
        self._draw_text_centered(text, self.font_instruction, self.BLACK)
        pygame.display.flip()
        if duration_ms:
            self._wait_ms(duration_ms)
        else:
            self.wait_for_space()

    # ──────────── CLEANUP ────────────

    def close(self):
        try:
            pygame.mixer.quit()
            pygame.quit()
        except Exception:
            pass
