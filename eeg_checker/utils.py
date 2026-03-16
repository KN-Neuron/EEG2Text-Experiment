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

HIGHPASS_FREQUENCY = 1  # Removes DC offset and slow drifts
LOWPASS_FREQUENCY = 40  # Removes high frequency noise (BrainAccess recommends 1-40 Hz)
SAMPLING_FREQUENCY = 250
MAX_FREQUENCY = SAMPLING_FREQUENCY // 2


def preprocess_data(file_to_check, apply_filter=True):
    """Load and preprocess EEG data from a FIF file.
    
    Args:
        file_to_check: Path to the FIF file (relative to data folder or absolute)
        apply_filter: Whether to apply bandpass filtering (default: True)
    
    Returns:
        MNE Raw object with preprocessed data
    """
    # Handle both relative and absolute paths
    file_path = Path(file_to_check)
    if not file_path.is_absolute():
        file_path = Path.cwd().parent / "data" / file_to_check
    
    raw_data = mne.io.read_raw_fif(file_path, preload=True, verbose=False)
    
    # Pick only EEG channels (exclude misc, syst channels)
    raw_data.pick(CHANNELS, verbose=False)
    
    if apply_filter:
        # Apply bandpass filter: as recommended by BrainAccess (1-40 Hz)
        raw_data.filter(l_freq=HIGHPASS_FREQUENCY, h_freq=LOWPASS_FREQUENCY, verbose=False)
    
    return raw_data
