# experiment_config.py
# Wszystkie konfigurowalne parametry eksperymentu EEG2Text (single-word paradigm)

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExperimentConfig:
    """Konfiguracja eksperymentu EEG2Text - paradigm single-word."""

    # === SŁOWA ===
    n_words: int = 100  # Ile unikalnych słów na sesję (N)
    k_repeats: int = 20  # Ile razy każde słowo się powtarza (K)

    # === PODEJŚCIE ===
    # approach1: słowo na ekranie → czytanie w myślach → spacja
    # approach2: słowo na ekranie → znika → beepy → mówienie w myślach (domyślne)
    approach: int = 2

    # === TIMINGI (w sekundach) ===
    # Podejście 1
    word_display_time_approach1: float = (
        1.5  # Jak długo słowo widoczne (approach1, 0 = czekaj na spację)
    )

    # Podejście 2
    word_display_time: float = 1.5  # Jak długo słowo widoczne przed zniknięciem
    n_beeps: int = 4  # Ile beepów na jedno słowo
    beep_interval: float = 2.5  # Odstęp między beepami (czas na powiedzenie w myślach)
    pre_beep_delay: float = 0.5  # Pauza między zniknięciem słowa a pierwszym beepem

    # Ogólne
    fixation_min_ms: int = 400  # Min czas fixation cross
    fixation_max_ms: int = 600  # Max czas fixation cross
    post_trial_blank_ms: int = 500  # Blank screen po każdym trialu
    inter_word_blank_ms: int = (
        300  # Blank między zniknięciem słowa a beepami (approach2)
    )

    # === PRZERWY ===
    break_every_n_trials: int = 50  # Przerwa co N trialli
    break_duration_ms: int = 60000  # Długość przerwy (60s)

    # === ZDANIA TESTOWE ===
    m_sentences: int = 20  # Ile zdań testowych na koniec
    sentence_display_mode: str = (
        "rsvp"  # "rsvp" (słowo po słowie) lub "full" (całe zdanie)
    )
    rsvp_word_duration: float = 1.5  # Czas wyświetlania jednego słowa w RSVP
    rsvp_post_sentence_blank: float = 0.5  # Blank po ostatnim słowie zdania w RSVP
    full_sentence_wait_for_space: bool = True  # Czy czekać na spację w trybie full

    # === PLIKI ===
    words_file: str = "zdania.txt"  # Plik ze zdaniami/słowami (sekcja słów na dole)
    sentences_file: str = "zdania.txt"  # Plik ze zdaniami testowymi

    # === BEEP AUDIO ===
    beep_frequency: int = 800  # Częstotliwość beep w Hz
    beep_duration_ms: int = 100  # Długość beep w ms

    @property
    def total_word_trials(self) -> int:
        """Łączna liczba trialli słownych."""
        return self.n_words * self.k_repeats

    def estimated_duration_minutes(self) -> float:
        """Przybliżony czas trwania sesji w minutach."""
        if self.approach == 1:
            # ~2s per trial (display + response)
            word_time = self.total_word_trials * 2.0
        else:
            # display + delay + beeps * interval
            trial_time = (
                self.word_display_time
                + self.pre_beep_delay
                + (self.n_beeps * self.beep_interval)
            )
            word_time = self.total_word_trials * trial_time

        # Przerwy
        n_breaks = self.total_word_trials // self.break_every_n_trials
        break_time = n_breaks * (self.break_duration_ms / 1000.0)

        # Zdania testowe (~10s per sentence)
        sentence_time = self.m_sentences * 10.0

        total_seconds = word_time + break_time + sentence_time
        return total_seconds / 60.0
