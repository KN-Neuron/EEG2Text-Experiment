# experiment.py

import sys
import tkinter as tk
from pathlib import Path
import logging
import random
from typing import List, Dict, Optional
import time
import json
import dataclasses
from datetime import datetime
from gui import ExperimentGUI
from stimuli import Sentence, StimulusManager
from audio_manager import AudioManager


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

    def is_acquiring(self):
        return self.recording


# --- EEG2TextExperiment Class ---
class EEG2TextExperiment:
    def __init__(self, participant_id: str, logger: logging.Logger,
                 debug_mode: bool = False, use_mock_eeg: bool = False):
        self.participant_id = participant_id
        self.logger = logger
        self.debug_mode = debug_mode
        self.use_mock_eeg = use_mock_eeg or '--mock-eeg' in sys.argv
        self.data_dir = Path("data") / participant_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.stimulus_manager = StimulusManager(logger, debug_mode)
        self.audio_manager = AudioManager(logger)
        self.reading_times: Dict[str, float] = {}

        # Przechowuje dane wszystkich prób
        self.trial_data: List[Dict] = []

        if debug_mode:
            self.config = {
                'trial_block_size': 3,
                'sentences_per_mini_block': 5,
                'num_normal_mini_blocks': 1,
                'num_imagination_mini_blocks': 1,
                'num_reading_and_listening_mini_blocks': 1,
                'memory_task_size': 3,
                'fixation_min_ms': 300,
                'fixation_max_ms': 500,
                'post_reading_delay_ms': 100,
                'memory_recall_time_ms': 4000,
                'rest_duration_seconds': 3,
                'question_ratio': 0.6,
                'practice_questions_guaranteed': 1,
            }
        else:
            self.config = {
                'trial_block_size': 10,
                'sentences_per_mini_block': 10,
                'num_normal_mini_blocks': 5,
                'num_imagination_mini_blocks': 5,
                'num_reading_and_listening_mini_blocks': 5,
                'memory_task_size': 10,
                'fixation_min_ms': 400,
                'fixation_max_ms': 600,
                'post_reading_delay_ms': 1000,
                'memory_recall_time_ms': 6000,
                'rest_duration_seconds': 30,
                'question_ratio': 0.2,
                'practice_questions_guaranteed': 2,
            }

        self.gui = ExperimentGUI(logger, debug_mode)
        self.eeg = None
        self.is_cleaned_up = False
        self.initialize_eeg()

    def initialize_eeg(self):
        if self.use_mock_eeg:
            self.logger.info("Using MOCK EEG headset as requested by command line flag.")
            self.eeg = MockEEGHeadset(self.logger)
            self.eeg.connect()
            return

        try:
            from eeg_headset import EEGHeadset
            self.logger.info("Initializing BrainAccess via EEGHeadset class...")
            self.eeg = EEGHeadset(participant_id=self.participant_id, logger=self.logger)

            if not self.eeg.connect():
                raise RuntimeError("EEGHeadset.connect() failed. Check device and logs.")

            self.logger.info("BrainAccess initialized successfully via EEGHeadset class!")

        except (ImportError, RuntimeError) as e:
            self.logger.error(f"Failed to initialize real EEG headset: {e}")
            self.logger.warning("Please ensure 'brainaccess' is installed and eeg_headset.py is present.")
            if self.debug_mode:
                self.logger.warning("DEBUG MODE: Continuing with MOCK EEG headset due to error.")
                self.eeg = MockEEGHeadset(self.logger)
                self.eeg.connect()
            else:
                self.logger.error("Exiting due to EEG connection failure. Run with --mock-eeg to bypass.")
                raise

    def _save_block_metadata(self, block_file_path: Path, sentences: List[Sentence],
                             block_type: str, block_num: int, trial_data: List[Dict]):
        """Zapisuje kompletne metadane bloku"""
        metadata_file = block_file_path.with_suffix('.json')

        sentences_data = [dataclasses.asdict(s) for s in sentences]

        metadata = {
            'participant_id': self.participant_id,
            'block_type': block_type,
            'block_number': block_num,
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'eeg_file': block_file_path.name,
            'num_sentences': len(sentences),
            'sentences': sentences_data,
            'trials': trial_data
        }

        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved block metadata to {metadata_file}")
        except Exception as e:
            self.logger.error(f"Failed to save block metadata {metadata_file}: {e}")

    def _should_ask_question(self, sentence: Sentence) -> bool:
        """Decyduje, czy zadać pytanie"""
        if not sentence.question or not sentence.options or sentence.correct_answer_index is None:
            return False
        return random.random() < self.config['question_ratio']

    def run(self):
        try:
            self.gui.show_welcome()

            block_counter = 0

            # FAZA: NORMALNE CZYTANIE
            self.logger.info("=" * 60)
            self.logger.info("PHASE: NORMAL READING")
            self.logger.info("=" * 60)

            self.gui.show_colored_instruction(
                "CZYTANIE NORMALNE",
                "W tym bloku będziesz czytał/a zdania w sposób normalny.\n\n"
                "Przeczytaj każde zdanie w swoim naturalnym tempie.\n"
                "Naciśnij SPACJĘ, gdy skończysz czytać zdanie.\n\n"
                "Co kilka zdań będą pojawiać się pytania kontrolne dotyczące przeczytanego właśnie zdania.\n"
                "Odpowiadaj tak dobrze jak potrafisz.\n\n"
                "Zacznijmy od treningu!",
                color='#E8F4F8'
            )

            self.run_trial_block("normal")
            block_counter = self.run_main_block_sequence(
                "normal",
                self.config['num_normal_mini_blocks'],
                block_counter
            )

            # FAZA: CZYTANIE Z WYOBRAŻANIEM
            self.logger.info("=" * 60)
            self.logger.info("PHASE: IMAGINATION READING")
            self.logger.info("=" * 60)

            self.gui.show_colored_instruction(
                "CZYTANIE Z WYOBRAŻANIEM",
                "W tym bloku będziesz czytał/a i wizualizował/a sobie zdania.\n\n"
                "Przeczytaj każde ze zdań.\n"
                "Każde zdanie opisuje jakąś scenę.\n"
                "WYOBRAŹ SOBIE je, stwórz jego obraz w głowie.\n"
                "Zwizualizuj scenę tak dokładnie jak potrafisz.\n"
                "Naciśnij spację w momencie gdy skończysz wizualizację.\n\n"
                "Przykład: 'Mężczyzna przechodzi przez ulicę'\n"
                "→ Stwórz w swojej głowie obraz mężczyzny przechodzącego przez ulicę\n\n"
                "Zacznijmy od treningu!",
                color='#FFF4E6'
            )

            self.run_trial_block("imagination")
            block_counter = self.run_main_block_sequence(
                "imagination",
                self.config['num_imagination_mini_blocks'],
                block_counter
            )

            # FAZA: CZYTANIE I SŁUCHANIE
            self.logger.info("=" * 60)
            self.logger.info("PHASE: READING AND LISTENING")
            self.logger.info("=" * 60)

            self.gui.show_colored_instruction(
                "CZYTANIE I SŁUCHANIE",
                "W tym bloku będziesz czytał/a i słuchał/a jednocześnie.\n\n"
                "Zdania będą pojawiały się na ekranie.\n"
                "W tym samym czasie usłyszysz nagranie tego samego zdania.\n"
                "Postaraj się zsynchronizować tempo czytania z szybkością nagrania\n"
                "Naciśnij SPACJĘ po zakończeniu zadania.\n\n"
                "Zacznijmy od treningu!",
                color='#F0E6FF'
            )

            self.run_trial_block("reading_and_listening")
            block_counter = self.run_main_block_sequence(
                "reading_and_listening",
                self.config['num_reading_and_listening_mini_blocks'],
                block_counter
            )

            # FAZA: ZADANIE PAMIĘCIOWE
            self.logger.info("=" * 60)
            self.logger.info("PHASE: MEMORY RECALL TASK")
            self.logger.info("=" * 60)

            self.gui.show_colored_instruction(
                "ZADANIE PAMIĘCIOWE",
                "ZADANIE KOŃCOWE: Przywołanie z pamięci\n\n"
                "Zobaczysz zdania, które pojawiły się wcześniej w eksperymencie.\n\n"
                "Najpierw uważnie przestudiuj zdanie.\n"
                "Następnie pojawi się pusty ekran.\n"
                "W tym czasie mentalnie przypomnij sobie to zdanie.\n\n"
                "Gotowy, by zacząć?",
                color='#E6F7E6'
            )

            self.run_memory_task()

            self.gui.show_completion()

        except Exception as e:
            self.logger.error(f"Experiment error during run: {e}", exc_info=True)
            self.cleanup()
            raise
        finally:
            self.cleanup()

    def run_trial_block(self, block_type: str):
        """Uruchamia blok treningowy z gwarantowanymi pytaniami i informacją zwrotną"""
        self.logger.info(f"Starting PRACTICE block: {block_type}")

        instructions = {
            'normal': "TRENING: Normalne Czytanie\n\nPrzeczytaj każde zdanie i naciśnij SPACJĘ, kiedy skończysz.\n\nNaciśnij SPACJĘ, aby rozpocząć trening.",
            'imagination': "TRENING: Czytanie z Wyobraźnią\n\nPrzeczytaj zdanie i WIZUALIZUJ scenę.\nStwórz wyraźny obraz mentalny.\n\nNaciśnij SPACJĘ, gdy skończysz wyobrażać.\n\nNaciśnij SPACJĘ, aby rozpocząć trening.",
            'reading_and_listening': "TRENING: Czytanie i Słuchanie\n\nBędziesz czytać i jednocześnie słuchać zdań.\nNaciśnij SPACJĘ, kiedy skończysz.\n\nNaciśnij SPACJĘ, aby rozpocząć praktykę."
        }
        self.gui.show_instruction(instructions[block_type])

        if block_type == 'reading_and_listening':
            sentences = self.stimulus_manager.get_sentences('normal', self.config['trial_block_size'], is_trial=True)
        else:
            category = block_type if block_type in ['normal', 'imagination'] else 'normal'
            sentences = self.stimulus_manager.get_sentences(category, self.config['trial_block_size'], is_trial=True)


        questions_to_ask = self.config['practice_questions_guaranteed']
        sentences_with_questions = [s for s in sentences if s.question and s.options]

        if len(sentences_with_questions) < questions_to_ask:
            self.logger.warning(
                f"Not enough sentences with questions for practice. Need {questions_to_ask}, have {len(sentences_with_questions)}")
            questions_to_ask = len(sentences_with_questions)

        question_indices = set(random.sample(range(min(len(sentences), len(sentences_with_questions))),
                                             min(questions_to_ask, len(sentences))))

        for i, sentence in enumerate(sentences):
            self.logger.info(f"Practice trial {i + 1}/{len(sentences)}")
            jitter_ms = random.randint(self.config['fixation_min_ms'], self.config['fixation_max_ms'])
            self.gui.show_fixation(jitter_ms)

            if block_type == "reading_and_listening":
                word_count = len(sentence.text.split())
                estimated_time = (word_count / 150.0) * 60.0
                self.present_reading_and_listening_trial(sentence, estimated_time, is_practice=True)
            else:
                self.present_reading_trial(sentence, block_type, is_practice=True)

            if i in question_indices and sentence.question and sentence.options:
                self.logger.info(f"Practice question {i + 1}")
                selected_answer = self.gui.show_question(sentence.question, sentence.options)
                is_correct = (selected_answer == sentence.correct_answer_index)

                # POKAZUJE INFORMACJĘ ZWROTNĄ
                self.gui.show_feedback(is_correct, sentence.correct_answer_index, sentence.options)

                self.logger.info(f"Practice answer: {selected_answer}, Correct: {is_correct}")

            self.gui.show_blank(800 if self.debug_mode else 1000)

        self.gui.show_message(
            "Trening zakończony!\n\n"
            "Pamiętaj:\n"
            "• Czytaj w swoim naturalnym tempie\n"
            "• Odpowiadaj na pytania, gdy się pojawią\n"
            "• Pozostań skupiony\n\n"
            "Naciśnij SPACJĘ, aby przejść do głównego eksperymentu.",
            duration_ms=None
        )

    def run_main_block_sequence(self, block_type: str, num_blocks: int,
                                current_block_num: int) -> int:
        for i in range(num_blocks):
            self.run_experimental_block(block_type, current_block_num, i + 1)
            current_block_num += 1
            if i < num_blocks - 1:
                self.gui.show_rest(self.config['rest_duration_seconds'] * 1000)
        return current_block_num

    def run_experimental_block(self, block_type: str, global_block_num: int, type_block_num: int):
        self.logger.info(f"Starting MAIN block {global_block_num}: {block_type} #{type_block_num}")

        instructions = {
            'normal': f"Blok {global_block_num}\n\nNormalne Czytanie\n\nNaciśnij SPACJĘ po przeczytaniu każdego zdania.",
            'imagination': f"Blok {global_block_num}\n\nCzytanie z Wyobrażaniem\n\nWizualizuj scenę i naciśnij SPACJĘ, gdy masz jasny obraz mentalny.",
            'reading_and_listening': f"Blok {global_block_num}\n\nCzytanie i Słuchanie\n\nPrzeczytaj i posłuchaj zdania, a następnie naciśnij SPACJĘ."
        }
        self.gui.show_instruction(instructions[block_type])

        if block_type == 'reading_and_listening':
            sentences = self.stimulus_manager.get_sentences_for_listening(self.config['sentences_per_mini_block'])
        else:
            category = block_type if block_type in ['normal', 'imagination'] else 'normal'
            sentences = self.stimulus_manager.get_sentences(category, self.config['sentences_per_mini_block'])

        if not sentences:
            self.logger.warning(f"No sentences available for block {block_type}, skipping.")
            return

        eeg_file = self.data_dir / f"block_{global_block_num:02d}_{block_type}_{type_block_num}.fif"

        block_trial_data = []

        self.eeg.start_recording(str(eeg_file))
        self.eeg.annotate(f"BLOCK_START_{block_type}_#{type_block_num}")

        try:
            for i, sentence in enumerate(sentences):
                self.logger.info(f" Trial {i + 1}/{len(sentences)} in block {global_block_num}")

                trial_info = {
                    'trial_number': i + 1,
                    'sentence_text': sentence.text,
                    'sentence_category': sentence.category,
                    'timestamp': datetime.now().isoformat()
                }

                jitter_ms = random.randint(self.config['fixation_min_ms'], self.config['fixation_max_ms'])
                trial_info['fixation_duration_ms'] = jitter_ms
                self.gui.show_fixation(jitter_ms)
                self.eeg.annotate("FIXATION")

                if block_type == "reading_and_listening":
                    reading_time = self.reading_times.get(sentence.text)
                    if not reading_time:
                        word_count = len(sentence.text.split())
                        reading_time = (word_count / 150.0) * 60.0
                        self.logger.warning(
                            f"No reading time for '{sentence.text[:30]}...'. Estimating: {reading_time:.2f}s")
                    trial_info['target_audio_duration_s'] = reading_time
                    self.present_reading_and_listening_trial(sentence, reading_time, trial_info)
                else:
                    self.present_reading_trial(sentence, block_type, trial_info=trial_info)

                # Zadaje pytanie (bez informacji zwrotnej w głównych blokach)
                if self._should_ask_question(sentence):
                    self.logger.info(f"Asking question for trial {i + 1}")
                    self.eeg.annotate(f"QUESTION_START_trial_{i + 1}")

                    selected_answer = self.gui.show_question(sentence.question, sentence.options)
                    is_correct = (selected_answer == sentence.correct_answer_index)

                    trial_info['question_asked'] = True
                    trial_info['question'] = sentence.question
                    trial_info['options'] = sentence.options
                    trial_info['correct_answer_index'] = sentence.correct_answer_index
                    trial_info['selected_answer_index'] = selected_answer
                    trial_info['answer_correct'] = is_correct

                    self.eeg.annotate(f"QUESTION_END_trial_{i + 1}_answer_{selected_answer}_correct_{is_correct}")
                    self.logger.info(f"Answer: {selected_answer}, Correct: {is_correct}")
                else:
                    trial_info['question_asked'] = False

                block_trial_data.append(trial_info)
                self.trial_data.append(trial_info)

                self.gui.show_blank(800 if self.debug_mode else 1000)

        finally:
            self.eeg.annotate(f"BLOCK_END_{block_type}_#{type_block_num}")
            if self.eeg.stop_recording():
                self.logger.info(f"Successfully stopped recording and saved data to {eeg_file}")
            else:
                self.logger.error(f"Failed to stop/save recording for {eeg_file}")

            self._save_block_metadata(eeg_file, sentences, block_type, global_block_num, block_trial_data)

    def present_reading_trial(self, sentence: Sentence, block_type: str,
                              is_practice: bool = False, trial_info: Optional[Dict] = None):
        if not is_practice:
            self.eeg.annotate(f"SENTENCE_START_{block_type}")

        start_time = time.time()
        self.gui.show_sentence(sentence.text)
        self.gui.wait_for_space()
        reading_time = time.time() - start_time

        if trial_info:
            trial_info['reading_time_s'] = reading_time

        if block_type == "normal" and not is_practice:
            self.reading_times[sentence.text] = reading_time
            self.logger.info(f"Recorded reading time: {reading_time:.2f}s")

        if not is_practice:
            self.eeg.annotate(f"SENTENCE_END_{block_type}")
        self.gui.clear()

    def present_reading_and_listening_trial(self, sentence: Sentence, target_duration: float,
                                            trial_info: Optional[Dict] = None, is_practice: bool = False):
        if not is_practice:
            self.eeg.annotate("DELAY_START")
            self.gui.show_blank(self.config['post_reading_delay_ms'])
            self.eeg.annotate("DELAY_END")

        audio_file = self.audio_manager.get_audio(sentence.text, sentence.audio_path, target_duration)

        if trial_info:
            trial_info['audio_file'] = str(audio_file)

        if not is_practice:
            self.eeg.annotate("READING_LISTENING_START")

        self.gui.show_sentence(sentence.text)
        self.audio_manager.start_playing(audio_file)

        # --- ZMIANA: BLOKADA SPACJI W TRAKCIE ODTWARZANIA ---
        self.gui.show_instruction_overlay("SŁUCHANIE...")

        # Pętla czeka, aż nagranie się skończy
        while self.audio_manager.is_playing():
            time.sleep(0.05)
            self.gui.root.update()  # Utrzymuje responsywność GUI

        self.gui.show_instruction_overlay("NACIŚNIJ SPACJĘ")

        start_time = time.time()
        self.gui.wait_for_key(['space'])  # Czeka na spację DOPIERO TERAZ
        actual_duration = time.time() - start_time

        if trial_info:
            trial_info['actual_duration_s'] = actual_duration

        if self.audio_manager.is_playing():
            self.audio_manager.stop()

        if not is_practice:
            self.eeg.annotate("READING_LISTENING_END")
        self.gui.clear()

    def run_memory_task(self):
        self.logger.info("Starting MEMORY RECALL task")

        memory_sentences = self.stimulus_manager.get_memory_sentences(self.config['memory_task_size'])
        if not memory_sentences:
            self.logger.warning("No sentences available for memory task, skipping.")
            return

        eeg_file = self.data_dir / "memory_task.fif"
        memory_trial_data = []

        self.eeg.start_recording(str(eeg_file))
        self.eeg.annotate("MEMORY_TASK_START")

        try:
            for i, sentence in enumerate(memory_sentences):
                self.logger.info(f"Memory trial {i + 1}/{len(memory_sentences)}")

                trial_info = {
                    'trial_number': i + 1,
                    'sentence_text': sentence.text,
                    'sentence_category': sentence.category,
                    'timestamp': datetime.now().isoformat()
                }

                self.eeg.annotate(f"MEMORY_STUDY_START_{i + 1}")
                self.gui.show_sentence(sentence.text)
                self.gui.show_instruction_overlay(
                    "Zapamiętaj to zdanie. Naciśnij SPACJĘ, gdy będziesz gotów/gotowa by je przywołać.")
                self.gui.wait_for_space()
                self.eeg.annotate(f"MEMORY_STUDY_END_{i + 1}")
                self.gui.show_blank(1000)

                self.eeg.annotate(f"MEMORY_RECALL_START_{i + 1}")
                self.logger.info(f" Recall phase: {self.config['memory_recall_time_ms']}ms")
                self.gui.show_message("Teraz przywołaj zdanie w umyśle...", duration_ms=1000)
                self.gui.show_blank(self.config['memory_recall_time_ms'] - 1000)
                self.eeg.annotate(f"MEMORY_RECALL_END_{i + 1}")
                self.gui.show_blank(1000)

                trial_info['recall_duration_ms'] = self.config['memory_recall_time_ms']
                memory_trial_data.append(trial_info)
                self.trial_data.append(trial_info)

        finally:
            self.eeg.annotate("MEMORY_TASK_END")
            if self.eeg.stop_recording():
                self.logger.info(f"Successfully stopped recording and saved memory task data to {eeg_file}")
            else:
                self.logger.error(f"Failed to stop/save recording for {eeg_file}")

            self._save_block_metadata(eeg_file, memory_sentences, "memory", 0, memory_trial_data)

    def save_reading_times(self):
        if not self.reading_times:
            self.logger.info("No reading times recorded, skipping save.")
            return

        times_file = self.data_dir / "reading_times.json"

        mean_time = sum(self.reading_times.values()) / len(self.reading_times)
        min_time = min(self.reading_times.values())
        max_time = max(self.reading_times.values())

        data = {
            'reading_times': self.reading_times,
            'statistics': {
                'total_sentences': len(self.reading_times),
                'mean_time': mean_time,
                'min_time': min_time,
                'max_time': max_time
            }
        }
        with open(times_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved {len(self.reading_times)} reading times to {times_file}")

    def save_experiment_summary(self):
        summary_file = self.data_dir / "experiment_summary.json"

        questions_asked = sum(1 for trial in self.trial_data if trial.get('question_asked', False))
        correct_answers = sum(1 for trial in self.trial_data if trial.get('answer_correct', False))

        summary = {
            'participant_id': self.participant_id,
            'experiment_timestamp': datetime.now().isoformat(),
            'debug_mode': self.debug_mode,
            'config': self.config,
            'total_trials': len(self.trial_data),
            'questions_asked': questions_asked,
            'questions_correct': correct_answers,
            'accuracy': correct_answers / questions_asked if questions_asked > 0 else 0,
            'all_trials': self.trial_data
        }

        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved experiment summary to {summary_file}")
        except Exception as e:
            self.logger.error(f"Failed to save experiment summary: {e}")

    def cleanup(self):
        if self.is_cleaned_up:
            return
        self.is_cleaned_up = True
        self.logger.info("Cleaning up...")
        self.save_reading_times()
        self.save_experiment_summary()
        if self.eeg:
            try:
                if self.eeg.is_recording():
                    self.logger.warning("Stopping active recording during cleanup...")
                    self.eeg.stop_recording()

                if hasattr(self.eeg, 'disconnect'):
                    self.logger.info("Disconnecting from EEG device...")
                    self.eeg.disconnect()
            except Exception as e:
                self.logger.error(f"Error during EEG cleanup: {e}")

        if hasattr(self, 'gui') and self.gui:
            self.gui.close()

        self.logger.info("Cleanup complete")