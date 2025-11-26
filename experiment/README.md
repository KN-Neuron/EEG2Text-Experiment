# EEG2Text Experiment

This project enables EEG data collection during text reading experiments using BrainAccess EEG headsets.

## Quick Start - One Command

### Option 1: Direct execution (Linux only)

```bash
cd /home/grzesiek/EEG2Text-Experiment/experiment
bash run.sh
```

### Option 2: Docker container (any OS with Docker)

```bash
# Build and run the container
cd /home/grzesiek/EEG2Text-Experiment/experiment
docker-compose up --build
```

## Prerequisites

### For Direct Execution (Recommended for Linux):

- Linux operating system (Ubuntu/Debian recommended)
- Python 3.8 or higher
- Git
- Bluetooth adapter
- BrainAccess EEG headset (e.g., BA MAXI 012 or BA Halo)

### For Docker Execution (Cross-platform):

- Docker
- Docker Compose
- Bluetooth adapter (with Docker access)
- BrainAccess EEG headset

## Detailed Setup Instructions

### 1. System Dependencies

Make sure you have the required system packages installed:

```bash
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv git curl
```

### 2. Bluetooth Setup

For the EEG headset to work via Bluetooth:

```bash
# Add current user to bluetooth group (required for EEG access)
sudo usermod -a -G bluetooth $USER

# Then log out and log back in, or run:
newgrp bluetooth
```

### 3. Pair Your EEG Headset

The first time, you'll need to pair your EEG headset:

```bash
# Start bluetoothctl
bluetoothctl

# In bluetoothctl:
[bluetooth]# scan on
# Find your device (e.g., "BA MAXI 012" or "BA Halo")
[bluetooth]# pair [DEVICE_MAC_ADDRESS]
[bluetooth]# connect [DEVICE_MAC_ADDRESS]
[bluetooth]# trust [DEVICE_MAC_ADDRESS]
[bluetooth]# quit
```

## Configuration

The EEG headset configuration is in `eeg_config.py`:

- `DEVICE_NAME`: Name of your EEG device (e.g., "BA MAXI 012", "BA Halo")
- `USED_DEVICE`: Channel mapping for your headset model
- `PORT`: Bluetooth serial port (usually "/dev/rfcomm0")

Update these values if your device name or configuration differs.

## Usage

### Command Line Options:

```bash
bash run_experiment.sh [options]

Options:
  --mock-eeg    Use mock EEG instead of real headset (for testing)
  --debug       Enable debug mode with more verbose logging
  -d            Same as --debug
```

### During the Experiment:

1. Enter a participant ID when prompted
2. Follow the on-screen instructions
3. The EEG will record during the experiment
4. Data will be saved to the `data/` folder
5. Check the `logs/` folder for experiment logs

## Troubleshooting

### Common Issues:

**"Could not load libbacore.so"**: This indicates the LD_LIBRARY_PATH wasn't set properly. Make sure to use `run_experiment.sh` instead of calling `python main.py` directly.

**"No such file or directory: /dev/rfcomm0"**: The Bluetooth serial port isn't established. You may need to create the rfcomm connection:

```bash
sudo rfcomm bind 0 [YOUR_HEADSET_MAC_ADDRESS]
```

**"Device setup failed"**: Ensure the headset is:

- Powered on and charged
- Properly paired and connected via Bluetooth
- The device name in `eeg_config.py` matches your actual device name

**"Permission denied"**: Make sure your user is in the bluetooth group:

```bash
groups $USER
# Should include "bluetooth"
```

## Project Structure

- `main.py`: Entry point for the experiment
- `eeg_headset.py`: EEG headset interface with BrainAccess SDK
- `eeg_config.py`: EEG device configuration
- `experiment.py`: Main experiment logic
- `gui.py`: Graphical user interface
- `run_experiment.sh`: Wrapper script with proper library paths
- `setup.sh`: One-command setup script
- `data/`: Storage for collected EEG data
- `logs/`: Storage for experiment logs

## Data Output

- EEG data: Saved in FIF format in `data/[participant_id]/`
- Experiment logs: Text files in `logs/`
- Summary data: JSON files with timing information

## Bluetooth Troubleshooting

If you're having trouble connecting to the EEG headset:

1. Check if it's visible:

   ```bash
   bluetoothctl
   [bluetooth]# scan on
   ```

2. Check if rfcomm0 exists:

   ```bash
   ls -la /dev/rfcomm*
   ```

3. If not connected, you can try manually establishing the connection:

   ```bash
   # Find your device MAC address
   hcitool scan

   # Bind to the device
   sudo rfcomm bind 0 [MAC_ADDRESS_HERE]

   # Verify connection
   ls -la /dev/rfcomm0
   ```

## Docker Setup (Alternative Method)

For systems that support Docker, you can use the containerized version:

### Prerequisites:

- Docker
- Docker Compose
- Bluetooth adapter

### To run with Docker:

```bash
cd /home/grzesiek/EEG2Text-Experiment/experiment
docker-compose up --build
```

### To run with Docker (detached mode):

```bash
docker-compose up --build -d
```

### To run with Docker interactively:

```bash
# Build the container
docker build -t eeg-experiment .

# Run interactively
docker run -it --privileged --net=host \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $(pwd)/data:/home/researcher/EEG2Text-Experiment/experiment/data \
  -v $(pwd)/logs:/home/researcher/EEG2Text-Experiment/experiment/logs \
  -v $(pwd):/home/researcher/EEG2Text-Experiment/experiment \
  -e DISPLAY=$DISPLAY \
  eeg-experiment
```

Note: The Docker approach may have limitations with Bluetooth device access on some systems. The direct execution method is recommended for production use.

## Notes

- The experiment uses a BrainAccess SDK with precompiled binaries
- EEG data is recorded at 250 Hz sampling rate
- All EEG annotations are saved with millisecond precision
- The GUI requires a display (doesn't work in headless mode)
