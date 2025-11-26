import ctypes

from brainaccess.core import _dll
from brainaccess.core.device_info import DeviceInfo
from brainaccess.utils.exceptions import BrainAccessException

# has_gyro()
_dll.ba_core_device_features_has_gyro.argtypes = [ctypes.c_void_p]
_dll.ba_core_device_features_has_gyro.restype = ctypes.c_bool

# has_accel()
_dll.ba_core_device_features_has_accel.argtypes = [ctypes.c_void_p]

_dll.ba_core_device_features_has_accel.restype = ctypes.c_bool

# is_bipolar()
_dll.ba_core_device_features_is_bipolar.argtypes = [ctypes.c_void_p]
_dll.ba_core_device_features_is_bipolar.restype = ctypes.c_bool

# electrode_count()
_dll.ba_core_device_features_electrode_count.argtypes = [ctypes.c_void_p]
_dll.ba_core_device_features_electrode_count.restype = ctypes.c_uint8

# device_features_get()
_dll.ba_core_device_features_get.argtypes = [ctypes.POINTER(DeviceInfo)]
_dll.ba_core_device_features_get.restype = ctypes.c_void_p


class DeviceFeatures:
    """The DeviceFeatures class allowing the user to check what features a
    particular device supports.
    """

    def __init__(self, device_info):
        """Gets an instance of DeviceFeatures for the corresponding DeviceInfo
        class.

        Parameters
        ----------
        device_info: DeviceInfo
            Device for which to get features. Serial number is ignored.
        """
        self.handle = _dll.ba_core_device_features_get(ctypes.pointer(device_info))
        if self.handle == None:
            raise BrainAccessException("Unknown device")

    def has_gyro(self) -> bool:
        """Whether or not the device can capture gyroscope data.

        Returns
        -------
        bool
            True if device has a gyroscope, False otherwise
        """
        return _dll.ba_core_device_features_has_gyro(self.handle)

    def has_accel(self) -> bool:
        """Whether or not the device can capture accelerometer data.

        Returns
        -------
        bool
            True if device has an accelerometer, False otherwise
        """
        return _dll.ba_core_device_features_has_accel(self.handle)

    def is_bipolar(self) -> bool:
        """Whether or not the device's electrodes are bipolar.
        Bipolar electrodes have separate P (positive) and N (negative) contacts.

        Returns
        -------
        bool
            True if electrodes are bipolar, False otherwise
        """
        return _dll.ba_core_device_features_is_bipolar(self.handle)

    def electrode_count(self) -> int:
        """Gets the number of EEG/EMG electrodes supported by the device.

        Returns
        -------
        int
            Number of electrodes
        """
        return _dll.ba_core_device_features_electrode_count(self.handle)
