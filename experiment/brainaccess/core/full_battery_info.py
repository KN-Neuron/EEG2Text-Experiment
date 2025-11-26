import ctypes
from enum import Enum, unique

from brainaccess.utils.exceptions import BrainAccessException


@unique
class EBaChargeStates(Enum):
    e_ba_charge_states_unknown = 0
    e_ba_charge_states_charging = 1
    e_ba_charge_states_discharging_active = 2
    e_ba_charge_states_discharging_inactive = 3
    e_ba_charge_states_last = 4


@unique
class EBaChargeLevel(Enum):
    e_ba_charge_level_unknown = 0
    e_ba_charge_level_good = 1
    e_ba_charge_level_low = 2
    e_ba_charge_level_critical = 3
    e_ba_charge_level_last = 4


class FullBatteryInfo(ctypes.Structure):
    """Object containing extended battery information
    Attributes
    ----------
    is_charger_connected
        True if charger is connected to the device
    level
        Battery charge percentage, 0-100
    health
        Battery health percentage, 0-100
    voltage
        Battery voltage in volts
    current
        Current flow in amps (negative means discharge)
    charge_state

    """

    _fields_ = [
        ("is_charger_connected", ctypes.c_bool),
        ("level", ctypes.c_uint8),
        ("health", ctypes.c_float),
        ("voltage", ctypes.c_float),
        ("current", ctypes.c_float),
        ("charge_state", ctypes.c_int),
        ("charge_level", ctypes.c_int),
    ]

    @property
    def charging_state(self):
        return EBaChargeStates(self._charging_state)

    @charging_state.setter
    def charging_state(self, value):
        if isinstance(value, EBaChargeStates):
            self._charging_state = value.value
        else:
            raise BrainAccessException("charging_state must be an instance of EBaChargeStates Enum")

    @property
    def charge_level(self):
        return EBaChargeLevel(self._charge_level)

    @charge_level.setter
    def charge_level(self, value):
        if isinstance(value, EBaChargeLevel):
            self._charge_level = value.value
        else:
            raise BrainAccessException("charge_level must be an instance of EBaChargeLevel Enum")
