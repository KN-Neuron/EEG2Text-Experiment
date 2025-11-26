import time

from brainaccess.core.eeg_manager import EEGManager
from brainaccess.utils import acquisition

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

eeg_acquisition.setup(eeg_manager, device_name=device_name, cap=device_dict)

eeg_acquisition.start_acquisition()

# time.sleep(2)

print("Acquiring EEG data...")

for _ in range(5):
    eeg_acquisition.annotate("test")

    time.sleep(1)

eeg_acquisition.get_mne()
eeg_acquisition.stop_acquisition()

eeg_acquisition.data.save("eeg_data.raw.fif")

eeg_manager.disconnect()
eeg_manager.destroy()

eeg_acquisition.close()

print("Done.")