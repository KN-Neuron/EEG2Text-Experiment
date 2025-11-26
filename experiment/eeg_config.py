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

BRAINACCESS_HALO_4_CHANNEL = {idx: channel for idx, channel in enumerate(channels)}


DEVICE_NAME = "BA MAXI 012"  # Common name for BrainAccess Halo headset, change if your device has a different name
PORT = "/dev/rfcomm0"

SAMPLING_RATE = 250

DATA_FOLDER_PATH = "eeg_data"

USED_DEVICE = BRAINACCESS_HALO_4_CHANNEL
