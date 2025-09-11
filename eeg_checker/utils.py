from pathlib import Path

import mne
import numpy as np

CHANNELS = [
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

VOLTS_IN_MICROVOLT = 10**-6
LOWPASS_FREQUENCY = 1
HIGHPASS_FREQUENCY = 50
SAMPLING_FREQUENCY = 250
MAX_FREQUENCY = SAMPLING_FREQUENCY // 2
BANDSTOP_FREQUENCY = np.arange(50, MAX_FREQUENCY, 50)


def preprocess_data(file_to_check):
    data_path = Path.cwd().parent / "data" / file_to_check
    raw_data = mne.io.read_raw_fif(data_path)
    raw_data.load_data()

    raw_data.pick(CHANNELS)
    raw_data.apply_function(fun=lambda x: x * VOLTS_IN_MICROVOLT)
    raw_data.filter(l_freq=LOWPASS_FREQUENCY, h_freq=HIGHPASS_FREQUENCY)
    raw_data.notch_filter(BANDSTOP_FREQUENCY)

    return raw_data
