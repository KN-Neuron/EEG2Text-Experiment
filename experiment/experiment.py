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
# from stimuli import Sentence, StimulusManager # (Nie używamy, jeśli wszystko idzie z JSON)
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


# --- EEG2TextExperiment Class ---
class EEG2TextExperiment:
    def __init__(self, participant_id: str, logger: logging.Logger,
                 debug_mode: bool = False, use_mock_eeg: bool = False,
                 json_filename: str = 'fb.json'):
        self.participant_id = participant_id
        self.logger = logger
        self.debug_mode = debug_mode
        self.use_mock_eeg = use_mock_eeg or '--mock-eeg' in sys.argv
        self.json_filename = json_filename

        # Słownik czasów czytania: { "Treść zdania": czas_w_sekundach }
        self.reading_times: Dict[str, float] = {}

        self.data_dir = Path("data") / participant_id
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.audio_manager = AudioManager(logger)
        self.gui = ExperimentGUI(logger, debug_mode)

        self.trial_data: List[Dict] = []
        self.eeg = None
        self.is_cleaned_up = False
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
            self.logger.error(f"Failed to initialize real EEG headset: {e}")
            if self.debug_mode:
                self.logger.warning("DEBUG MODE: Continuing with MOCK EEG headset.")
                self.eeg = MockEEGHeadset(self.logger)
                self.eeg.connect()
            else:
                raise

    def load_experiment_data(self) -> List[Dict]:
        possible_paths = [Path("data") / self.json_filename, Path(self.json_filename)]
        json_path = next((p for p in possible_paths if p.exists()), None)

        if not json_path:
            # Tworzymy plik dummy, jeśli nie ma
            raise FileNotFoundError(f"Nie znaleziono pliku JSON: {self.json_filename}")

        self.logger.info(f"Loading experiment data from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            if isinstance(content, dict) and "fullContent" in content:
                return content["fullContent"]
            elif isinstance(content, list):
                return content
            raise ValueError("Nieznany format pliku JSON.")

    def get_instruction_text(self, block_type: str) -> dict:
        instructions = {
            "nr": {
                "title": "CZYTANIE NORMALNE",
                "text": "Przeczytaj zdanie w swoim naturalnym tempie.\nNaciśnij SPACJĘ po zakończeniu.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#E8F4F8"
            },
            "sr": {
                "title": "OCENA SENTYMENTU",
                "text": "Przeczytaj zdanie. Jeśli pojawi się pytanie, oceń wydźwięk.\nNaciśnij SPACJĘ po zakończeniu.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#FFF4E6"
            },
            "audio": {
                "title": "SŁUCHANIE AUDIO",
                "text": "Posłuchaj nagrania. Tekst będzie widoczny na ekranie.\nDługość nagrania dostosuje się do Twojego tempa czytania.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#F0E6FF"
            }
        }
        return instructions.get(block_type, {"title": "INSTRUKCJA", "text": "Naciśnij SPACJĘ.", "color": "#FFFFFF"})

    def run(self):
        try:
            self.gui.show_welcome()
            experiment_data = self.load_experiment_data()

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            eeg_path = self.data_dir / f"{self.participant_id}_full_experiment_{timestamp_str}.fif"

            self.logger.info(f"Starting recording to: {eeg_path}")
            self.eeg.start_recording(str(eeg_path))
            self.eeg.annotate("EXPERIMENT_START")

            current_block_type = None

            for index, item in enumerate(experiment_data):
                item_type = item.get("type", "nr").lower()
                item_id = item.get("id", "unknown")
                item_text = item.get("text", "")

                # 1. PRZERWA
                if item_type == "break":
                    self.eeg.annotate("BREAK_START")
                    self.gui.show_rest(duration_ms=10000)
                    self.eeg.annotate("BREAK_END")
                    current_block_type = "break"
                    continue

                # 2. INSTRUKCJA
                if item_type != current_block_type:
                    instr = self.get_instruction_text(item_type)
                    self.eeg.annotate(f"INSTRUCTION_START_{item_type.upper()}")
                    self.gui.show_colored_instruction(instr["title"], instr["text"], color=instr["color"])
                    self.eeg.annotate(f"INSTRUCTION_END_{item_type.upper()}")
                    current_block_type = item_type

                trial_info = {
                    "trial_index": index,
                    "id": item_id,
                    "type": item_type,
                    "text": item_text,
                    "timestamp": datetime.now().isoformat(),
                    "question_asked": False
                }

                # FIXATION
                fixation_time = random.randint(400, 600)
                self.gui.show_fixation(fixation_time)
                self.eeg.annotate("FIXATION")

                # 3. PREZENTACJA BODŹCA
                self.eeg.annotate(f"STIM_START_ID_{item_id}_TYPE_{item_type.upper()}")
                start_time = time.time()

                if item_type == "audio":
                    # --- OBSŁUGA AUDIO ---
                    raw_audio_path = item.get("path")

                    # Pobieramy zapisany czas czytania
                    target_duration = self.reading_times.get(item_text, 0.0)

                    self.logger.info(f"Preparing audio for ID {item_id}. Target duration: {target_duration:.2f}s")

                    # AudioManager przygotowuje plik (przyspiesza/zwalnia/generuje TTS)
                    # Zwraca ścieżkę do gotowego pliku
                    final_audio_path = self.audio_manager.get_audio(item_text, raw_audio_path, target_duration)

                    trial_info["audio_path"] = str(final_audio_path)
                    trial_info["target_duration"] = target_duration

                    # 1. Pokaż tekst
                    self.gui.show_sentence(item_text)
                    # 2. Pokaż overlay
                    self.gui.show_instruction_overlay("SŁUCHANIE...")

                    # 3. Graj
                    self.audio_manager.start_playing(final_audio_path)

                    # 4. Czekaj na koniec audio
                    while self.audio_manager.is_playing():
                        time.sleep(0.05)
                        self.gui.root.update()

                    self.gui.show_instruction_overlay("NACIŚNIJ SPACJĘ")
                    self.gui.wait_for_key(['space'])

                else:
                    # --- OBSŁUGA CZYTANIA (NR / SR) ---
                    self.gui.show_sentence(item_text)
                    self.gui.wait_for_space()

                    # KLUCZOWE: Zapisujemy czas czytania
                    reading_time = time.time() - start_time
                    self.reading_times[item_text] = reading_time
                    self.logger.info(f"Recorded reading time for text: {reading_time:.2f}s")
                    trial_info["reading_duration"] = reading_time

                self.eeg.annotate(f"STIM_END_ID_{item_id}")

                # 4. PYTANIA
                question_text = item.get("question")
                answers = item.get("answers") or item.get("options")

                if question_text and answers:
                    self.gui.clear()
                    self.gui.show_blank(200)
                    self.eeg.annotate(f"QUESTION_START_ID_{item_id}")

                    selected_idx = self.gui.show_question(question_text, answers)

                    correct_idx = item.get("right_answer")
                    if correct_idx is not None and isinstance(correct_idx, int):
                        if correct_idx > 0 and correct_idx <= len(answers):
                            correct_idx = correct_idx - 1

                    is_correct = (selected_idx == correct_idx) if correct_idx is not None else None

                    trial_info["question_asked"] = True
                    trial_info["selected_answer"] = selected_idx
                    trial_info["correct_answer"] = correct_idx
                    trial_info["is_correct"] = is_correct
                    self.eeg.annotate(f"RESPONSE_IDX_{selected_idx}_CORRECT_{is_correct}")

                self.trial_data.append(trial_info)
                self.gui.show_blank(500)

            self.eeg.annotate("EXPERIMENT_END")
            self.save_data()
            self.gui.show_completion()

        except Exception as e:
            self.logger.error(f"Critical error: {e}", exc_info=True)
            raise
        finally:
            self.cleanup()

    def save_data(self):
        output_file = self.data_dir / f"{self.participant_id}_results.json"
        summary = {
            "participant_id": self.participant_id,
            "timestamp": datetime.now().isoformat(),
            "data_source": self.json_filename,
            "total_trials": len(self.trial_data),
            "reading_times_captured": self.reading_times,
            "trials": self.trial_data
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Results saved to {output_file}")

    def cleanup(self):
        if self.is_cleaned_up: return
        self.is_cleaned_up = True
        self.logger.info("Cleaning up...")
        if self.eeg:
            if self.eeg.is_recording(): self.eeg.stop_recording()
            if hasattr(self.eeg, 'disconnect'): self.eeg.disconnect()
        if hasattr(self, 'gui') and self.gui: self.gui.close()