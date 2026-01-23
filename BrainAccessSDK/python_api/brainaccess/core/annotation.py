import ctypes


class Annotation(ctypes.Structure):
    """Object containing annotation information

    Attributes
    ------------
    timestamp
        Sample number corresponding to the time the annotation was recorded
    annotation
        Annotation text

    """
    _fields_ = [
        ("timestamp", ctypes.c_size_t),
        ("_annotation", ctypes.c_char_p),
    ]

    @property
    def annotation(self):
        return self._annotation.decode('ascii')
