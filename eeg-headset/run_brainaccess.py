#!/usr/bin/env python3
"""
Wrapper script for BrainAccess EEG application
This script sets the proper library path before importing brainaccess modules
"""

import os
import sys

# Add the BrainAccess SDK libraries to the library path
sdk_path = os.path.join(os.path.dirname(__file__), "BrainAccessSDK-linux")
if os.path.exists(sdk_path):
    # On Linux, we need to set LD_LIBRARY_PATH
    current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
    if current_ld_path:
        os.environ['LD_LIBRARY_PATH'] = f"{sdk_path}:{current_ld_path}"
    else:
        os.environ['LD_LIBRARY_PATH'] = sdk_path
else:
    print(f"Error: BrainAccess SDK path not found: {sdk_path}")
    sys.exit(1)

# Now import and run the main application
from brainaccess.utils import acquisition
import brainaccess.core as bacore
from brainaccess.core.eeg_manager import EEGManager
import time
import signal


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
    bacore.init(bacore.Version(2, 0, 0))
    print('BrainAccess core initialized')

    eeg_manager = EEGManager()
    eeg_acquisition = acquisition.EEG()

    device_name = "BA MAXI 012"

    channels = [
        "P8",
        "O2",
        "P4",
        "C4",
        "F8",
        "F4",
        "Oz",
        "Cz",
        "Fz",
        "Pz",
        "F3",
        "O1",
        "P7",
        "C3",
        "P3",
        "F7",
        "T8",
        "FC6",
        "CP6",
        "CP2",
        "PO4",
        "FC2",
        "AF4",
        "POz",
        "AFz",
        "AF3",
        "FC1",
        "FC5",
        "T7",
        "CP1",
        "CP5",
        "PO3",
    ]

    device_dict = {idx: channel for idx, channel in enumerate(channels)}

    print(f'Attempting to connect to device: {device_name}...')

    try:
        eeg_acquisition.setup(eeg_manager, device_name=device_name, cap=device_dict)
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

    print("Acquiring EEG data...")

    for i in range(5):
        try:
            eeg_acquisition.annotate(f"test_{i}")
            print(f"Annotation {i} completed")
            time.sleep(1)
        except Exception as e:
            print(f"Error during acquisition loop: {e}")
            break

    # Get and save data
    try:
        raw_data = eeg_acquisition.get_mne()
        eeg_acquisition.stop_acquisition()
        eeg_acquisition.data.save("eeg_data.raw.fif")
        print("Data acquired and saved successfully")
    except Exception as e:
        print(f"Error during data acquisition or saving: {e}")

    # Cleanup
    try:
        eeg_acquisition.close()
        eeg_manager.disconnect()
        eeg_manager.destroy()
        print("Cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
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

print("Done.")