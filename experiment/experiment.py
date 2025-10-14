# experiment.py

import sys
import tkinter as tk
from pathlib import Path
import logging
import random
from typing import List, Dict, Optional
import time
import json
import dataclasses # <--- ADDED: To convert Sentence objects to dictionaries
from gui import ExperimentGUI
from stimuli import Sentence, StimulusManager
from audio_manager import AudioManager

# --- MOCK EEG HEADSET (Unchanged) ---
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


# --- EEG2TextExperiment Class (MODIFIED) ---
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
        
        if debug_mode:
            self.config = {
                'trial_block_size': 2,
                'sentences_per_mini_block': 3,
                'num_normal_mini_blocks': 1,
                'num_sentiment_mini_blocks': 1,
                'num_reading_and_listening_mini_blocks': 1,
                'memory_task_size': 2,
                'fixation_min_ms': 400,
                'fixation_max_ms': 600,
                'post_reading_delay_ms': 100,
                'memory_recall_time_ms': 6000,
                'rest_duration_seconds': 5,
            }
        else:
            self.config = {
                'trial_block_size': 10,
                'sentences_per_mini_block': 10,
                'num_normal_mini_blocks': 5,
                'num_sentiment_mini_blocks': 5,
                'num_reading_and_listening_mini_blocks': 5,
                'memory_task_size': 10,
                'fixation_min_ms': 400,
                'fixation_max_ms': 600,
                'post_reading_delay_ms': 1000,
                'memory_recall_time_ms': 6000,
                'rest_duration_seconds': 30,
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

    # --- ADDED HELPER TO SAVE STIMULI ---
    def _save_stimuli_for_block(self, file_path: Path, sentences: List[Sentence]):
        """Saves the list of sentences for a block to a JSON file."""
        stimuli_file = file_path.with_suffix('.json')
        # Convert list of Sentence objects to a list of dictionaries
        sentences_as_dicts = [dataclasses.asdict(s) for s in sentences]
        try:
            with open(stimuli_file, 'w', encoding='utf-8') as f:
                json.dump(sentences_as_dicts, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved stimuli for block to {stimuli_file}")
        except Exception as e:
            self.logger.error(f"Failed to save stimuli file {stimuli_file}: {e}")


    def run(self):
        try:
            self.gui.show_welcome()
            
            block_counter = 0

            self.logger.info("=" * 60)
            self.logger.info("PHASE: NORMAL READING")
            self.logger.info("=" * 60)
            self.run_trial_block("normal") 
            block_counter = self.run_main_block_sequence(
                "normal", 
                self.config['num_normal_mini_blocks'], 
                block_counter
            )

            self.logger.info("=" * 60)
            self.logger.info("PHASE: SENTIMENT READING")
            self.logger.info("=" * 60)
            self.run_trial_block("sentiment")
            block_counter = self.run_main_block_sequence(
                "sentiment", 
                self.config['num_sentiment_mini_blocks'],
                block_counter
            )

            self.logger.info("=" * 60)
            self.logger.info("PHASE: READING AND LISTENING")
            self.logger.info("=" * 60)
            self.run_trial_block("reading_and_listening")
            block_counter = self.run_main_block_sequence(
                "reading_and_listening", 
                self.config['num_reading_and_listening_mini_blocks'],
                block_counter
            )

            self.logger.info("=" * 60)
            self.logger.info("PHASE: MEMORY RECALL TASK")
            self.logger.info("=" * 60)
            self.run_memory_task()
            
            self.gui.show_completion()

        except Exception as e:
            self.logger.error(f"Experiment error during run: {e}", exc_info=True)
            self.cleanup()
            raise
        finally:
            self.cleanup()

    # --- run_trial_block and run_main_block_sequence (Unchanged) ---
    def run_trial_block(self, block_type: str):
        self.logger.info(f"Starting PRACTICE block: {block_type}")
        instructions = {
            'normal': "PRACTICE: Normal Reading\n\nRead the sentences that appear on the screen.\nPress SPACE when you have finished reading.\n\nPress SPACE to begin.",
            'sentiment': "PRACTICE: Emotional Reading\n\nRead the sentences and imagine the scenario being described.\nPress SPACE when you are done.\n\nPress SPACE to begin.",
            'reading_and_listening': "PRACTICE: Reading and Listening\n\nRead the sentence on the screen while listening to the audio.\nPress SPACE when the audio finishes to continue.\n\nPress SPACE to begin."
        }
        self.gui.show_instruction(instructions[block_type])
        
        sentences = self.stimulus_manager.get_sentences(
            'listening' if block_type == 'reading_and_listening' else block_type,
            self.config['trial_block_size'],
            is_trial=True
        )
        for i, sentence in enumerate(sentences):
            self.logger.info(f"Practice Trial {i+1}/{len(sentences)}: {block_type}")
            fixation_duration = random.randint(
                self.config['fixation_min_ms'],
                self.config['fixation_max_ms']
            )
            self.gui.show_fixation(fixation_duration)
            
            if block_type == "reading_and_listening":
                word_count = len(sentence.text.split())
                estimated_time = (word_count / 150.0) * 60.0 
                self.present_reading_and_listening_trial(sentence, estimated_time, is_practice=True)
            else:
                self.present_reading_trial(sentence, block_type, is_practice=True)
            self.gui.show_blank(1000)
            
        self.gui.show_message("Practice complete.\nThe main task will now begin.\n\nPress SPACE to continue.")
        self.logger.info(f"Practice block for {block_type} completed")

    def run_main_block_sequence(self, block_type: str, num_mini_blocks: int, start_block_num: int) -> int:
        current_block_num = start_block_num
        for i in range(num_mini_blocks):
            current_block_num += 1
            self.run_experimental_block(block_type, current_block_num, i + 1)
            if i < num_mini_blocks - 1:
                self.gui.show_rest(self.config['rest_duration_seconds'] * 1000)
        return current_block_num

    # --- run_experimental_block (MODIFIED) ---
    def run_experimental_block(self, block_type: str, global_block_num: int, type_block_num: int):
        self.logger.info(f"Starting MAIN block {global_block_num}: {block_type} #{type_block_num}")
        instructions = {
            'normal': f"Block {global_block_num}\n\nNormal Reading\n\nPress SPACE when you finish reading each sentence.",
            'sentiment': f"Block {global_block_num}\n\nEmotional Reading\n\nImagine the scenario described and press SPACE when done.",
            'reading_and_listening': f"Block {global_block_num}\n\nReading and Listening\n\nRead and listen to the sentence, then press SPACE."
        }
        self.gui.show_instruction(instructions[block_type])
        
        if block_type == 'reading_and_listening':
            sentences = self.stimulus_manager.get_sentences_for_listening(self.config['sentences_per_mini_block'])
        else:
            sentences = self.stimulus_manager.get_sentences(block_type, self.config['sentences_per_mini_block'])

        if not sentences:
            self.logger.warning(f"No sentences available for block {block_type}, skipping.")
            return

        eeg_file = self.data_dir / f"block_{global_block_num:02d}_{block_type}_{type_block_num}.fif"
        
        # ADDED: Save the sentences for this block
        self._save_stimuli_for_block(eeg_file, sentences)
        
        self.eeg.start_recording(str(eeg_file))
        self.eeg.annotate(f"BLOCK_START_{block_type}_#{type_block_num}")
        try:
            for i, sentence in enumerate(sentences):
                self.logger.info(f" Trial {i+1}/{len(sentences)} in block {global_block_num}")
                jitter_ms = random.randint(self.config['fixation_min_ms'], self.config['fixation_max_ms'])
                self.gui.show_fixation(jitter_ms)
                self.eeg.annotate("FIXATION")
                
                if block_type == "reading_and_listening":
                    reading_time = self.reading_times.get(sentence.text)
                    if not reading_time:
                        word_count = len(sentence.text.split())
                        reading_time = (word_count / 150.0) * 60.0 
                        self.logger.warning(f"No reading time for '{sentence.text[:30]}...'. Estimating: {reading_time:.2f}s")
                    self.present_reading_and_listening_trial(sentence, reading_time)
                else:
                    self.present_reading_trial(sentence, block_type)
                
                self.gui.show_blank(1000)
        finally:
            self.eeg.annotate(f"BLOCK_END_{block_type}_#{type_block_num}")
            if self.eeg.stop_recording():
                self.logger.info(f"Successfully stopped recording and saved data to {eeg_file}")
            else:
                self.logger.error(f"Failed to stop/save recording for {eeg_file}")


    # --- present_reading_trial and present_reading_and_listening_trial (Unchanged) ---
    def present_reading_trial(self, sentence: Sentence, block_type: str, is_practice: bool = False):
        if not is_practice:
            self.eeg.annotate(f"SENTENCE_START_{block_type}")
        
        start_time = time.time()
        self.gui.show_sentence(sentence.text)
        self.gui.wait_for_space()
        reading_time = time.time() - start_time
        
        if block_type == "normal" and not is_practice:
            self.reading_times[sentence.text] = reading_time
            self.logger.info(f"Recorded reading time: {reading_time:.2f}s")

        if not is_practice:
            self.eeg.annotate(f"SENTENCE_END_{block_type}")
        self.gui.clear()

    def present_reading_and_listening_trial(self, sentence: Sentence, target_duration: float, is_practice: bool = False):
        if not is_practice:
            self.eeg.annotate("DELAY_START")
            self.gui.show_blank(self.config['post_reading_delay_ms'])
            self.eeg.annotate("DELAY_END")

        audio_file = self.audio_manager.get_audio(sentence.text, sentence.audio_path, target_duration)
        
        if not is_practice:
            self.eeg.annotate("READING_LISTENING_START")
        
        self.gui.show_sentence(sentence.text)
        self.audio_manager.start_playing(audio_file)
        
        self.gui.wait_for_space()
        if self.audio_manager.is_playing():
            self.audio_manager.stop()
        
        if not is_practice:
            self.eeg.annotate("READING_LISTENING_END")
        self.gui.clear()

    # --- run_memory_task (MODIFIED) ---
    def run_memory_task(self):
        self.logger.info("Starting MEMORY RECALL task")
        self.gui.show_instruction(
            "FINAL TASK: Memory Recall\n\n"
            "You will see sentences from earlier.\n"
            "Study each sentence, then press SPACE.\n"
            "After that, a blank screen will appear. Mentally recall the sentence.\n\n"
            "Press SPACE to begin."
        )
        memory_sentences = self.stimulus_manager.get_memory_sentences(self.config['memory_task_size'])
        if not memory_sentences:
            self.logger.warning("No sentences available for memory task, skipping.")
            return

        eeg_file = self.data_dir / "memory_task.fif"
        
        # ADDED: Save the sentences for this block
        self._save_stimuli_for_block(eeg_file, memory_sentences)

        self.eeg.start_recording(str(eeg_file))
        self.eeg.annotate("MEMORY_TASK_START")
        try:
            for i, sentence in enumerate(memory_sentences):
                self.logger.info(f"Memory trial {i+1}/{len(memory_sentences)}")
                
                self.eeg.annotate(f"MEMORY_STUDY_START_{i+1}")
                self.gui.show_sentence(sentence.text)
                self.gui.show_instruction_overlay("Study this sentence. Press SPACE when ready to recall it.")
                self.gui.wait_for_space()
                self.eeg.annotate(f"MEMORY_STUDY_END_{i+1}")
                self.gui.show_blank(1000)

                self.eeg.annotate(f"MEMORY_RECALL_START_{i+1}")
                self.logger.info(f" Recall phase: {self.config['memory_recall_time_ms']}ms")
                self.gui.show_message("Now, recall the sentence in your mind...", duration_ms=1000)
                self.gui.show_blank(self.config['memory_recall_time_ms'] - 1000)
                self.eeg.annotate(f"MEMORY_RECALL_END_{i+1}")
                self.gui.show_blank(1000)
        finally:
            self.eeg.annotate("MEMORY_TASK_END")
            if self.eeg.stop_recording():
                self.logger.info(f"Successfully stopped recording and saved memory task data to {eeg_file}")
            else:
                self.logger.error(f"Failed to stop/save recording for {eeg_file}")


    # --- save_reading_times (Unchanged) ---
    def save_reading_times(self):
        if not self.reading_times:
            return
        times_file = self.data_dir / "reading_times.json"
        
        if not self.reading_times:
            self.logger.info("No reading times recorded, skipping save.")
            return

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

    def cleanup(self):
        if self.is_cleaned_up:
            return
        self.is_cleaned_up = True
        self.logger.info("Cleaning up...")
        self.save_reading_times()
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