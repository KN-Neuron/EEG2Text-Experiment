"""EEG measurement example

Example how to get measurements using brainaccess library

Change Bluetooth device name to your device name (line 57)
"""

import numpy as np
import time
import threading
import matplotlib.pyplot as plt
from scipy.signal import butter, sosfiltfilt
from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
import brainaccess.core.eeg_channel as eeg_channel
from brainaccess.core.gain_mode import (
    GainMode,
)


def butter_bandpass(lowcut, highcut, fs, order=2):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = butter(order, [low, high], analog=False, btype="bandpass", output="sos")
    return sos


def butter_bandpass_filter(data, lowcut, highcut, fs, order=2):
    sos = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sosfiltfilt(sos, data)
    return y


def _acq_closure(ch_number: int = 1, buffer_length: int = 1000):
    data = np.zeros((ch_number, buffer_length))
    mutex = threading.Lock()

    def _acq_callback(chunk, chunk_size):
        nonlocal data
        nonlocal mutex
        with mutex:
            data = np.roll(data, -chunk_size)
            data[:, -chunk_size:] = chunk

    def get_data():
        nonlocal data
        with mutex:
            return data.copy()

    return _acq_callback, get_data


if __name__ == "__main__":
    # Change to your device name
    # Device name can be found on the back of the device
    device_name = "BA HALO 001"

    # init the core
    core.init()

    # scan for devices
    core.scan(0)  # adapter number (on windows always 0)
    count = core.get_device_count()
    port = 0
    # find the defined one
    print("Found devices:", count)
    for i in range(count):
        name = core.get_device_name(i)
        if device_name in name:
            port = i
            break
    else:
        raise Exception(f"Device {device_name} not found")

    # connect to the device
    with EEGManager() as mgr:
        print("Connecting to device:", core.get_device_name(port))
        _status = mgr.connect(port)
        if _status == 1:
            raise Exception("Connection failed")
        elif _status == 2:
            raise Exception("Stream is incompatible. Update the firmware.")

        # battery info
        print(f"battery level: {mgr.get_battery_info().level} %")

        # Get electrode count
        device_features = mgr.get_device_features()
        eeg_channels_number = device_features.electrode_count()
        print(f"Device has {eeg_channels_number} EEG channels")

        # set the channels
        ch_nr = 0
        # for i in range(eeg_channels_number):
        for i in range(eeg_channels_number):
            mgr.set_channel_enabled(eeg_channel.ELECTRODE_MEASUREMENT + i, True)
            ch_nr += 1
            mgr.set_channel_gain(eeg_channel.ELECTRODE_MEASUREMENT + i, GainMode.X8)
        mgr.set_channel_bias(eeg_channel.ELECTRODE_MEASUREMENT + i, True)

        # check if the device has accelerometer
        has_accel = device_features.has_accel()
        if has_accel:
            print("Setting the accelerometer")
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 1, True)
            ch_nr += 1
            mgr.set_channel_enabled(eeg_channel.ACCELEROMETER + 2, True)
            ch_nr += 1

        mgr.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
        ch_nr += 1

        # set the streaming channel, shows 0 if Bluetooth connection
        # was lost and 0 was added to the data
        mgr.set_channel_enabled(eeg_channel.STREAMING, True)
        ch_nr += 1

        # get the sample rate
        sr = mgr.get_sample_frequency()

        # define the callback for the acquisition
        duration = 10
        buffer_time = int(sr * duration)  # seconds
        _acq_callback, get_data = _acq_closure(
            ch_number=ch_nr, buffer_length=buffer_time
        )
        mgr.set_callback_chunk(_acq_callback)

        # load defined configuration
        mgr.load_config()

        # start the stream
        mgr.start_stream()
        print("Stream started")

        # collect data
        time.sleep(4)
        for i in range(duration):
            time.sleep(1)
            print(f"Collecting data {i + 1}/{duration}")

        # get the data
        dat = get_data()

        # stop the stream
        mgr.stop_stream()
        print("Stream stopped")
        time.sleep(1)

        # The EEGManager destructor calls mgr.disconnect()
        # so we don't need to call it here

    print("Disconnected from the device")
    time.sleep(1)

    # close the core
    core.close()
    print("Core closed")

    # plot the data
    print("Plotting the data")

    # Create channel labels
    ch = ["sample"]
    ch.extend([f"ch_{i}" for i in range(eeg_channels_number)])
    if has_accel:
        ch.extend(["accel_x", "accel_y", "accel_z"])
    ch.extend(["streaming"])

    # Apply bandpass filter to EEG data
    eeg_data = dat[1 : eeg_channels_number + 1, :]
    eeg_data = butter_bandpass_filter(eeg_data, 1, 40, sr)

    # Normalize EEG data
    eps = 1e-20  # To avoid division by zero in this example
    eeg_data = (eeg_data - np.mean(eeg_data, axis=0)) / (np.std(eeg_data, axis=0) + eps)
    # Add offsets for visualization
    breakpoint()
    eeg_data = eeg_data + np.arange(eeg_channels_number)[:, np.newaxis]

    # Create subplots
    fig, axs = plt.subplots(4, 1, figsize=(10, 10))

    # Plot the data
    axs[0].plot(eeg_data.T)
    axs[0].set_ylabel("EEG Channels")

    if has_accel:
        axs[1].plot(dat[len(ch) - 4 : -1, :].T)
        axs[1].set_ylabel("Accelerometer")
    else:
        axs[1].axis("off")  # Hide the unused subplot

    axs[2].plot(dat[0, :])
    axs[2].set_ylabel("Sample")

    axs[3].plot(dat[-1, :])
    axs[3].set_ylabel("Streaming")

    plt.show()
