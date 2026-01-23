#!/usr/bin/env python3
"""
Test script to verify the existing eeg_headset.py implementation works with the BrainAccess SDK
"""

import logging
import sys
import os

# Add the project directory to Python path so it can find the brainaccess module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup basic logging for the test"""
    logger = logging.getLogger("TestEEG")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Console handler
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    return logger

def test_connection():
    """Test EEG headset connection"""
    logger = setup_logging()
    
    try:
        # Initialize and test the EEG headset
        from eeg_headset import EEGHeadset
        
        logger.info("Creating EEGHeadset instance...")
        headset = EEGHeadset(participant_id="test", logger=logger)
        
        logger.info("Attempting to connect to the headset...")
        connected = headset.connect()
        
        if connected:
            logger.info("Successfully connected to the EEG headset!")
            
            # Try to start recording
            logger.info("Starting recording...")
            recording_started = headset.start_recording("test_eeg_data.fif")
            
            if recording_started:
                logger.info("Recording started successfully!")
                
                # Add a test annotation
                headset.annotate("test_annotation")
                
                # Wait a moment
                import time
                time.sleep(2)
                
                # Stop recording
                logger.info("Stopping recording...")
                headset.stop_recording()
                logger.info("Recording stopped.")
            else:
                logger.error("Failed to start recording.")
                
            # Disconnect
            logger.info("Disconnecting from headset...")
            headset.disconnect()
            logger.info("Disconnected successfully.")
        else:
            logger.error("Failed to connect to the EEG headset.")
            
    except Exception as e:
        logger.error(f"Error during EEG headset test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set the library path for BrainAccess SDK
    os.environ['LD_LIBRARY_PATH'] = f"/home/grzesiek/EEG2Text-Experiment/experiment/BrainAccessSDK-linux:{os.environ.get('LD_LIBRARY_PATH', '')}"
    test_connection()