import ctypes
import warnings
from multimethod import multimethod
from brainaccess.utils.exceptions import _handle_error_bacore, BrainAccessException
from brainaccess.core.log_level import LogLevel
from brainaccess.libload import load_library

_dll = load_library("bacore")

from brainaccess.core.version import Version  # noqa: E402

# init()
_dll.ba_core_init.argtypes = []
_dll.ba_core_init.restype = ctypes.c_uint8
# close()
_dll.ba_core_close.argtypes = []
_dll.ba_core_close.restype = None
# get_version()
_dll.ba_core_get_version.argtypes = []
_dll.ba_core_get_version.restype = ctypes.POINTER(Version)
# get_device_count()
_dll.ba_core_device_count.argtypes = []
_dll.ba_core_device_count.restype = ctypes.c_uint8
# get_device_name()
_dll.ba_core_device_get_name.argtypes = [ctypes.c_char_p, ctypes.c_int]
_dll.ba_core_device_get_name.restype = None
# get_device_address()
_dll.ba_core_device_get_address.argtypes = [ctypes.c_char_p, ctypes.c_int]
_dll.ba_core_device_get_address.restype = None
# scan()
_dll.ba_core_scan.argtypes = [ctypes.c_uint8]
_dll.ba_core_scan.restype = ctypes.c_uint8
# config_set_log_level()
_dll.ba_core_config_set_log_level.argtypes = [ctypes.c_uint8]
_dll.ba_core_config_set_log_level.restype = ctypes.c_uint8
# config_set_chunk_size()
_dll.ba_core_config_set_chunk_size.argtypes = [ctypes.c_int]
_dll.ba_core_config_set_chunk_size.restype = ctypes.c_uint8
# config_enable_logging()
_dll.ba_core_config_enable_logging.argtypes = [ctypes.c_bool]
_dll.ba_core_config_enable_logging.restype = ctypes.c_uint8
# set_config_path()
_dll.ba_core_set_core_log_path.argtypes = [ctypes.c_char_p, ctypes.c_bool, ctypes.c_int]
_dll.ba_core_set_core_log_path.restype = ctypes.c_uint8
# set_config_timestamp()
_dll.ba_core_config_timestamp.argtypes = [ctypes.c_bool]
_dll.ba_core_config_timestamp.restype = ctypes.c_uint8
# set_config_autoflush()
_dll.ba_core_config_autoflush.argtypes = [ctypes.c_bool]
_dll.ba_core_config_autoflush.restype = ctypes.c_uint8
# set_config_thread_id()
_dll.ba_core_config_thread_id.argtypes = [ctypes.c_int]
_dll.ba_core_config_thread_id.restype = ctypes.c_uint8
# set_config_update_path()
_dll.ba_core_config_set_update_path.argtypes = [ctypes.c_char_p]
_dll.ba_core_config_set_update_path.restype = ctypes.c_uint8


@multimethod
def init() -> bool:
    """Initializes the library

    This function reads the config file, starts logging, etc.

    Returns
    --------
    bool
        True if successful otherwise raises a RuntimeError

    Raises
    -------
    BrainAccessException if initialization fails

    Warning
    -------
    Must bet called before any other BrainAccess Core library function. Only call once.
    """
    return _handle_error_bacore(_dll.ba_core_init())


@multimethod
def init(expected_version: Version) -> bool:
    """Initializes the library
    DEPRECATED: Use init() instead, version is not needed anymore during initialization

    This function reads the config file, starts logging, etc.

    Parameters
    -----------
    version
        The version of the library that the application expects.

    Returns
    --------
    bool
        True if successful otherwise raises a RuntimeError

    Raises
    -------
    BrainAccessException if initialization fails

    Warning
    -------
    Must bet called before any other BrainAccess Core library function. Only call once.
    """
    warnings.warn(
        "Version is not needed anymore during initialization", DeprecationWarning
    )
    return init()


def close() -> None:
    """Closes the library and cleans up afterwards.

    Warning
    --------
    Must be called after all BrainAccess Core library functions used by the application.
    Only call once.
    If initialization failed, do not call this function.
    """
    _dll.ba_core_close()


def get_version() -> Version:
    """Returns the installed library's actual version"""
    return _dll.ba_core_get_version()[0]


def get_device_count() -> int:
    """Returns the number of devices connected to the computer"""
    return _dll.ba_core_device_count()


def get_device_name(device_index: int) -> str:
    """Returns the name of the device at the given index"""
    name_buffer = ctypes.create_string_buffer(20)
    _dll.ba_core_device_get_name(name_buffer, device_index)
    return name_buffer.value.decode("utf-8")


def get_device_address(device_index: int) -> str:
    """Returns the address of the device at the given index"""
    address = ctypes.create_string_buffer(20)
    _dll.ba_core_device_get_address(address, device_index)
    return address.value.decode("utf-8")


def scan(adapter_index: int = 0) -> bool:
    """Scans for devices for the given amount of time

    Parameters
    -----------
    adapter_index: int (default: 0)
        The index of the Bluetooth adapter to use

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if scanning fails

    """
    return _handle_error_bacore(_dll.ba_core_scan(adapter_index))


def config_set_log_level(log_level: LogLevel) -> bool:
    """Sets the log level

    Parameters
    -----------
    log_level: LogLevel
        The log level to set

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if log level is invalid

    """
    return _handle_error_bacore(_dll.ba_core_config_set_log_level(log_level.value))


def config_set_chunk_size(chunk_size: int) -> bool:
    """Sets the chunk size

    Parameters
    -----------
    chunk_size: int
        The chunk size to set

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if chunk size is invalid

    """
    err = _dll.ba_core_config_set_chunk_size(chunk_size)
    if err == 0:
        return True
    elif err == 1:
        raise BrainAccessException("Chunk size is invalid")
    else:
        raise BrainAccessException("Unknown error")


def config_enable_logging(enable: bool) -> bool:
    """Enables or disables logging

    Parameters
    -----------
    enable: bool
        True to enable logging, False to disable

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if logging cannot be enabled

    """
    err = _dll.ba_core_config_enable_logging(enable)
    if err == 0:
        return True
    elif err == 1:
        raise BrainAccessException("Cannot enable logging")
    else:
        raise BrainAccessException("Unknown error")


def set_config_path(
    file_path: str, append: bool = True, buffer_size: int = 512
) -> bool:
    """Sets the path for the core log file

    Parameters
    -----------
    file_path
        The path to the log file
    append
        If True, the log file will be appended
    buffer_size
        The size of the buffer

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if log file path cannot be set
    """
    file = ctypes.create_string_buffer(file_path.encode("utf-8"))
    err = _dll.ba_core_set_core_log_path(file, append, buffer_size)
    if err == 0:
        return True
    elif err == 1:
        raise BrainAccessException("Cannot set log file path")
    else:
        raise BrainAccessException("Unknown error")


def set_config_timestamp(enable: bool = True) -> bool:
    """Enables or disables timestamps in the log file

    Parameters
    -----------
    enable
        True to enable timestamps, False to disable

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if timestamp cannot be set

    """
    err = _dll.ba_core_config_timestamp(enable)
    if err == 0:
        return True
    else:
        raise BrainAccessException("Failed to set timestamp")


def set_config_autoflush(enable: bool = True) -> bool:
    """Enables or disables autoflush in the log file

    Parameters
    -----------
    enable
        True to enable autoflush, False to disable

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if autoflush cannot be set
    """
    err = _dll.ba_core_config_autoflush(enable)
    if err == 0:
        return True
    else:
        raise BrainAccessException("Failed to set autoflush")


def set_config_thread_id(enable: bool = True) -> bool:
    """Enables or disables thread id in the log file

    Parameters
    -----------
    enable
        True to enable thread id, False to disable

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException

    Raises
    -------
    BrainAccessException if thread id cannot be set

    """
    err = _dll.ba_core_config_thread_id(enable)
    if err == 0:
        return True
    else:
        raise BrainAccessException("Failed to set thread id")


def set_config_update_path(file_path: str) -> bool:
    """Sets the path for the update file

    Parameters
    -----------
    file_path
        The path to the update file

    Returns
    --------
    bool
        True if successful otherwise raises a BrainAccessException
    """
    file = ctypes.create_string_buffer(file_path.encode("utf-8"))
    return _handle_error_bacore(_dll.ba_core_config_set_update_path(file))
