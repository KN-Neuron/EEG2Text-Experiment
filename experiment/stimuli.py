# stimuli.py - WERSJA POPRAWIONA z kategorią WYOBRAŹNIA

import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import logging


@dataclass
class Sentence:
    text: str
    category: str
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer_index: Optional[int] = None
    audio_path: Optional[str] = None


class StimulusManager:
    def __init__(self, logger: logging.Logger, debug_mode: bool = False):
        self.logger = logger
        self.debug_mode = debug_mode
        self.assets_dir = Path("src/assets")
        self.assets_dir.mkdir(exist_ok=True)

        # Wczytuje wszystkie kategorie zdań
        self.all_sentences = {
            'normal': self._load_sentences('normal_sentences.json', 'normal'),
            'imagination': self._load_sentences('sentiment_sentences.json', 'imagination'),
        }

        # Tworzy kategorię 'listening' bazując na zdaniach 'normal'
        self.all_sentences['listening'] = [
            Sentence(
                text=s.text,
                category='listening',
                audio_path=s.audio_path
            )
            for s in self.all_sentences['normal']
        ]

        # Tasuje wszystkie kategorie
        for category in self.all_sentences:
            random.shuffle(self.all_sentences[category])

        self.current_index = {
            'normal': 0,
            'imagination': 0,
            'listening': 0
        }
        self.used_sentences: List[Sentence] = []
        self.presented_normal_sentences: List[Sentence] = []

        self.logger.info(f"Loaded stimuli:")
        for cat, sentences in self.all_sentences.items():
            self.logger.info(f"  {cat}: {len(sentences)} sentences")

    def _load_sentences(self, filename: str, category: str) -> List[Sentence]:
        filepath = self.assets_dir / filename
        if not filepath.exists():
            self.logger.warning(f"File not found: {filepath}, creating example file")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Sentence(category=category, **item) for item in data]
        except (json.JSONDecodeError, TypeError) as e:
            self.logger.error(f"Error loading or parsing {filepath}: {e}")
            self._create_example_file(filepath, category)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Sentence(category=category, **item) for item in data]

    def get_sentences(self, category: str, count: int,
                      is_trial: bool = False) -> List[Sentence]:
        available = self.all_sentences.get(category, [])
        if not available:
            self.logger.error(f"No sentences available for category: {category}")
            return []

        if is_trial:
            return available[:count]

        start_idx = self.current_index[category]
        end_idx = start_idx + count

        if end_idx > len(available):
            self.logger.warning(f"Not enough unique {category} sentences, wrapping around.")
            random.shuffle(available)
            start_idx = 0
            end_idx = count
            self.current_index[category] = 0

        sentences = available[start_idx:end_idx]
        self.current_index[category] = end_idx

        if not is_trial:
            self.used_sentences.extend(sentences)
            if category == 'normal':
                self.presented_normal_sentences.extend(sentences)

        return sentences

    def get_sentences_for_listening(self, count: int) -> List[Sentence]:
        if not self.presented_normal_sentences:
            self.logger.warning(
                "No sentences from 'normal' block have been presented yet. Using random listening sentences.")
            return self.get_sentences('listening', count)

        num_to_sample = min(count, len(self.presented_normal_sentences))
        sampled_sentences = random.sample(self.presented_normal_sentences, num_to_sample)

        return [
            Sentence(text=s.text, category='listening', audio_path=s.audio_path)
            for s in sampled_sentences
        ]

    def get_memory_sentences(self, count: int) -> List[Sentence]:
        if not self.used_sentences:
            return []

        unique_used_sentences = list({s.text: s for s in self.used_sentences}.values())
        num_to_sample = min(count, len(unique_used_sentences))
        return random.sample(unique_used_sentences, num_to_sample)