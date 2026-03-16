# experiment.py - Single-word EEG2Text paradigm
#
# Podejście 1 (--approach1): słowo na ekranie → czytanie w myślach → spacja
# Podejście 2 (--approach2): słowo na ekranie → znika → beepy → mówienie w myślach
#
# Struktura sesji:
#   1. Instrukcje + trening (kilka słów)
#   2. Faza słów: N słów * K powtórzeń, zshufflowane, przerwy co X trialli
#   3. Faza zdań testowych: M zdań (RSVP lub full)

import dataclasses
import json
import logging
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from experiment_config import ExperimentConfig
from gui import ExperimentGUI
from stimuli import SentenceTrial, StimulusManager, WordTrial


# --- MOCK EEG HEADSET ---
class MockEEGHeadset:
    def __init__(self, logger):
        self.logger = logger
        self.recording = False

    def connect(self):
        self.logger.info("[MOCK EEG] Connected")
        return True

    def start_recording(self, filepath):
        self.recording = True
        self.logger.info(f"[MOCK EEG] Started recording: {filepath}")
        return True

    def stop_recording(self):
        self.recording = False
        self.logger.info("[MOCK EEG] Stopped recording")
        return True

    def annotate(self, annotation):
        self.logger.info(f"[MOCK EEG] Annotation: {annotation}")

    def disconnect(self):
        self.logger.info("[MOCK EEG] Disconnected")

    def is_recording(self):
        return self.recording


class EEG2TextExperiment:
    def __init__(self, participant_id: str, logger: logging.Logger,
                 config: ExperimentConfig,
                 debug_mode: bool = False, use_mock_eeg: bool = False):
        self.participant_id = participant_id
        self.logger = logger
        self.config = config
        self.debug_mode = debug_mode
        self.use_mock_eeg = use_mock_eeg or '--mock-eeg' in sys.argv

        self.data_dir = Path("data") / participant_id
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.gui = ExperimentGUI(logger, debug_mode)
        self.stimuli = StimulusManager(
            logger,
            words_file=config.words_file,
            sentences_file=config.sentences_file
        )

        self.trial_data: List[Dict] = []
        self.eeg = None
        self.is_cleaned_up = False

        # Info o sesji
        est_time = config.estimated_duration_minutes()
        self.logger.info(f"=== KONFIGURACJA SESJI ===")
        self.logger.info(f"Podejście: {config.approach}")
        self.logger.info(f"Słowa: {config.n_words} x {config.k_repeats} = {config.total_word_trials} trialli")
        self.logger.info(f"Zdania testowe: {config.m_sentences} ({config.sentence_display_mode})")
        self.logger.info(f"Przerwy co: {config.break_every_n_trials} trialli")
        self.logger.info(f"Szacowany czas: {est_time:.1f} min")
        if config.approach == 2:
            self.logger.info(f"Beepy: {config.n_beeps} x co {config.beep_interval}s")
            self.logger.info(f"Słowo widoczne: {config.word_display_time}s")
        self.logger.info(f"==========================")

        self.initialize_eeg()

    def initialize_eeg(self):
        if self.use_mock_eeg:
            self.logger.info("Using MOCK EEG headset.")
            self.eeg = MockEEGHeadset(self.logger)
            self.eeg.connect()
            return

        try:
            from eeg_headset import EEGHeadset
            self.logger.info("Initializing BrainAccess via EEGHeadset class...")
            self.eeg = EEGHeadset(participant_id=self.participant_id, logger=self.logger)
            if not self.eeg.connect():
                raise RuntimeError("EEGHeadset.connect() failed.")
            self.logger.info("BrainAccess initialized successfully!")
        except (ImportError, RuntimeError) as e:
            self.logger.error(f"Failed to initialize real EEG: {e}")
            if self.debug_mode:
                self.logger.warning("DEBUG: Falling back to MOCK EEG.")
                self.eeg = MockEEGHeadset(self.logger)
                self.eeg.connect()
            else:
                raise

    def run(self):
        try:
            # === WELCOME ===
            self.gui.show_welcome()

            # === START EEG RECORDING ===
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            eeg_path = self.data_dir / f"{self.participant_id}_eeg_{timestamp_str}.fif"
            self.eeg.start_recording(str(eeg_path))
            self.eeg.annotate("EXPERIMENT_START")
            self.eeg.annotate(f"APPROACH_{self.config.approach}")

            # === INSTRUKCJE ===
            self._show_instructions()

            # === TRENING ===
            self._run_practice()

            # === FAZA 1: SŁOWA ===
            word_trials = self.stimuli.get_word_trials(
                self.config.n_words, self.config.k_repeats
            )
            used_words = list(set(t.word for t in word_trials))

            self.eeg.annotate("PHASE_WORDS_START")
            self._run_word_phase(word_trials)
            self.eeg.annotate("PHASE_WORDS_END")

            # === PRZERWA PRZED ZDANIAMI ===
            self.gui.show_rest(duration_ms=30000)

            # === FAZA 2: ZDANIA TESTOWE ===
            sentence_trials = self.stimuli.get_sentence_trials(
                self.config.m_sentences, used_words=used_words
            )

            self._show_sentence_instructions()

            self.eeg.annotate("PHASE_SENTENCES_START")
            self._run_sentence_phase(sentence_trials)
            self.eeg.annotate("PHASE_SENTENCES_END")

            # === KONIEC ===
            self.eeg.annotate("EXPERIMENT_END")
            self.save_data()
            self.gui.show_completion()

        except Exception as e:
            self.logger.error(f"Critical error: {e}", exc_info=True)
            raise
        finally:
            self.cleanup()

    # === INSTRUKCJE ===

    def _show_instructions(self):
        if self.config.approach == 1:
            self.gui.show_colored_instruction(
                "INSTRUKCJA",
                "W tym badaniu będziesz widział(a) na ekranie pojedyncze słowa.\n\n"
                "Twoim zadaniem jest:\n"
                "1. Przeczytać słowo w myślach\n"
                "2. Nacisnąć SPACJĘ gdy skończysz\n\n"
                "Staraj się skupić wzrok na środku ekranu\n"
                "i czytać w naturalnym tempie.",
                color='#E8F4F8'
            )
        else:  # approach 2
            self.gui.show_colored_instruction(
                "INSTRUKCJA",
                "W tym badaniu będziesz widział(a) na ekranie pojedyncze słowa.\n\n"
                "Przebieg jednego trialu:\n"
                "1. Słowo pojawia się na ekranie — przeczytaj je\n"
                "2. Słowo znika\n"
                "3. Usłyszysz kilka sygnałów dźwiękowych (beepów)\n"
                "4. Na każdy beep — powtórz to słowo w myślach\n\n"
                "Staraj się skupić wzrok na środku ekranu.",
                color='#E8F4F8'
            )

    def _show_sentence_instructions(self):
        if self.config.sentence_display_mode == 'rsvp':
            text = ("Teraz zobaczysz kilka zdań testowych.\n\n"
                    "Słowa będą pojawiać się jedno po drugim.\n"
                    "Czytaj je w myślach w miarę pojawiania się.")
        else:
            text = ("Teraz zobaczysz kilka zdań testowych.\n\n"
                    "Przeczytaj każde zdanie w myślach,\n"
                    "a następnie naciśnij SPACJĘ.")

        self.gui.show_colored_instruction(
            "FAZA TESTOWA: ZDANIA",
            text,
            color='#FFF4E6'
        )

    # === TRENING ===

    def _run_practice(self):
        """Kilka trialli treningowych żeby uczestnik zrozumiał zadanie."""
        practice_words = ["dom", "mama", "pies"]  # Proste słowa na rozgrzewkę

        self.gui.show_colored_instruction(
            "TRENING",
            f"Teraz zrobimy {len(practice_words)} próbne trialle.\n\n"
            "To tylko trening — dane nie będą zapisywane.\n\n"
            "Naciśnij SPACJĘ by rozpocząć trening.",
            color='#D1F2EB'
        )

        self.eeg.annotate("PRACTICE_START")

        for i, word in enumerate(practice_words):
            progress = f"Trening {i + 1}/{len(practice_words)}"

            # Fixation
            fix_time = random.randint(
                self.config.fixation_min_ms, self.config.fixation_max_ms
            )
            self.gui.show_fixation(fix_time)

            if self.config.approach == 1:
                self._run_approach1_trial(word, is_practice=True, progress_text=progress)
            else:
                self._run_approach2_trial(word, is_practice=True, progress_text=progress)

            self.gui.show_blank(self.config.post_trial_blank_ms)

        self.eeg.annotate("PRACTICE_END")

        self.gui.show_colored_instruction(
            "KONIEC TRENINGU",
            "Trening zakończony!\n\n"
            "Teraz zaczyna się właściwy eksperyment.\n"
            "Postaraj się nie ruszać głową.\n\n"
            "Naciśnij SPACJĘ by rozpocząć.",
            color='#D1F2EB'
        )

    # === FAZA SŁÓW ===

    def _run_word_phase(self, trials: List[WordTrial]):
        """Główna pętla fazy słów."""
        total = len(trials)
        self.logger.info(f"Rozpoczynam fazę słów: {total} trialli")

        for i, trial in enumerate(trials):
            # Przerwa co N trialli
            if i > 0 and i % self.config.break_every_n_trials == 0:
                self.eeg.annotate(f"BREAK_START_AFTER_{i}")
                self.gui.show_rest(self.config.break_duration_ms)
                self.eeg.annotate("BREAK_END")

            progress = f"{i + 1}/{total}"

            # Fixation
            fix_time = random.randint(
                self.config.fixation_min_ms, self.config.fixation_max_ms
            )
            self.gui.show_fixation(fix_time)
            self.eeg.annotate("FIXATION")

            # Trial
            trial_info = {
                "phase": "words",
                "trial_index": i,
                "word": trial.word,
                "word_index": trial.word_index,
                "repetition": trial.repetition,
                "approach": self.config.approach,
                "timestamp": datetime.now().isoformat(),
            }

            if self.config.approach == 1:
                duration = self._run_approach1_trial(trial.word, progress_text=progress)
                trial_info["reading_duration"] = duration
            else:
                self._run_approach2_trial(trial.word, progress_text=progress)

            self.trial_data.append(trial_info)
            self.gui.show_blank(self.config.post_trial_blank_ms)

        self.logger.info("Faza słów zakończona")

    def _run_approach1_trial(self, word: str, is_practice: bool = False,
                             progress_text: Optional[str] = None) -> float:
        """
        Podejście 1: słowo na ekranie → czytanie w myślach → spacja
        Zwraca czas reakcji w sekundach.
        """
        marker_prefix = "PRACTICE_" if is_practice else ""
        self.eeg.annotate(f"{marker_prefix}WORD_SHOW_{word}")

        start_time = time.time()

        if self.config.word_display_time_approach1 > 0:
            # Wyświetl na określony czas, potem czekaj na spację
            self.gui.show_word_timed(
                word,
                int(self.config.word_display_time_approach1 * 1000),
                progress_text
            )
            # Po zniknięciu czekamy na spację (opcjonalnie)
            self.gui.show_blank(0)
            self.gui.show_word(word, progress_text)
            self.gui.wait_for_space()
        else:
            # Wyświetl i czekaj na spację
            self.gui.show_word_wait_space(word, progress_text)

        duration = time.time() - start_time
        self.eeg.annotate(f"{marker_prefix}WORD_END_{word}")

        return duration

    def _run_approach2_trial(self, word: str, is_practice: bool = False,
                             progress_text: Optional[str] = None):
        """
        Podejście 2: słowo na ekranie → znika → beepy → mówienie w myślach
        """
        marker_prefix = "PRACTICE_" if is_practice else ""

        # 1. Wyświetl słowo
        self.eeg.annotate(f"{marker_prefix}WORD_SHOW_{word}")
        self.gui.show_word_timed(
            word,
            int(self.config.word_display_time * 1000),
            progress_text
        )

        # 2. Słowo znika - krótka pauza
        self.gui.show_blank(int(self.config.pre_beep_delay * 1000))

        # 3. Beepy
        self.eeg.annotate(f"{marker_prefix}BEEP_PHASE_START_{word}")

        for beep_idx in range(self.config.n_beeps):
            # Pokaż indicator
            self.gui.show_beep_indicator(beep_idx + 1, self.config.n_beeps)

            # Beep
            self.gui.play_beep(
                frequency=self.config.beep_frequency,
                duration_ms=self.config.beep_duration_ms
            )
            self.eeg.annotate(f"{marker_prefix}BEEP_{beep_idx + 1}_{word}")

            # Czekaj na interval (minus czas beepa)
            wait_ms = int(self.config.beep_interval * 1000) - self.config.beep_duration_ms
            if wait_ms > 0:
                self.gui._wait_ms(wait_ms)

        self.eeg.annotate(f"{marker_prefix}BEEP_PHASE_END_{word}")

    # === FAZA ZDAŃ ===

    def _run_sentence_phase(self, trials: List[SentenceTrial]):
        """Faza zdań testowych."""
        total = len(trials)
        self.logger.info(f"Rozpoczynam fazę zdań: {total} zdań ({self.config.sentence_display_mode})")

        for i, trial in enumerate(trials):
            progress = f"Zdanie {i + 1}/{total}"

            # Fixation
            fix_time = random.randint(
                self.config.fixation_min_ms, self.config.fixation_max_ms
            )
            self.gui.show_fixation(fix_time)
            self.eeg.annotate("FIXATION")

            self.eeg.annotate(f"SENTENCE_START_{i}")

            trial_info = {
                "phase": "sentences",
                "trial_index": i,
                "sentence": trial.sentence,
                "words": trial.words,
                "display_mode": self.config.sentence_display_mode,
                "timestamp": datetime.now().isoformat(),
            }

            if self.config.sentence_display_mode == 'rsvp':
                # Annotuj każde słowo osobno
                for w_idx, word in enumerate(trial.words):
                    self.eeg.annotate(f"RSVP_WORD_{w_idx}_{word}")

                self.gui.show_sentence_rsvp(
                    trial.words,
                    int(self.config.rsvp_word_duration * 1000),
                    progress_text=progress
                )
                self.gui.show_blank(int(self.config.rsvp_post_sentence_blank * 1000))
            else:
                # Full sentence
                start_time = time.time()
                self.gui.show_sentence_full(trial.sentence, progress_text=progress)
                trial_info["reading_duration"] = time.time() - start_time

            self.eeg.annotate(f"SENTENCE_END_{i}")
            self.trial_data.append(trial_info)
            self.gui.show_blank(self.config.post_trial_blank_ms)

        self.logger.info("Faza zdań zakończona")

    # === ZAPIS I CLEANUP ===

    def save_data(self):
        output_file = self.data_dir / f"{self.participant_id}_results.json"
        summary = {
            "participant_id": self.participant_id,
            "timestamp": datetime.now().isoformat(),
            "config": dataclasses.asdict(self.config),
            "total_word_trials": len([t for t in self.trial_data if t.get("phase") == "words"]),
            "total_sentence_trials": len([t for t in self.trial_data if t.get("phase") == "sentences"]),
            "trials": self.trial_data
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Results saved to {output_file}")

    def cleanup(self):
        if self.is_cleaned_up:
            return
        self.is_cleaned_up = True
        self.logger.info("Cleaning up...")
        if self.eeg:
            if self.eeg.is_recording():
                self.eeg.stop_recording()
            if hasattr(self.eeg, 'disconnect'):
                self.eeg.disconnect()
        if hasattr(self, 'gui') and self.gui:
            self.gui.close()
