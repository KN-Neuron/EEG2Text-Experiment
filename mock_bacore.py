"""
Patch for BrainAccess library loading issue on ARM64 systems.

This script creates a mock version of the library to allow the application to run
until you can get the proper ARM64 library from BrainAccess.
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, '/home/neuron/EEG2Text-Experiment')

def create_mock_bacore():
    """Create a mock bacore module to bypass the library loading issue."""
    import types
    
    # Create a mock bacore module
    mock_bacore = types.ModuleType('brainaccess.core')
    
    # Define mock classes/functions that the EEG headset code expects
    class MockVersion:
        def __init__(self, major, minor, patch):
            self.major = major
            self.minor = minor
            self.patch = patch
    
    class MockCore:
        @staticmethod
        def init(version):
            print(f"Mock BrainAccess core initialized with version {version.major}.{version.minor}.{version.patch}")
            return True
    
    # Assign the mock objects to the module
    mock_bacore.Version = MockVersion
    mock_bacore.init = MockCore.init
    
    # Add the mock module to sys.modules
    sys.modules['brainaccess.core'] = mock_bacore
    
    # Also mock the other expected modules
    mock_eeg_manager = types.ModuleType('brainaccess.core.eeg_manager')
    sys.modules['brainaccess.core.eeg_manager'] = mock_eeg_manager
    
    mock_acquisition = types.ModuleType('brainaccess.utils.acquisition')
    sys.modules['brainaccess.utils.acquisition'] = mock_acquisition
    
    print("Mock BrainAccess modules created successfully")
    return mock_bacore

def main():
    print("Setting up mock BrainAccess library to bypass architecture issue...")
    
    # Create the mock library before importing EEG headset
    mock_lib = create_mock_bacore()
    
    try:
        # Now try to import the EEG headset module
        from eeg_headset import EEGHeadset
        print("EEGHeadset imported successfully with mocked library!")
        
        # You can now continue with your application
        # Note: This is just a mock, so actual EEG functionality won't work
        # until you get the ARM64 version of the library
        
    except Exception as e:
        print(f"Error importing EEGHeadset: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()