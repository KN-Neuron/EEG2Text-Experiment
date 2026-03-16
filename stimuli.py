# stimuli.py - Wersja dla single-word paradigm
# Ładuje słowa i zdania z pliku zdania.txt

import logging
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class WordTrial:
    """Pojedynczy trial słowny."""

    word: str
    word_index: int  # Indeks słowa w liście unikalnych słów
    repetition: int  # Która to powtórka (1..K)
    trial_index: int = 0  # Globalny indeks trialu (ustawiany po shuffle)


@dataclass
class SentenceTrial:
    """Pojedynczy trial zdaniowy (test)."""

    sentence: str
    words: List[str]
    sentence_index: int


class StimulusManager:
    """Zarządza słowami i zdaniami dla eksperymentu EEG2Text."""

    def __init__(
        self,
        logger: logging.Logger,
        words_file: str = "zdania.txt",
        sentences_file: str = "zdania.txt",
    ):
        self.logger = logger
        self.words_file = Path(words_file)
        self.sentences_file = Path(sentences_file)

        self.all_words: List[str] = []
        self.all_sentences: List[str] = []

        self._load_data()

    def _load_data(self):
        """Ładuje słowa i zdania z pliku zdania.txt."""
        if not self.words_file.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku: {self.words_file}")

        content = self.words_file.read_text(encoding="utf-8")

        self.all_sentences = self._parse_sentences(content)
        self.logger.info(
            f"Załadowano {len(self.all_sentences)} zdań z {self.words_file}"
        )

        self.all_words = self._parse_words(content)
        self.logger.info(f"Załadowano {len(self.all_words)} słów z {self.words_file}")

    def _parse_sentences(self, content: str) -> List[str]:
        """Parsuje zdania z pliku (format: '  1. Mama daje kwiat tu.')"""
        sentences = []
        in_sentences = False

        for line in content.split("\n"):
            line = line.strip()

            if "PROSTYCH ZDAŃ" in line or "ZDAŃ W JĘZYKU" in line:
                in_sentences = True
                continue

            if "LISTA UŻYTYCH SŁÓW" in line:
                break

            if line.startswith("===") or not line:
                continue

            if in_sentences:
                match = re.match(r"\d+\.\s+(.+)", line)
                if match:
                    sentences.append(match.group(1).strip())

        return sentences

    def _parse_words(self, content: str) -> List[str]:
        """Parsuje listę słów z pliku (format: '  1. ale')"""
        words = []
        in_words = False

        for line in content.split("\n"):
            line = line.strip()

            if "LISTA UŻYTYCH SŁÓW" in line:
                in_words = True
                continue

            if in_words:
                if line.startswith("===") or not line or line.startswith("✓"):
                    continue

                match = re.match(r"\d+\.\s+(.+)", line)
                if match:
                    words.append(match.group(1).strip())

        return words

    def get_word_trials(self, n_words: int, k_repeats: int) -> List[WordTrial]:
        """
        Generuje listę trialli słownych.

        Args:
            n_words: Ile unikalnych słów (max len(self.all_words))
            k_repeats: Ile powtórzeń każdego słowa

        Returns:
            Zshufflowana lista WordTrial (N * K elementów)
        """
        n_words = min(n_words, len(self.all_words))

        selected_words = random.sample(self.all_words, n_words)
        self.logger.info(
            f"Wybrano {n_words} słów, {k_repeats} powtórzeń = {n_words * k_repeats} trialli"
        )

        trials = []
        for word_idx, word in enumerate(selected_words):
            for rep in range(1, k_repeats + 1):
                trials.append(WordTrial(word=word, word_index=word_idx, repetition=rep))

        random.shuffle(trials)

        for i, trial in enumerate(trials):
            trial.trial_index = i

        self.logger.info(
            f"Wygenerowano {len(trials)} trialli słownych (zshufflowanych)"
        )
        return trials

    def get_sentence_trials(
        self, m_sentences: int, used_words: Optional[List[str]] = None
    ) -> List[SentenceTrial]:
        """
        Losuje M zdań testowych.

        Args:
            m_sentences: Ile zdań
            used_words: Opcjonalnie filtruj zdania zawierające te słowa

        Returns:
            Lista SentenceTrial
        """
        available = self.all_sentences.copy()

        if used_words:
            used_set = set(w.lower() for w in used_words)
            filtered = [
                s
                for s in available
                if any(w.lower() in used_set for w in s.replace(".", "").split())
            ]
            if len(filtered) >= m_sentences:
                available = filtered
                self.logger.info(
                    f"Przefiltrowano do {len(available)} zdań zawierających słowa z sesji"
                )

        m_sentences = min(m_sentences, len(available))
        selected = random.sample(available, m_sentences)

        trials = []
        for i, sentence in enumerate(selected):
            words = sentence.replace(".", "").split()
            trials.append(
                SentenceTrial(sentence=sentence, words=words, sentence_index=i)
            )

        self.logger.info(f"Wygenerowano {len(trials)} zdań testowych")
        return trials

