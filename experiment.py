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

    def _create_practice_items(self, block_type: str) -> List[Dict]:
        """Generuje 3 zdania treningowe dla danego typu bloku."""
        items = []

        if block_type == 'nr':
            items = [
                {
                    "text": "To jest zdanie treningowe. Przeczytaj je w naturalnym tempie.",
                    "id": "p_nr_1", "type": "nr_practice", "path": None
                },
                {
                    "text": "Naciśnij spację dopiero, gdy skończysz czytać cały tekst.",
                    "id": "p_nr_2", "type": "nr_practice", "path": None
                },
                {
                    "text": "To ostatnie zdanie treningowe czytania.",
                    "id": "p_nr_3", "type": "nr_practice", "path": None
                }
            ]
        elif block_type == 'sr':
            items = [
                {
                    "text": "Lubię, gdy świeci słońce i jest ciepło.",
                    "id": "p_sr_1", "type": "sr_practice", "path": None,
                    "question": None,
                    "right_answer": 1
                },
                {
                    "text": "Dzisiaj zgubiłem klucze i spóźniłem się do pracy.",
                    "id": "p_sr_2", "type": "sr_practice", "path": None,
                    "question": None,
                    "right_answer": 2
                },
                {
                    "text": "Wczoraj po południu czytałem gazetę.",
                    "id": "p_sr_3", "type": "sr_practice", "path": None,
                    "question": None,
                    "right_answer": 3
                }
            ]
        elif block_type == 'audio':
            items = [
                {
                    "text": "Szukam inspiracji w starych książkach podróżniczych.",
                    "id": "p_audio_1", "type": "audio_practice",
                    "path": "test_audio/audio0.mp3",
                    "question": "Jakie słowo pojawiło się w zdaniu", "answers": ["Szukam", "Siłownia", "Plecak"], "right_answer": 1
                },
                {
                    "text": "Ostatnio odwiedziłam nowo otwartą siłownię w centrum",
                    "id": "p_audio_2", "type": "audio_practice",
                    "path": "test_audio/audio1.mp3",
                    "question": None, "answers": None, "right_answer": None
                },
                {
                    "text": "On często spaceruje brzegiem rzeki przy zachodzie słońca",
                    "id": "p_audio_3", "type": "audio_practice",
                    "path": "test_audio/audio2.mp3",
                    "question": None, "answers": None, "right_answer": None
                }
            ]

        return items

    def _inject_practice_blocks(self, original_data: List[Dict]) -> List[Dict]:
        """Wstawia bloki treningowe przed pierwszym wystąpieniem danego typu."""
        new_data = []
        practiced_types = set()

        # Mapowanie typów z JSON na typy bazowe
        for item in original_data:
            t = item.get('type', 'nr').lower()

            # Jeśli to główny typ (nie break) i jeszcze nie był trenowany
            if t in ['nr', 'sr', 'audio'] and t not in practiced_types:
                self.logger.info(f"Injecting PRACTICE block for type: {t}")

                # Dodajemy 3 zdania treningowe
                practice_items = self._create_practice_items(t)
                new_data.extend(practice_items)

                # Oznaczamy, że ten typ ma już trening
                practiced_types.add(t)

            # Dodajemy oryginalny element
            new_data.append(item)

        return new_data

    def load_experiment_data(self) -> List[Dict]:
        possible_paths = [Path("data") / self.json_filename, Path(self.json_filename)]
        json_path = next((p for p in possible_paths if p.exists()), None)

        if not json_path:
            raise FileNotFoundError(f"Nie znaleziono pliku JSON: {self.json_filename}")

        self.logger.info(f"Loading experiment data from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            data = []
            if isinstance(content, dict) and "fullContent" in content:
                data = content["fullContent"]
            elif isinstance(content, list):
                data = content
            else:
                raise ValueError("Nieznany format pliku JSON.")

            # TUTAJ wstrzykujemy treningi
            return self._inject_practice_blocks(data)

    def get_instruction_text(self, block_type: str) -> dict:
        """Zwraca treść instrukcji. Obsługuje też typy treningowe."""
        instructions = {
            # --- TRENINGI ---
            "nr_practice": {
                "title": "TRENING: CZYTANIE",
                "text": "To jest krótki trening.\n\nPrzeczytaj zdania w naturalnym tempie.\nNaciśnij SPACJĘ, gdy skończysz.\n\nNaciśnij SPACJĘ, aby rozpocząć trening.",
                "color": "#D1F2EB"  # Jasny turkus
            },
            "sr_practice": {
                "title": "TRENING: SENTYMENT",
                "text": "To jest krótki trening.\n\nPrzeczytaj zdanie i odpowiedz na pytanie (jeśli się pojawi).\n\nNaciśnij SPACJĘ, aby rozpocząć trening.",
                "color": "#FAD7A0"  # Jasny pomarańcz
            },
            "audio_practice": {
                "title": "TRENING: AUDIO",
                "text": "To jest krótki trening.\n\nZałóż słuchawki. Posłuchaj nagrań testowych.\n\nNaciśnij SPACJĘ, aby rozpocząć trening.",
                "color": "#D7BDE2"  # Jasny fiolet
            },

            # --- GŁÓWNE BLOKI ---
            "nr": {
                "title": "EKSPERYMENT: CZYTANIE",
                "text": "Koniec treningu. Zaczynamy badanie.\n\nPrzeczytaj zdanie w swoim naturalnym tempie.\nNaciśnij SPACJĘ po zakończeniu.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#E8F4F8"
            },
            "sr": {
                "title": "EKSPERYMENT: OCENA SENTYMENTU",
                "text": "Koniec treningu. Zaczynamy badanie.\n\nPrzeczytaj zdanie. Jeśli pojawi się pytanie, odpowiedz na nie.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#FFF4E6"
            },
            "audio": {
                "title": "EKSPERYMENT: SŁUCHANIE AUDIO",
                "text": "Koniec treningu. Zaczynamy badanie.\n\nPosłuchaj nagrania. Tekst będzie widoczny.\nDługość nagrania dostosuje się do Twojego tempa czytania.\n\nNaciśnij SPACJĘ, aby rozpocząć.",
                "color": "#F0E6FF"
            }
        }
        # Fallback dla nieznanych typów
        return instructions.get(block_type, {"title": "INSTRUKCJA", "text": "Naciśnij SPACJĘ, aby kontynuować.",
                                             "color": "#FFFFFF"})

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
                # raw_type to np. "nr_practice" lub "nr"
                raw_type = item.get("type", "nr").lower()
                item_id = item.get("id", "unknown")
                item_text = item.get("text", "")

                # Sprawdzamy czy to practice, by wiedzieć jak traktować logikę (base_type)
                is_practice = "_practice" in raw_type
                # base_type to "nr", "sr", "audio" (usuwamy suffix _practice)
                base_type = raw_type.replace("_practice", "")

                # 1. PRZERWA
                if base_type == "break":
                    self.eeg.annotate("BREAK_START")
                    self.gui.show_rest(duration_ms=10000)
                    self.eeg.annotate("BREAK_END")
                    current_block_type = "break"
                    continue

                # 2. INSTRUKCJA (na zmianę raw_type, czyli np. z nr_practice na nr też pokaże instrukcję)
                if raw_type != current_block_type:
                    instr = self.get_instruction_text(raw_type)
                    self.eeg.annotate(f"INSTRUCTION_START_{raw_type.upper()}")
                    self.gui.show_colored_instruction(instr["title"], instr["text"], color=instr["color"])
                    self.eeg.annotate(f"INSTRUCTION_END_{raw_type.upper()}")
                    current_block_type = raw_type

                trial_info = {
                    "trial_index": index,
                    "id": item_id,
                    "type": raw_type,  # Zapisujemy dokładny typ (np. nr_practice)
                    "text": item_text,
                    "timestamp": datetime.now().isoformat(),
                    "is_practice": is_practice,
                    "question_asked": False
                }

                # FIXATION
                fixation_time = random.randint(400, 600)
                self.gui.show_fixation(fixation_time)
                self.eeg.annotate("FIXATION")

                # Marker EEG zawiera informację czy to PRACTICE
                marker_type = raw_type.upper()
                self.eeg.annotate(f"STIM_START_ID_{item_id}_TYPE_{marker_type}")

                start_time = time.time()

                if base_type == "audio":
                    # --- OBSŁUGA AUDIO ---
                    raw_audio_path = item.get("path")

                    # Pobieramy czas czytania (tylko dla głównego eksperymentu, dla treningu raczej nie będzie matchu tekstowego)
                    target_duration = self.reading_times.get(item_text, 0.0)

                    # Dla practice audio - jeśli nie ma czasu (bo tekst inny niż w practice NR), puści normalnie.

                    self.logger.info(f"Preparing audio ID {item_id}. Target: {target_duration:.2f}s")
                    final_audio_path = self.audio_manager.get_audio(item_text, raw_audio_path, target_duration)

                    trial_info["audio_path"] = str(final_audio_path)
                    trial_info["target_duration"] = target_duration

                    self.gui.show_sentence(item_text)
                    self.gui.show_instruction_overlay("SŁUCHANIE...")

                    self.audio_manager.start_playing(final_audio_path)

                    while self.audio_manager.is_playing():
                        time.sleep(0.05)
                        self.gui.root.update()

                    self.gui.show_instruction_overlay("NACIŚNIJ SPACJĘ")
                    self.gui.wait_for_key(['space'])

                else:
                    # --- OBSŁUGA CZYTANIA (NR / SR) ---
                    self.gui.show_sentence(item_text)
                    self.gui.wait_for_space()

                    reading_time = time.time() - start_time

                    # Zapisujemy czas TYLKO jeśli to nie jest trening (żeby nie śmiecić słownika)
                    # Albo zapisujemy zawsze - jeśli teksty w treningu Audio są takie same jak w treningu NR, to zadziała.
                    # W mojej implementacji teksty są inne, więc po prostu zapisujemy.
                    self.reading_times[item_text] = reading_time

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
