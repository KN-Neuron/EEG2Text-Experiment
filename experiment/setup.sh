#!/bin/bash

# EEG2Text Experiment Setup Script
# This script sets up and runs the EEG2Text experiment with all necessary dependencies

set -e  # Exit on any error

echo "========================================="
echo "EEG2Text Experiment Setup and Runner"
echo "========================================="

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This script is designed for Linux. Some features may not work on other OS."
    read -p "Do you want to continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for required tools
echo "Checking for required tools..."

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed. Please install pip."
    exit 1
fi

# Install poetry if not present
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

# Add poetry to PATH for this session if needed
if ! command -v poetry &> /dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing project dependencies..."
cd /home/grzesiek/EEG2Text-Experiment/experiment
poetry install

echo "Setting executable permissions..."
chmod +x /home/grzesiek/EEG2Text-Experiment/experiment/run_experiment.sh

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run the experiment:"
echo "  - With real EEG headset: bash run_experiment.sh"
echo "  - With mock EEG headset: bash run_experiment.sh --mock-eeg"
echo ""
echo "Important notes:"
echo "- If using real EEG headset, make sure the device is:"
echo "  * Turned on and charged"
echo "  * Paired via Bluetooth"
echo "  * Accessible as /dev/rfcomm0 (or update eeg_config.py)"
echo "- For first-time Bluetooth setup, you may need to run:"
echo "  sudo usermod -a -G bluetooth $USER"
echo "  (then log out and log back in)"
echo ""
echo "The BrainAccess EEG SDK is now properly configured!"