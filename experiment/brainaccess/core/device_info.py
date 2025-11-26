import ctypes
from brainaccess.core.version import Version
from brainaccess.core.device_model import DeviceModel


class DeviceInfo(ctypes.Structure):
    """Object containing device information

    Attributes
    ----------

    id
        Device model number
    hardware_version
        Hardware version
    firmware_version
        Firmware version
    serial_number
        Device serial number
    """
    _fields_ = [
        ("_device_model", ctypes.c_uint8),
        ("hardware_version", Version),
        ("firmware_version", Version),
        ("serial_number", ctypes.c_size_t),
    ]

    @property
    def device_model(self):
        return DeviceModel(self._device_model)

    @device_model.setter
    def device_model(self, val):
        self._device_model = ctypes.c_uint8(val.value)
