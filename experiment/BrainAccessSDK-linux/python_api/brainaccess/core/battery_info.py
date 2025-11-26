import ctypes


class BatteryInfo(ctypes.Structure):
    """Object containing standard battery information

    Attributes
    -----------
    level
        Battery charge percentage, 0-100
    is_charger_connected
        True if charger is connected to the device
    is_charging
        True if battery is charging

    """
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("is_charger_connected", ctypes.c_bool),
        ("is_charging", ctypes.c_bool),
    ]
