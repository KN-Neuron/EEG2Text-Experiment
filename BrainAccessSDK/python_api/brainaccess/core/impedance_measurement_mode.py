"""Modes to be used for impedance measurement"""
import enum


class ImpedanceMeasurementMode(enum.Enum):
    """
    Attributes
    ------------
    OFF
       No active impedance measurement
    HZ_7_8
        7.9 Hz wave
    HZ_31_2
        31.2 Hz wave
    DR_DIV4
        Wave frequency of sample_rate/4
    """
    OFF = 0
    HZ_7_8 = 1
    HZ_31_2 = 2
    DR_DIV4 = 3
