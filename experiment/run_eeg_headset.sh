#!/bin/bash

# Set the library path to include BrainAccess SDK libraries for the current project
export LD_LIBRARY_PATH="/home/grzesiek/EEG2Text-Experiment/experiment/BrainAccessSDK-linux:$LD_LIBRARY_PATH"

# Run the Python script with the proper library path
python3 "/home/grzesiek/EEG2Text-Experiment/experiment/test_eeg_connection.py"