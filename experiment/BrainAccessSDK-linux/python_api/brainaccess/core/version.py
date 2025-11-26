import ctypes
from brainaccess.core import _dll


class Version(ctypes.Structure):
    """Object describing version numbers

    Attributes
    ----------
    major
        API-breaking changes
    minor
        Feature updates
    patch
        Bugfixes
    """

    _fields_ = [
        ("major", ctypes.c_uint8),
        ("minor", ctypes.c_uint8),
        ("patch", ctypes.c_uint8),
    ]

    def __init__(self, major, minor, patch):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __repr__(self):
        return "{0}.{1}.{2}".format(self.major, self.minor, self.patch)


_dll.ba_is_version_compatible.argtypes = [
    ctypes.POINTER(Version),
    ctypes.POINTER(Version),
]
_dll.ba_is_version_compatible.restype = ctypes.c_bool


def is_version_compatible(expected: str, actual: str) -> bool:
    """Check if versions are compatible

    Parameters
    -----------
    expected: str
    actual: str

    Returns
    --------
    bool
        True if compatible
    """
    return _dll.ba_is_version_compatible(
        ctypes.pointer(expected), ctypes.pointer(actual)
    )
