import ctypes
from enum import Enum
from brainaccess.core import _dll


class GainMode(Enum):
    """Gain mode multipliers

    Attributes
    ------------
    X4
        4x gain
    X6
        6x gain
    X8
        8x gain
    X12
        12x gain
    UNKNOWN
        OxFF gain

    """

    X4 = 2
    X6 = 3
    X8 = 4
    X12 = 5
    UNKNOWN = 0xFF


_dll.ba_gain_mode_to_multiplier.argtypes = [ctypes.c_uint8]
_dll.ba_gain_mode_to_multiplier.restype = ctypes.c_int


def gain_mode_to_multiplier(gain_mode: GainMode) -> int:
    """Converts gain mode to integer multiplier representing the gain mode

    Parameters
    ------------
    gain_mode: GainMode

    Returns
    -------
    int
        integer multiplier representing the gain mode (ex: X12 returns 12)
    """
    return _dll.ba_gain_mode_to_multiplier(ctypes.c_uint8(gain_mode.value))


_dll.ba_multiplier_to_gain_mode.argtypes = [ctypes.c_int]
_dll.ba_multiplier_to_gain_mode.restype = ctypes.c_uint8


def multiplier_to_gain_mode(multiplier: int) -> GainMode:
    """Converts multiplier to the gain mode

    Parameters
    ------------
    multiplier: int

    Returns
    -------
    GainMode
    """
    return GainMode(_dll.ba_multiplier_to_gain_mode(ctypes.c_int(multiplier)))
