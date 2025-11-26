#!/bin/bash

# One-Command EEG2Text Experiment Runner
# This script handles setup and execution in one go

set -e

echo "====================================="
echo "EEG2Text Experiment - One Command Setup & Run"
echo "====================================="

PROJECT_DIR="/home/grzesiek/EEG2Text-Experiment/experiment"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory not found at $PROJECT_DIR"
    echo "Please make sure the project is properly located."
    exit 1
fi

cd "$PROJECT_DIR"

echo "Step 1: Checking system requirements..."
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed"
    exit 1
fi

if ! command -v pip &> /dev/null; then
    echo "Error: pip is not installed"
    exit 1
fi

echo "Step 2: Setting up the environment..."
bash setup.sh

echo ""
echo "Step 3: Running the experiment..."
echo "====================================="
echo "Choose an option:"
echo "1) Run with real EEG headset"
echo "2) Run with mock EEG (for testing)"
echo "====================================="

read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo "Running with real EEG headset..."
    echo "Make sure your EEG headset is:"
    echo "  - Turned on and charged"
    echo "  - Paired and connected via Bluetooth"
    echo "  - Accessible as /dev/rfcomm0"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    bash run_experiment.sh
elif [ "$choice" = "2" ]; then
    echo "Running with mock EEG headset..."
    bash run_experiment.sh --mock-eeg
else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "====================================="
echo "Experiment completed!"
echo "Data saved in the 'data/' directory"
echo "Logs saved in the 'logs/' directory"
echo "====================================="