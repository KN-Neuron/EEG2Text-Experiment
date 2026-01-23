# BrainAccess EEG Application

This project contains code to interface with BrainAccess EEG devices.

## Prerequisites

1. **BrainAccess SDK**: The required SDK libraries are included in the `BrainAccessSDK-linux` directory.

2. **EEG Device**: You need a BrainAccess EEG device (such as BA MAXI 012) that is properly paired with your computer via Bluetooth.

## Setup

1. Make sure you're in the project directory:
   ```bash
   cd "/home/grzesiek/Downloads/eeg-headset (1)"
   ```

2. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Running the Application

To run the application, use the provided shell script which properly sets the library path:

```bash
./run_brainaccess.sh
```

Alternatively, you can run:

```bash
export LD_LIBRARY_PATH="/home/grzesiek/Downloads/eeg-headset (1)/BrainAccessSDK-linux:$LD_LIBRARY_PATH" && python3 main.py
```

## Troubleshooting

1. **"No devices found"**: This means the EEG device is not found. Make sure:
   - The EEG device is turned on
   - The device is properly paired with your computer via Bluetooth
   - The device name in the code matches your actual device name
   - You have proper Bluetooth permissions

2. **"Could not load libbacore.so"**: This means the library path is not set correctly. Always use the shell script or manually set the `LD_LIBRARY_PATH` as shown above.

3. **Permission issues**: You may need to ensure your user has access to Bluetooth, which might require adding your user to the `bluetooth` group:
   ```bash
   sudo usermod -a -G bluetooth $USER
   ```
   Then log out and log back in.

## Device Pairing

If your device is not detected:

1. Make sure the EEG device is in pairing mode
2. Use the Bluetooth manager to pair the device:
   ```bash
   bluetoothctl
   ```
3. Once paired, check the device name with `systemctl list-units --type=service | grep bluetooth` if needed

## Notes

- The device name in the code (`BA MAXI 012`) may need to be changed to match your actual device name
- The application will try to connect to the EEG device and acquire data for 5 seconds
- Acquired data will be saved to `eeg_data.raw.fif` when the acquisition is complete