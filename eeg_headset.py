# eeg_headset.py

import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class EEGHeadset:
    """
    Handles connection and data acquisition from BrainAccess Halo 4-channel headset.
    """

    def __init__(self, participant_id: str, logger: logging.Logger) -> None:
        """
        Initialize the EEG headset interface.

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

        try:
            # Initialize BrainAccess library (SDK 3.5.0)
            self.logger.info("Initializing BrainAccess library...")
            from brainaccess.core.eeg_manager import EEGManager
            from brainaccess.utils import acquisition

            # W SDK 3.5.0 NIE używamy bacore.init() - po prostu importujemy klasy
            self.EEGManager = EEGManager
            self.acquisition = acquisition
        except ImportError:
            self.logger.error("BrainAccess library not installed. Use pip install brainaccess")
            raise

    def connect(self) -> bool:
        """
        Connect to the BrainAccess Halo headset.

        Returns:
            bool: True if connection was successful, False otherwise.
        """
        if self._is_connected:
            self.logger.info("Already connected to the headset.")
            return True

        from eeg_config import PORT, USED_DEVICE
        self.logger.info(f"Attempting to connect to BrainAccess Halo on port {PORT}...")

        while self._connection_attempts < self._max_attempts:
            try:
                self._eeg_manager = self.EEGManager()
                self._eeg_acquisition = self.acquisition.EEG()

                # Connect to the headset
                from eeg_config import DEVICE_NAME
                self._eeg_acquisition.setup(self._eeg_manager, device_name=DEVICE_NAME, cap=USED_DEVICE)

                # Check connection
                if self._eeg_manager.is_connected():
                    self._is_connected = True
                    self.logger.info("Successfully connected to BrainAccess Halo!")
                    return True

            except Exception as e:
                self._connection_attempts += 1
                self.logger.warning(
                    f"Connection attempt {self._connection_attempts} failed: {str(e)}"
                )
                self.logger.info(f"Retrying in {self._connection_attempts} seconds...")
                time.sleep(self._connection_attempts)

        self.logger.error("Failed to connect to the headset after multiple attempts.")
        self.logger.error("Please check that:")
        self.logger.error("1. The device is turned on and charged")
        self.logger.error("2. The device is within Bluetooth range")
        self.logger.error("3. The port configuration is correct")
        return False

    def disconnect(self) -> None:
        """
        Disconnect from the BrainAccess Halo headset.
        """
        if not self._is_connected:
            self.logger.info("Not connected to any headset.")
            return

        if self._is_recording:
            self.stop_recording()

        try:
            # Stop acquisition if it's running
            if hasattr(self, '_eeg_acquisition') and self._eeg_acquisition is not None:
                try:
                    self._eeg_acquisition.stop_acquisition()
                except:
                    pass  # Might already be stopped
                try:
                    self._eeg_acquisition.close()
                except:
                    pass  # Clean up as much as possible

            # Disconnect the manager
            if hasattr(self, '_eeg_manager') and self._eeg_manager is not None:
                self._eeg_manager.disconnect()

            self._is_connected = False
            self.logger.info("Disconnected from BrainAccess Halo.")
        except Exception as e:
            self.logger.error(f"Error disconnecting from the headset: {str(e)}")

    def start_recording(self, filepath: str) -> bool:
        """
        Start recording EEG data.

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
            self.logger.info("Starting EEG data acquisition...")
            self._eeg_acquisition.start_acquisition()
            self._is_recording = True
            self._session_name = os.path.basename(filepath)
            self._filepath = filepath
            self._recording_start_time = time.time()

            self._annotate_internal("Recording started")

            self.logger.info(f"Recording started: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error starting recording: {str(e)}")
            return False

    def stop_recording(self) -> bool:
        """
        Stop recording and save the data.

        Returns:
            bool: True if data was saved successfully, False otherwise.
        """
        if not self._is_recording:
            self.logger.info("No active recording to stop.")
            return False

        try:
            self._annotate_internal("Recording ended")

            self.logger.info("Processing recorded data...")
            raw_data = self._eeg_acquisition.get_mne()

            if raw_data is not None:
                self.logger.info(f"Saving EEG data to {self._filepath}")
                Path(self._filepath).parent.mkdir(parents=True, exist_ok=True)
                raw_data.save(self._filepath)

                # Also stop the acquisition
                self._eeg_acquisition.stop_acquisition()
                self._eeg_manager.clear_annotations()

                self.logger.info("Recording stopped and data saved successfully.")
            else:
                self.logger.warning("No data to save - get_mne() returned None")
                # Still stop the acquisition even if no data
                try:
                    self._eeg_acquisition.stop_acquisition()
                except:
                    pass
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}", exc_info=True)
            # Try to stop acquisition even if saving failed
            try:
                self._eeg_acquisition.stop_acquisition()
            except:
                pass
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
            self._eeg_acquisition.annotate(annotation)
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
