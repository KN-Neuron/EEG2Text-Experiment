import ctypes
import numpy as np

from brainaccess.connect import _dll
from brainaccess.utils.exceptions import BrainAccessException

# ctypes

_dll.ba_bci_connect_p300_init.argtypes = [
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.c_uint8
]
_dll.ba_bci_connect_p300_init.restype = ctypes.c_uint8

_dll.ba_bci_connect_p300_predict.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_double)
]
_dll.ba_bci_connect_p300_predict.restype = ctypes.c_uint8

_dll.ba_bci_connect_p300_free.argtypes = [
    ctypes.c_void_p
]
_dll.ba_bci_connect_p300_free.restype = None


class P300:
    """P300 BCI library"""

    def __init__(self, model_number: int) -> None:
        """Initialize P300 model.

        Parameters
        ------------
        model_number: int
            Model type to load, currently available:
            0 - 8 electrode Standard Kit setup, 1 repetitions
            1 - 8 electrode Standard Kit setup, 3 repetition
            2 - 8 electrode Standard Kit setup, 3 repetitions, "fast" - inter trial interval is 215ms
            3 - O1 and O2 electrodes only, 3 repetitions, "fast" - inter trial interval is 215ms
        Raises
        -------
        Exception
            An error is raised if initializing failed

        """
        self._p300 = ctypes.c_void_p()
        self.model_number: int = model_number
        self.reps = 3 if model_number in [1, 2, 3] else 1
        self.n_channels = 8 if model_number in [0, 1, 2] else 2
        err = _dll.ba_bci_connect_p300_init(ctypes.pointer(self._p300), model_number)
        if err != 0:
            raise BrainAccessException("P300 model failed to load")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.destroy()

    def destroy(self) -> None:
        _dll.ba_bci_connect_p300_free(self._p300)

    def predict(self, x: np.ndarray) -> float:
        """Predict P300

        Parameters
        ------------
        x: np.ndarray
            data for classifier

        Returns
        ---------
        float:
            probability that data was P300 event

        Raises
        -------
        Exception
            An error is raised if prediction failed

        Warnings
        ----------
        Data sampled at 250 Hz must have these properties:

        - standardized with ewma and filtered with 1-40 Hz filter
        - (8, 176 * repetitions) shape (channels x samples),
        - each repetition 200 ms prior to stimulus onset up to 500 ms after stimulus onset
        - Channels must be in exactly this order: F3, F4, C3, C4, P3, P4, O1, O2 (8 channels) or O1, O2 (2 channels)

        """
        nchans = x.shape[0]
        nsamples = x.shape[1]
        if nchans != self.n_channels:
            raise BrainAccessException(f"{self.n_channels} channels required")
        if nsamples != 176 * self.reps:
            raise BrainAccessException(f"{176 * self.reps} samples required")
        _x = x.copy().ravel(order="C").astype(np.double)
        c_arr = np.ctypeslib.as_ctypes(_x)
        _res = np.zeros(2).astype(np.double)
        c_res = np.ctypeslib.as_ctypes(_res)
        _error = _dll.ba_bci_connect_p300_predict(self._p300, c_arr, c_res)
        if _error != 0:
            raise BrainAccessException("P300 prediction failed")
        return np.array(c_res)[1]
