"""
eeg_headset_mock.py

A mock version of the EEG headset that simulates the functionality without requiring
the actual BrainAccess library. This allows the application to run on ARM64 systems
until the proper ARM64 library is available.
"""

import os
import time
from typing import Any, Dict, List, Optional
import numpy as np
import logging
from pathlib import Path

class EEGHeadset:
    """
    Mock version of EEG headset interface that simulates connection and data acquisition
    without requiring the actual BrainAccess library.
    """

    def __init__(self, participant_id: str, logger: logging.Logger) -> None:
        """
        Initialize the mock EEG headset interface.

        Args:
            participant_id (str): ID to use as folder name for saved data.
            logger (logging.Logger): Logger for recording information and errors.
        """
        self.logger = logger
        self._is_connected = False
        self._is_recording = False
        self._participant_id = participant_id
        self._data_folder_path = "data"
        self._save_dir_path = os.path.join(self._data_folder_path, participant_id)
        self._connection_attempts = 0
        self._max_attempts = 3
        self._annotations = []
        self._recording_start_time = 0

        # Create directories for data storage
        self._create_dir_if_not_exist(self._data_folder_path)
        self._create_dir_if_not_exist(self._save_dir_path)

        # Mock initialization of BrainAccess library
        self.logger.info("Initializing mock BrainAccess library...")
        self.logger.info("Note: This is a mock implementation. Actual EEG functionality requires ARM64 library.")

    def connect(self) -> bool:
        """
        Mock connection to the BrainAccess Halo headset.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        if self._is_connected:
            self.logger.info("Already connected to the headset (mock).")
            return True

        from eeg_config import PORT, USED_DEVICE
        self.logger.info(f"Attempting to connect to BrainAccess Halo on port {PORT}... (mock)")

        # Simulate connection process
        self._is_connected = True
        self.logger.info("Successfully connected to BrainAccess Halo! (mock)")
        return True

    def disconnect(self) -> None:
        """
        Mock disconnection from the BrainAccess Halo headset.
        """
        if not self._is_connected:
            self.logger.info("Not connected to any headset.")
            return

        if self._is_recording:
            self.stop_recording()

        self._is_connected = False
        self.logger.info("Disconnected from BrainAccess Halo. (mock)")

    def start_recording(self, filepath: str) -> bool:
        """
        Mock start recording EEG data.

        Args:
            filepath (str): Path where data will be saved.

        Returns:
            bool: True if recording started successfully, False otherwise.
        """
        if not self._is_connected:
            if not self.connect():
                self.logger.error("Cannot start recording: Failed to connect to the headset.")
                return False

        if self._is_recording:
            self.logger.warning("Called start_recording when already recording. Forcing stop of previous one.")
            self.stop_recording()

        try:
            self.logger.info("Starting EEG data acquisition... (mock)")
            self._is_recording = True
            self._session_name = os.path.basename(filepath)
            self._filepath = filepath
            self._recording_start_time = time.time()

            self._annotate_internal("Recording started (mock)")

            self.logger.info(f"Recording started: {filepath} (mock)")
            return True
        except Exception as e:
            self.logger.error(f"Error starting recording: {str(e)}")
            return False

    def stop_recording(self) -> bool:
        """
        Mock stop recording and save simulated data.

        Returns:
            bool: True if data was saved successfully, False otherwise.
        """
        if not self._is_recording:
            self.logger.info("No active recording to stop.")
            return False

        try:
            self._annotate_internal("Recording ended (mock)")

            self.logger.info("Processing recorded data... (mock)")
            
            # Generate simulated EEG data
            from eeg_config import SAMPLING_RATE
            duration = 10  # seconds of simulated data
            n_channels = len([ch for ch in range(32)])  # Using the channel count from config
            n_samples = duration * SAMPLING_RATE
            
            # Create mock EEG data (random noise with some structure)
            mock_data = np.random.normal(0, 10, (n_channels, n_samples)).astype(np.float32)
            
            # Add some simulated signal patterns
            t = np.linspace(0, duration, n_samples)
            for i in range(min(n_channels, 4)):  # Add alpha waves to first 4 channels
                mock_data[i, :] += 5 * np.sin(2 * np.pi * 10 * t)  # 10Hz alpha waves
            
            # Create a mock MNE Raw object-like structure
            class MockRaw:
                def __init__(self, data, sfreq, ch_names):
                    self.data = data
                    self.info = {'sfreq': sfreq}
                    self.ch_names = ch_names
                
                def save(self, fname):
                    # Save the mock data to the specified file
                    import pickle
                    mock_data_dict = {
                        'data': self.data,
                        'sfreq': self.info['sfreq'],
                        'ch_names': self.ch_names,
                        'annotations': getattr(self, '_annotations', [])
                    }
                    Path(fname).parent.mkdir(parents=True, exist_ok=True)
                    with open(fname, 'wb') as f:
                        pickle.dump(mock_data_dict, f)
                    self.logger.info(f"Mock EEG data saved to {fname}")
            
            # Create mock raw object with channel names from config
            from eeg_config import channels
            ch_names = channels[:n_channels]  # Use appropriate number of channels
            raw_data = MockRaw(mock_data, SAMPLING_RATE, ch_names)
            raw_data._annotations = self._annotations
            raw_data.logger = self.logger

            if raw_data is not None:
                self.logger.info(f"Saving mock EEG data to {self._filepath}")
                raw_data.save(self._filepath)

                self.logger.info("Recording stopped and mock data saved successfully.")
            else:
                self.logger.warning("No data to save - get_mne() returned None")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}", exc_info=True)
            return False
        finally:
            # Always reset the recording state to prevent the experiment from getting stuck
            self._is_recording = False


    def annotate(self, annotation: str) -> None:
        """
        Add an annotation to the EEG data.

        Args:
            annotation (str): Annotation text to add.
        """
        self._annotate_internal(annotation)

    def _annotate_internal(self, annotation: str) -> None:
        """
        Internal method to add an annotation to the EEG data.

        Args:
            annotation (str): Annotation text to add.
        """
        if not self._is_connected:
            self.logger.warning(f"Cannot annotate '{annotation}': Not connected to the headset.")
            return

        try:
            timestamp = time.time() - self._recording_start_time if self._is_recording else 0
            # In mock, we just store the annotation
            self._annotations.append({"timestamp": timestamp, "annotation": annotation})
            self.logger.info(f"Annotation added: '{annotation}' at {timestamp:.2f}s")
        except Exception as e:
            self.logger.error(f"Error adding annotation: {str(e)}")

    def is_recording(self) -> bool:
        """Check if the headset is recording data"""
        return self._is_recording

    def is_acquiring(self) -> bool:
        """
        Check if the headset is acquiring data.
        For this class, recording and acquiring are the same state.
        """
        return self.is_recording()

    def _create_dir_if_not_exist(self, path: str) -> None:
        """
        Create a directory if it does not exist.

        Args:
            path (str): Directory path to create.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            self.logger.info(f"Created directory: {path}")