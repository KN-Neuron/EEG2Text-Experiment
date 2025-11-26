"""Starting addresses of channels in the chunk

Attributes
-----------
SAMPLE_NUMBER
    The number of the sample starting from 0 at stream start
ELECTRODE_MEASUREMENT
    EEG electrode measurement value (uV)
ELECTRODE_CONTACT
    Whether or not the electrode is making contact with the skin
DIGITAL_INPUT
    Digital IO pin
ACCELEROMETER
    Accelerometer values
GYROSCOPE
    Gyroscope values
STREAMING
    Whether or not the device is streaming
ELECTRODE_CONTACT_P
    Whether or not the positive (P) electrode is making contact with the skin
ELECTRODE_CONTACT_N
    Whether or not the negative (N) electrode is making contact with the skin


Examples
---------
To get ACCELEROMETER x y and z index in the chunk

- x: get_channel_index(ACCELEROMETER + 0)
- y: get_channel_index(ACCELEROMETER + 1)
- z: get_channel_index(ACCELEROMETER + 2)

"""
SAMPLE_NUMBER = 0
ELECTRODE_MEASUREMENT = 1
ELECTRODE_CONTACT_P = 513
ELECTRODE_CONTACT = 1025
ELECTRODE_CONTACT_N = 1537
DIGITAL_INPUT = 2049
GYROSCOPE = 2497
ACCELEROMETER = 2561
STREAMING = 2625
