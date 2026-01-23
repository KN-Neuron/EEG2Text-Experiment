""" Impedance measurement example
Example how to get impedance measurements
using acquisition class from brainaccess.utils

Change Bluetooth device name to your device name (line 18)
"""

import time

from brainaccess.utils import acquisition
from brainaccess.core.eeg_manager import EEGManager

eeg = acquisition.EEG()

cap: dict = {
  0: "Fp1",
  1: "Fp2",
  2: "O1",
  3: "O2",
}

# define device name
device_name = "BA HALO 001"

with EEGManager() as mgr:

    eeg.setup(mgr, device_name=device_name, cap=cap)
    # Start measuring impedance
    eeg.start_impedance_measurement()
    # Print impedances
    start_time = time.time()
    while time.time()-start_time < 20:
        time.sleep(1)
        imp = eeg.calc_impedances()
        print(imp)

    # Stop measuring impedance
    eeg.stop_impedance_measurement()
    mgr.disconnect()

eeg.close()
