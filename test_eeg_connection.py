#!/usr/bin/env python3
"""
Test script to verify BrainAccess library import and connect to EEG headset
"""

import time
import signal
import sys
import os

# Add the project directory to Python path so it can find the brainaccess module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(sig, frame):
    print('\nExiting gracefully...')
    try:
        if 'eeg_acquisition' in globals():
            eeg_acquisition.stop_acquisition()
            eeg_acquisition.close()
        if 'eeg_manager' in globals():
            eeg_manager.disconnect()
            eeg_manager.destroy()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

try:
    # Initialize the brainaccess core
    import brainaccess.core as bacore
    bacore.init(bacore.Version(2, 0, 0))
    print('BrainAccess core initialized successfully')

    from brainaccess.core.eeg_manager import EEGManager
    from brainaccess.utils import acquisition

    eeg_manager = EEGManager()
    eeg_acquisition = acquisition.EEG()

    # Using the configuration from eeg_config.py
    from eeg_config import USED_DEVICE, PORT

    # Bluetooth serial port - may need to be adjusted based on your system

    print(f'Attempting to connect to device on port {PORT}...')

    try:
        eeg_acquisition.setup(eeg_manager, USED_DEVICE, port=PORT)
        print('Device setup successful')
    except Exception as e:
        print(f'Device setup failed: {e}')
        print('Make sure the EEG device is connected and the port is correct.')
        print('You may need to pair the device via Bluetooth and create the rfcomm connection.')
        sys.exit(1)

    try:
        eeg_acquisition.start_acquisition()
        print('Acquisition started successfully')
    except Exception as e:
        print(f'Acquisition start failed: {e}')
        print('Check if another application is using the device.')
        sys.exit(1)

    print("Acquiring EEG data for 5 seconds...")

    for i in range(5):
        try:
            eeg_acquisition.annotate(f"test_annotation_{i}")
            print(f"Annotation {i} completed")
            time.sleep(1)
        except Exception as e:
            print(f"Error during acquisition loop: {e}")
            break

    # Get and save data
    try:
        raw_data = eeg_acquisition.get_mne()
        eeg_acquisition.stop_acquisition()
        if raw_data is not None:
            raw_data.save("test_eeg_data.raw.fif")
            print("Data acquired and saved successfully as test_eeg_data.raw.fif")
        else:
            print("Warning: No EEG data acquired")
    except Exception as e:
        print(f"Error during data acquisition or saving: {e}")
        print(f"Exception details: {e}")

    # Cleanup
    try:
        eeg_acquisition.close()
        eeg_manager.disconnect()
        eeg_manager.destroy()
        print("Cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

except ImportError as e:
    print(f"Import error - BrainAccess library not found: {e}")
    print("Make sure the brainaccess module is in the Python path.")
except Exception as e:
    print(f"Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    # Try to clean up if possible
    try:
        if 'eeg_acquisition' in globals():
            eeg_acquisition.stop_acquisition()
            eeg_acquisition.close()
        if 'eeg_manager' in globals():
            eeg_manager.disconnect()
            eeg_manager.destroy()
    except:
        pass

print("Test completed.")