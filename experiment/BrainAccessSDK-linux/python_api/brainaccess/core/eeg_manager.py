import ctypes
import warnings
import threading
import numpy as np
import copy
from multimethod import multimethod
from typing import Callable, Union, Optional

from brainaccess.utils.exceptions import _callback, _handle_error, BrainAccessException
from brainaccess.core import _dll
from brainaccess.core.battery_info import BatteryInfo
from brainaccess.core.device_info import DeviceInfo
from brainaccess.core.gain_mode import GainMode
from brainaccess.core.annotation import Annotation
from brainaccess.core.polarity import Polarity
from brainaccess.core.impedance_measurement_mode import ImpedanceMeasurementMode  # noqa
from brainaccess.core.device_features import DeviceFeatures


# ctypes
# new_eeg_manager
_dll.ba_eeg_manager_new.argtypes = []
_dll.ba_eeg_manager_new.restype = ctypes.c_void_p
# destructor
_dll.ba_eeg_manager_free.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_free.restype = None
# connect(port)
_dll.ba_eeg_manager_connect.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.CFUNCTYPE(None, ctypes.c_bool, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_connect.restype = ctypes.c_uint8
# is_connected()
_dll.ba_eeg_manager_is_connected.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_is_connected.restype = ctypes.c_bool
# disconnect()
_dll.ba_eeg_manager_disconnect.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_disconnect.restype = None
# start_stream()
_dll.ba_eeg_manager_start_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_start_stream.restype = ctypes.c_uint8
# stop_stream()
_dll.ba_eeg_manager_stop_stream.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_stop_stream.restype = ctypes.c_uint8
# is_streaming()
_dll.ba_eeg_manager_is_streaming.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_is_streaming.restype = ctypes.c_bool
# load_config()
_dll.ba_eeg_manager_load_config.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_load_config.restype = ctypes.c_uint8
# get_battery_info()
_dll.ba_eeg_manager_get_battery_info.argtypes = [
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_get_battery_info.restype = BatteryInfo
# set_channel_enabled()
_dll.ba_eeg_manager_set_channel_enabled.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_bool,
]
_dll.ba_eeg_manager_set_channel_enabled.restype = None
# set_channel_gain()
_dll.ba_eeg_manager_set_channel_gain.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_channel_gain.restype = None
# set_channel_bias()
_dll.ba_eeg_manager_set_channel_bias.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint16,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_channel_bias.restype = None
# set_impedance_mode()
_dll.ba_eeg_manager_set_impedance_mode.argtypes = [
    ctypes.c_void_p,
    ctypes.c_uint8,
]
_dll.ba_eeg_manager_set_impedance_mode.restype = None
# get_device_info()
_dll.ba_eeg_manager_get_device_info.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_get_device_info.restype = ctypes.POINTER(DeviceInfo)
# get_channel_index()
_dll.ba_eeg_manager_get_channel_index.argtypes = [ctypes.c_void_p, ctypes.c_uint16]
_dll.ba_eeg_manager_get_channel_index.restype = ctypes.c_size_t
# get_sample_frequency()
_dll.ba_eeg_manager_get_sample_frequency.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_get_sample_frequency.restype = ctypes.c_uint16
# set_callback_chunk()
_dll.ba_eeg_manager_set_callback_chunk.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(
        None,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_size_t,
        ctypes.c_void_p,
    ),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_chunk.restype = None
# set_callback_battery()
_dll.ba_eeg_manager_set_callback_battery.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.POINTER(BatteryInfo), ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_battery.restype = None
# set_callback_disconnect()
_dll.ba_eeg_manager_set_callback_disconnect.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_set_callback_disconnect.restype = None
# update firmware
_dll.ba_eeg_manager_start_update.argtypes = [
    ctypes.c_void_p,
    ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t),
    ctypes.c_void_p,
]
_dll.ba_eeg_manager_start_update.restype = ctypes.c_uint8
# annotate()
_dll.ba_eeg_manager_annotate.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
_dll.ba_eeg_manager_annotate.restype = ctypes.c_uint8
# get_annotations()
_dll.ba_eeg_manager_get_annotations.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(Annotation)),
    ctypes.POINTER(ctypes.c_size_t),
]
_dll.ba_eeg_manager_get_annotations.restype = None
# clear_annotations()
_dll.ba_eeg_manager_clear_annotations.argtypes = [ctypes.c_void_p]
_dll.ba_eeg_manager_clear_annotations.restype = None

# Stream size type info super secret function thingy
_dll.ba_eeg_manager_get_stream_channel_data_types.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.POINTER(ctypes.c_uint8)),
    ctypes.POINTER(ctypes.c_size_t),
]
_dll.ba_eeg_manager_get_stream_channel_data_types.restype = None


_managers_mtx = threading.Lock()
_managers: dict = dict()

_types_map = [
    ctypes.c_float,  # 0
    ctypes.c_uint8,  # 1
    ctypes.c_size_t,  # 2
    ctypes.c_double,  # 3
]


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _callback_stop_stream(data: ctypes.c_void_p) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_stop_stream_mix:
                cbk = mgr._callback_stop_stream
                if cbk is not None:
                    cbk()


@ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t)
def _callback_ota_update(data: ctypes.c_void_p, progress: int, total: int) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_ota_update_mtx:
                cbk = mgr._callback_ota_update
                if cbk is not None:
                    cbk(progress, total)


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _callback_start_stream(data: ctypes.c_void_p) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_start_stream_mix:
                cbk = mgr._callback_start_stream
                if cbk is not None:
                    cbk()


@ctypes.CFUNCTYPE(
    None, ctypes.POINTER(ctypes.c_void_p), ctypes.c_size_t, ctypes.c_void_p
)
def _callback_chunk(chunk_data, chunk_size, data) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_chunk_mtx:
                cbk = mgr._callback_chunk
                if cbk is not None:
                    # Get channel sizes and type information
                    types_ptr = ctypes.POINTER(ctypes.c_uint8)()
                    types_size = ctypes.c_size_t()
                    _dll.ba_eeg_manager_get_stream_channel_data_types(
                        data, ctypes.byref(types_ptr), ctypes.byref(types_size)
                    )
                    types = [_types_map[types_ptr[i]] for i in range(types_size.value)]

                    chunk_arrays = []
                    for i, ctype in enumerate(types):
                        data_pointer = ctypes.cast(
                            chunk_data[i], ctypes.POINTER(ctype * chunk_size)
                        )
                        np_array = np.ctypeslib.as_array(
                            data_pointer.contents, shape=(chunk_size,)
                        )
                        chunk_arrays.append(np_array)

                    cbk(chunk_arrays, chunk_size)


@ctypes.CFUNCTYPE(None, ctypes.POINTER(BatteryInfo), ctypes.c_void_p)
def _callback_battery(b_info, data) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_battery_mtx:
                cbk = mgr._callback_battery
                if cbk is not None:
                    cbk(copy.copy(b_info[0]))


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _callback_load_config(data) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_load_config_mtx:
                cbk = mgr._callback_load_config
                if cbk is not None:
                    cbk()


@ctypes.CFUNCTYPE(None, ctypes.c_void_p)
def _callback_disconnect(data) -> None:
    with _managers_mtx:
        mgr = _managers.get(data)
        if mgr is not None:
            with mgr._callback_disconnect_mtx:
                cbk = mgr._callback_disconnect
                if cbk is not None:
                    cbk()


class EEGManager:
    """The EEG manager is the primary tool for
    communicating with the BrainAccess device.
    """

    def __init__(self) -> None:
        """Creates an EEG Manager.

        Warning
        ---------
        Make sure the core library has been initialized first!
        """
        self.conenction_success: int = 0
        self._callback_chunk_mtx = threading.Lock()
        self._callback_battery_mtx = threading.Lock()
        self._callback_disconnect_mtx = threading.Lock()
        self._callback_start_stream_mtx = threading.Lock()
        self._callback_stop_stream_mtx = threading.Lock()
        self._callback_load_config_mtx = threading.Lock()
        self._callback_ota_update_mtx = threading.Lock()
        self._manager = _dll.ba_eeg_manager_new()
        with _managers_mtx:
            _managers[self._manager] = self

        self._callback_disconnect = lambda: None
        _dll.ba_eeg_manager_set_callback_disconnect(
            self._manager, _callback_disconnect, self._manager
        )

    def __enter__(self) -> "EEGManager":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.destroy()

    def destroy(self) -> None:
        """Destroys an EEG manager instance.

        Warning
        ---------
        Must be called exactly once, after the manager is no longer needed
        """
        self.disconnect()  # prevent callback deadlock by disconnecting first.
        with _managers_mtx:
            _dll.ba_eeg_manager_free(self._manager)
            del _managers[self._manager]

    def disconnect(self) -> None:
        """Disconnects the EEGManager from the EEG device, if connected"""
        _dll.ba_eeg_manager_disconnect(self._manager)

    def connect(self, bt_device_index: int = 0) -> int:
        """Connects the EEGManager to an EEG device

        Parameters
        ----------
        bt_device_index : int
            index of the device to connect in the scan list

        Returns
        -------
        int
            value:
            0 if the connection was successful,
            1 if connection failed,
            2 if connection is established but data stream is not compatible

        """
        cbk, _ = _callback()
        self.connection_success = _dll.ba_eeg_manager_connect(self._manager, bt_device_index, cbk, None)
        if self.connection_success == 2:
            warnings.warn("Stream is incompatible. Update the firmware.")
        return self.connection_success

    def is_connected(self) -> bool:
        """Checks if the EEGManager is currently connected to an EEG device

        Returns
        -------
        bool
            True if connected, False otherwise

        """
        return _dll.ba_eeg_manager_is_connected(self._manager)

    def start_stream(self, callback: Union[Callable, None] = None) -> bool:
        """Starts streaming data from the device

        Returns
        -------
        bool
            value: True if the stream was started successfully

        Raises
        -------
        BrainAccessException if the stream is already running
        or if the stream could not be started
        """
        if self.connection_success == 2:
            raise BrainAccessException("Stream is incompatible. Update the firmware.")
        if callback is not None:
            with self._callback_start_stream_mtx:
                self._callback_start_stream = callback
        else:
            with self._callback_start_stream_mtx:
                self._callback_start_stream = lambda: None

        if self.is_streaming():
            raise BrainAccessException("Stream already running")
        return _handle_error(
            _dll.ba_eeg_manager_start_stream(
                self._manager, _callback_start_stream, self._manager
            )
        )

    def stop_stream(self, callback: Union[Callable, None] = None) -> bool:
        """Stops streaming data from the device

        Returns
        -------
        bool
            value: True if the stream was stopped successfully

        Raises
        -------
        BrainAccessException if the stream is not running
        or if the stream could not be stopped
        """
        if callback is not None:
            with self._callback_stop_stream_mtx:
                self._callback_stop_stream = callback
        else:
            with self._callback_stop_stream_mtx:
                self._callback_stop_stream = lambda: None

        if not self.is_streaming():
            raise BrainAccessException("Stream not running")
        return _handle_error(
            _dll.ba_eeg_manager_stop_stream(self._manager, _callback_stop_stream, None)
        )

    def is_streaming(self) -> bool:
        """Checks if the device is streaming

        Returns
        -------
        bool
            True if the stream is active, False otherwise

        """
        return _dll.ba_eeg_manager_is_streaming(self._manager)

    def load_config(self, callback: Union[Callable, None] = None) -> None:
        """Loads the configuration of channel and other settings to the device"""
        if callback is not None:
            with self._callback_load_config_mtx:
                self._callback_load_config = callback
        else:
            with self._callback_load_config_mtx:
                self._callback_load_config = lambda: None

        _handle_error(
            _dll.ba_eeg_manager_load_config(
                self._manager, _callback_load_config, self._manager
            )
        )

    def get_battery_info(self) -> BatteryInfo:
        """Returns a structure containing standard battery information from the device

        Returns
        -------
        BatteryInfo
            Battery information from the EEG device
        """
        return _dll.ba_eeg_manager_get_battery_info(self._manager)

    def set_channel_enabled(self, channel: int, state: bool) -> None:
        """Enables or disables the channel on the device

        Warning
        ---------
        Enabled channels are reset by stream stop.
        Must be called with the appropriate arguments before every stream start

        Parameters
        -------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to enable/disable.
        state: bool
            True to enable channel, False to disable.

        Raises
        -------
        BrainAccessException if device is streaming

        """
        if self.is_streaming():
            raise BrainAccessException("Cannot change channel state while streaming")
        _dll.ba_eeg_manager_set_channel_enabled(
            self._manager, ctypes.c_uint16(channel), ctypes.c_bool(state)
        )

    def set_channel_gain(self, channel: int, gain: GainMode) -> None:
        """Changes gain mode for a channel on the device.
        Setting gain values to lower will increase the measured voltage range,
        but would decrease the amplitude resolution, 12 is the optimum in most cases.

        Warning
        ------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.
        This only affects channels that support it. For example, it affects the
        electrode measurement channels but not sample number or digital input.

        Parameters
        -----------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) whose gain to modify.
        gain: GainMode
            Gain mode. Default X12

        Raises
        -------
        BrainAccessException if device is streaming or if the channel number is invalid

        """
        if channel < 0 or channel > 33:
            raise BrainAccessException("Invalid channel number")
        if self.is_streaming():
            raise BrainAccessException("Cannot change channel gain while streaming")
        _dll.ba_eeg_manager_set_channel_gain(
            self._manager, ctypes.c_uint16(channel), ctypes.c_uint8(gain.value)
        )

    @multimethod
    def set_channel_bias(self, channel: int, bias: bool) -> None:
        """
        DEPRECATED: use the version with Polarity instead.

        Set an electrode channel as a bias electrode
        Essentially the signals of these channels are inverted and injected
        into the bias channel/electrode. This helps in reducing common mode
        noise such as noise coming from the mains.
        Only select channels for bias feedback that have good contact with a skin.
        Typically one channel is sufficient for bias feedback to work effectively.

        Warning
        --------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        ------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to set/unset as bias channel
        bias: bool
            True to enable channel, False to disable.

        Raises
        -------

        BrainAccessException if device is streaming

        """
        warnings.warn(
            "This function is deprecated, use the version with Polarity instead.",
            DeprecationWarning,
        )
        if self.is_streaming():
            raise BrainAccessException("Cannot change channel bias while streaming")
        self.set_channel_bias(channel, Polarity.BOTH if bias else Polarity.NONE)

    @multimethod
    def set_channel_bias(self, channel: int, p: Polarity) -> None:
        """Set an electrode channel as a bias electrode
        Essentially the signals of these channels are inverted and injected
        into the bias channel/electrode. This helps in reducing common mode
        noise such as noise coming from the mains.
        Only select channels for bias feedback that have good contact with a skin.
        Typically one channel is sufficient for bias feedback to work effectively.

        Warning
        --------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        ------------
        channel: int
            Channel ID (brainaccess.core.eeg_channel) to set/unset as bias channel
        p: Polarity
            Which side of the electrode to use (if device is not bipolar, use
            BOTH)

        Raises
        -------
        BrainAccessException if device is streaming

        """
        if self.is_streaming():
            raise BrainAccessException("Cannot change channel bias while streaming")
        _dll.ba_eeg_manager_set_channel_bias(
            self._manager, ctypes.c_uint16(channel), ctypes.c_uint8(p.value)
        )

    def set_impedance_mode(self, mode: ImpedanceMeasurementMode):
        """Sets impedance measurement mode
        This function setups device for electrode impedance measurement.
        It injects a 7nA certain frequency current through the bias electrodes
        to measurement electrodes. Voltage recordings from each channel can
        then be used to calculate the impedance for each electrode:
        Impedance = Vpp/7nA

        Warning
        ---------
        This function takes effect on stream start, and its effects are
        reset by stream stop. Therefore, it must be called with the appropriate
        arguments before every stream start.

        Parameters
        -----------
        mode: ImpedanceMeasurementMode
            Impedance mode to set

        Raises
        -------
        BrainAccessException if device is streaming

        """
        if self.is_streaming():
            raise BrainAccessException("Cannot change impedance mode while streaming")
        _dll.ba_eeg_manager_set_impedance_mode(
            self._manager, ctypes.c_uint8(mode.value)
        )

    def get_device_info(self) -> DeviceInfo:
        """Get device information

        Warning
        ----------
        Must not be called unless device connection is successful

        Returns
        -------
        DeviceInfo
            device model, version, firmware version and buffer size
        """
        return _dll.ba_eeg_manager_get_device_info(self._manager).contents

    def get_channel_index(self, channel: int) -> int:
        """Gets the index of a channel's data into the chunk

        Get the index into the array provided by the chunk callback that contains
        the data of the channel number specified

        Parameters
        ------------
        channel: int
            The number of the channel whose index to get

        Returns
        ---------
        int
            Index into chunk representing a channel
        """
        val = _dll.ba_eeg_manager_get_channel_index(
            self._manager, ctypes.c_uint16(channel)
        )
        if val == ctypes.c_size_t(-1).value:
            raise BrainAccessException(
                "Channel does not exist or is not currently streaming"
            )
        return val

    def get_sample_frequency(self) -> int:
        """Get device sampling frequency

        Returns
        -------
        int
            Sample frequency (Hz)

        """
        return _dll.ba_eeg_manager_get_sample_frequency(self._manager)

    def set_callback_chunk(self, f: Callable) -> None:
        """Sets a callback to be called every time a chunk is available

        Warning
        -------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.

        Parameters
        ------------
        f
            callback Function to be called every time a chunk is available
            Set to null to disable.
        """
        with self._callback_chunk_mtx:
            self._callback_chunk = f
            _dll.ba_eeg_manager_set_callback_chunk(
                self._manager, _callback_chunk if f is not None else None, self._manager
            )

    def set_callback_battery(self, callback: Union[Callable, None] = None) -> None:
        """Sets a callback to be called every time the battery status is updated

        Warning
        ---------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.

        Parameters
        ----------
        callback: Union[Callable, None]
            pass callback Function to be called every time a battery update is available
            Set to null to disable.

        Raises
        -------
        BrainAccessException if callback is None

        """
        if callback is not None:
            with self._callback_battery_mtx:
                self._callback_battery = callback
        else:
            raise BrainAccessException("Callback cannot be null")
        _dll.ba_eeg_manager_set_callback_battery(
            self._manager,
            _callback_battery,
            self._manager,
        )

    def set_callback_disconnect(self, callback: Optional[Callable] = None) -> None:
        """Sets a callback to be called every time the device disconnects

        Warning
        ---------
        The callback may or may not run in the reader thread, and as such,
        synchronization must be used to avoid race conditions, and the callback
        itself must be as short as possible to avoid blocking communication
        with the device.


        Parameters
        ----------
        callback: Union[Callable, None]
            callback Function to be called every time the device disconnects. Set to null to disable.

        """
        if callback is None:
            with self._callback_disconnect_mtx:
                self._callback_disconnect = lambda: None
        else:
            with self._callback_disconnect_mtx:
                self._callback_disconnect = callback
        _dll.ba_eeg_manager_set_callback_disconnect(
            self._manager, _callback_disconnect, self._manager
        )

    def annotate(self, annotation: str) -> None:
        """Adds an annotation at the current time

        Warning
        ---------
        Annotations are cleared on disconnect

        Parameters
        ----------
        annotation: str
            annotation text

        Raises
        -------
        BrainAccessException if annotation is None or empty

        """
        if annotation is None:
            raise BrainAccessException("Annotation cannot be None")
        if len(annotation) == 0:
            raise BrainAccessException("Annotation cannot be empty")
        _handle_error(
            _dll.ba_eeg_manager_annotate(
                self._manager, ctypes.c_char_p(annotation.encode("ascii"))
            )
        )

    def get_device_features(self) -> DeviceFeatures:
        """Get device features and capabilities

        Returns
        -------
        DeviceFeatures
            object with methods to check the status of gyro, accelerometer, bipolarity, electrode count
        """
        info = self.get_device_info()
        return DeviceFeatures(info)

    def get_annotations(self) -> dict:
        """Retrieve all the accumulated annotations

        Warning
        ---------
        Annotations are cleared on disconnect

        Returns
        -------
        dict
            annotations: List[str]
            timestamps: List[float]
        """
        ae = ctypes.POINTER(Annotation)()
        size = ctypes.c_size_t()
        _dll.ba_eeg_manager_get_annotations(
            self._manager, ctypes.pointer(ae), ctypes.pointer(size)
        )
        annotations = [ae[i] for i in range(size.value)]
        timestamps = [x.timestamp for x in annotations]
        annotations = [x.annotation for x in annotations]
        return {"annotations": annotations, "timestamps": timestamps}

    def clear_annotations(self) -> None:
        """Clears annotations"""
        _dll.ba_eeg_manager_clear_annotations(self._manager)

    def start_update(self, callback: Union[Callable, None] = None) -> None:
        """Starts a firmware update

        Parameters
        ----------
        callback: Union[Callable, None]
            callback to be called every time the update progress changes

        Raises
        -------
        BrainAccessException if unable to start update

        """
        if callback is not None:
            with self._callback_ota_update_mtx:
                self._callback_ota_update = callback
        else:
            with self._callback_ota_update_mtx:
                self._callback_ota_update = lambda x, y: None

        _handle_error(
            _dll.ba_eeg_manager_start_update(
                self._manager, _callback_ota_update, self._manager
            )
        )
