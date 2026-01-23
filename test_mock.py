#!/usr/bin/env python3
"""
Test script to run the EEG application with the mock library.
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting EEG2Text Experiment with mock library...")
    
    # Temporarily replace the import of eeg_headset with the mock version
    import importlib.util
    
    # Load the mock version
    mock_spec = importlib.util.spec_from_file_location("eeg_headset", "./eeg_headset_mock.py")
    mock_module = importlib.util.module_from_spec(mock_spec)
    mock_spec.loader.exec_module(mock_module)
    
    # Replace the module in sys.modules
    import sys
    sys.modules['eeg_headset'] = mock_module
    
    try:
        # Now import and use the mock version
        from eeg_headset import EEGHeadset
        
        # Create an instance
        headset = EEGHeadset(participant_id="test_participant", logger=logger)
        
        # Test the functionality
        logger.info("Testing EEG headset connection...")
        connected = headset.connect()
        logger.info(f"Connected: {connected}")
        
        logger.info("Testing EEG headset recording...")
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.fif', delete=False) as tmp_file:
            temp_filename = tmp_file.name
        
        started = headset.start_recording(temp_filename)
        logger.info(f"Started recording: {started}")
        
        # Wait a bit
        import time
        time.sleep(2)
        
        # Add an annotation
        headset.annotate("Test annotation")
        
        # Stop recording
        stopped = headset.stop_recording()
        logger.info(f"Stopped recording: {stopped}")
        
        # Disconnect
        headset.disconnect()
        
        logger.info("Test completed successfully with mock library!")
        print("SUCCESS: Application ran with mock library")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nThe application ran successfully with the mock library!")
        print("\nNext steps:")
        print("1. Contact BrainAccess support for an ARM64 version of libbacore.so")
        print("2. Once you receive the ARM64 library, replace the mock with the real implementation")
        print("3. For now, you can continue development using this mock version")
    else:
        print("\nThe application failed to run with the mock library.")
        sys.exit(1)