""" EEG measurement example

Example how to get measurements and
save to fif format
using acquisition class from brainaccess.utils

Change Bluetooth device name (line 23)
"""

import matplotlib.pyplot as plt
import matplotlib
import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

matplotlib.use("TKAgg", force=True)

eeg = acquisition.EEG()

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

cap = {idx: channel for idx, channel in enumerate(channels)}


# define device name
device_name = "BA MAXI 012"  # Common name for BrainAccess Halo headset, change if your device has a different name

# start EEG acquisition setup
with EEGManager() as mgr:
    eeg.setup(mgr, device_name=device_name, cap=cap, sfreq=250)

    # Start acquiring data
    eeg.start_acquisition()
    print("Acquisition started")
    time.sleep(3)

    start_time = time.time()
    annotation = 1
    while time.time() - start_time < 10:
        time.sleep(1)
        # send annotation to the device
        print(f"Sending annotation {annotation} to the device")
        eeg.annotate(str(annotation))
        annotation += 1

    print("Preparing to plot data")
    time.sleep(2)

    # get all eeg data and stop acquisition
    eeg.get_mne()
    eeg.stop_acquisition()
    mgr.disconnect()

# save EEG data to MNE fif format
eeg.data.save(f'{time.strftime("%Y%m%d_%H%M")}-raw.fif')
# Close brainaccess library
eeg.close()
# Show recorded data
eeg.data.mne_raw.filter(1, 40).plot(scalings="auto", verbose=False)
plt.show()