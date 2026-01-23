import ctypes
import numpy as np

from brainaccess.connect import _dll
from brainaccess.utils.exceptions import BrainAccessException

# ctypes

_dll.ba_bci_connect_ssvep_classify.argtypes = [
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.c_double,
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_double),
]
_dll.ba_bci_connect_ssvep_classify.restype = ctypes.c_int


class SSVEP:
    """SSVEP BCI library"""

    def __init__(self, frequencies: list = [], sample_rate: float = 250) -> None:
        """Initialize SSVEP model

        Parameters
        ------------
        frequencies: list
            list of stimulation frequencies

        sample_rate: float
            data sampling rate

        """
        self.frequencies = np.array(frequencies)
        self.sample_rate = sample_rate

    def predict(
        self, x: np.ndarray, frequencies: list = None, sample_rate: float = None
    ) -> tuple:
        """Classify EEG SSVEP (steady state visually evoked potentials) given a set of class frequencies

        Parameters
        ------------
        x: np.ndarray
            EEG data (channels x samples) for classifier
        frequencies: list
            list of stimulation frequencies
        sample_rate: float
            data sampling rate

        Returns
        ---------
        float:
            target frequency
        float:
            target threshold value

        Raises
        -------
        Exception
            An error is raised if prediction failed

        Warnings
        ----------
        Data must have these properties:

        - filtered with 1-90 Hz filter
        - selected channels must be from ocipital region

        """
        if frequencies is not None:
            self.frequencies = np.array(frequencies)
        if sample_rate is not None:
            self.sample_rate = sample_rate
        _x = x.copy().ravel(order="C").astype(np.float64)
        c_arr = np.ctypeslib.as_ctypes(_x)
        freqs = np.ctypeslib.as_ctypes(self.frequencies.astype(np.float64))
        score = np.ctypeslib.as_ctypes(np.zeros(1).astype(np.float64))
        n_chans = x.shape[0]
        n_time_steps = x.shape[1]
        res = _dll.ba_bci_connect_ssvep_classify(
            c_arr,
            n_time_steps,
            n_chans,
            self.sample_rate,
            freqs,
            len(self.frequencies),
            score,
        )
        # if res != 0:
        #     raise BrainAccessException("SSVEP prediction failed")
        return res, score[0]
