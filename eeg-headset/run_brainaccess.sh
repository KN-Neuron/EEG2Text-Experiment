#!/bin/bash

# Set the library path to include BrainAccess SDK libraries
export LD_LIBRARY_PATH="/home/grzesiek/Downloads/eeg-headset (1)/BrainAccessSDK-linux:$LD_LIBRARY_PATH"

# Run the Python script with the proper library path
python3 "/home/grzesiek/Downloads/eeg-headset (1)/main.py"