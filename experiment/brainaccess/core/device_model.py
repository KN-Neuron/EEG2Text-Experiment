import enum


class DeviceModel(enum.Enum):
    """Device model information

    Attributes
    ----------
    MINI_V2
        BrainAccess MINI V2
    MIDI
        BrainAccess MIDI (16 Channels)
    MAXI
        BrainAccess MAXI (32 Channels)
    EMG
        BrainAccess EMG
    HALO1
        BrainAccess Halo v1
    HALO
        BrainAccess Halo
    UNKNOWN
        Unknown device
    """
    MINI = 0
    MIDI = 1
    MAXI = 2
    EMG = 3
    HALO1 = 4
    HALO = 5
    UNKNOWN = 0xFF
