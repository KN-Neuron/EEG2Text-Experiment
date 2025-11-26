#!/bin/bash

# Script to run the EEG experiment with proper library paths
# This ensures LD_LIBRARY_PATH is set before the Python process starts

export LD_LIBRARY_PATH="/home/grzesiek/EEG2Text-Experiment/experiment/BrainAccessSDK-linux:$LD_LIBRARY_PATH"

# Run the Python application with poetry
cd /home/grzesiek/EEG2Text-Experiment/experiment
poetry run python main.py "$@"