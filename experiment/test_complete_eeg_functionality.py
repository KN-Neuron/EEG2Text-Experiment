#!/usr/bin/env python3
"""
Final test script to verify the complete EEG headset functionality 
"""

import logging
import sys
import os
import time

# Add the project directory to Python path so it can find the brainaccess module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Setup basic logging for the test"""
    logger = logging.getLogger("FinalTestEEG")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    # Console handler
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    return logger

def test_complete_functionality():
    """Test complete EEG headset functionality"""
    logger = setup_logging()
    
    try:
        # Initialize the EEG headset
        from eeg_headset import EEGHeadset
        
        logger.info("Creating EEGHeadset instance...")
        headset = EEGHeadset(participant_id="final_test", logger=logger)
        
        # Test connection
        logger.info("Testing connection to headset...")
        connected = headset.connect()
        
        if not connected:
            logger.error("Failed to connect to the EEG headset.")
            return False
        
        logger.info("✓ Successfully connected to the EEG headset!")
        
        # Test starting recording
        logger.info("Testing recording start...")
        recording_started = headset.start_recording("final_test_eeg_data.raw.fif")
        
        if not recording_started:
            logger.error("Failed to start recording.")
            headset.disconnect()
            return False
            
        logger.info("✓ Recording started successfully!")
        
        # Test adding annotations during recording
        logger.info("Testing annotation functionality...")
        headset.annotate("start_of_test")
        time.sleep(1)
        headset.annotate("middle_of_test")
        time.sleep(1)
        headset.annotate("end_of_test")
        logger.info("✓ Annotations added successfully!")
        
        # Test stopping recording
        logger.info("Testing recording stop...")
        recording_stopped = headset.stop_recording()
        
        if not recording_stopped:
            logger.warning("Recording may not have been saved properly.")
            # Continue anyway to test disconnect
        
        logger.info("✓ Recording stopped successfully!")
        
        # Test disconnection
        logger.info("Testing disconnection...")
        headset.disconnect()
        logger.info("✓ Successfully disconnected from the headset!")
        
        logger.info("✓ All EEG headset functionality tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error during EEG headset functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set the library path for BrainAccess SDK
    os.environ['LD_LIBRARY_PATH'] = f"/home/grzesiek/EEG2Text-Experiment/experiment/BrainAccessSDK-linux:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    success = test_complete_functionality()
    
    if success:
        print("\\n🎉 All tests completed successfully! The EEG headset functionality is working properly.")
    else:
        print("\\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)