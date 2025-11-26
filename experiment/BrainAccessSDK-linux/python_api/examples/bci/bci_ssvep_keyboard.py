# -*- coding: utf-8 -*-
"""SSVEP keyboard bci

40 target SSVEP classification
Concentrate on the letter during stimulation. After `prediction_interval` seconds prediction will be displayed at the top of the screen.

Press q to quit.

After the experiment acquired raw eeg data with annotations is saved to the root directory.

Usage
------
To print help:
    python bci_ssvep_keyboard.py --help

Standard run if device name is BA MINI 001
    python bci_ssvep_keyboard.py --name BA MINI 001 --prediction_interval 10 --full_screen True

"""

import time
import click
import logging
import numpy as np
import mne

from brainaccess.core.eeg_manager import EEGManager
from brainaccess.utils import acquisition
from brainaccess.connect.SSVEP import SSVEP
import feedback_psychopy as feedback
import keyboard_ssvep as ssvep


class Predict:
    """Prediction logic of SSVEP"""

    def __init__(
        self,
        main_app,
        eeg,
        prediction_time: float = 10,
    ) -> None:
        self.eeg = eeg
        self.main_app = main_app
        self.guess: int = 9
        self.passed: bool = False
        self.sample_rate: int = 250
        self.prediction_time: float = prediction_time
        self.duration: int = int(self.sample_rate * self.prediction_time)+1
        self.clf = SSVEP()
        self.threshold = 0

    def get_last_event(self, data):
        reg = ".*[^f]$"
        events, _ = mne.events_from_annotations(data, regexp=reg)
        data = data.filter(1, 90, method="fir", verbose=False)
        epochs = mne.Epochs(
            data,
            events=np.array([events[-1, :]]),
            tmin=0,
            tmax=self.prediction_time,
            baseline=None,
            preload=True,
            verbose=False,
        )
        return epochs.get_data()

    def predict(self, frequencies):
        data = self.eeg.get_mne().pick(["O1", "O2"])
        sample_rate = data.info['sfreq']
        data = self.get_last_event(data)
        predicted_class, predicted_score = self.clf.predict(data[0, :, :], frequencies, sample_rate)
        self.guess = predicted_class
        self.passed = predicted_score > self.threshold
        return self.guess, self.passed


@click.command()
@click.option(
    "--full_screen", type=bool, help="Display stimulation full screen?", default=True
)
@click.option(
    "--prediction_interval",
    type=float,
    help="Prediction interval (sec)",
    default=10,
)
@click.option(
    "--name", type=str, help="Device name", default="BA MINI 001"
)
def main(
    full_screen: bool = False,
    name: str = "BA MINI 001",
    prediction_interval: float = 10,
):
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        filename=f'{time.strftime("%Y%m%d_%H%M")}.log',
        filemode="w",
        level=logging.DEBUG,
        format=log_fmt,
    )
    """Live SSVEP keyboard BCI"""
    logging.info("Vectorized keyboard start")
    eeg = acquisition.EEG()
    main_app = feedback.Feedback()
    main_app.window(
        size=[800, 800],
        fullscr=full_screen,
        screen=0,
        win_type="pyglet",
        units="pix",
        color=[-0.9, -0.9, -0.9],
    )
    cap: dict = {
      0: "Fp1",
      1: "Fp2",
      2: "O1",
      3: "O2",
    }
    with EEGManager() as mgr:
        eeg.setup(mgr, device_name=name, bias=[0], cap=cap)
        eeg.start_acquisition()
        feed = Predict(main_app=main_app, eeg=eeg, prediction_time=prediction_interval)
        text = "Press space key to start\n During the demo press q to exit"
        main_app.wait_for_press(text, height=50)
        main_app.cross(height=100)
        time.sleep(1)
        ssvep.keyboard_live(
            main_app,
            eeg=eeg,
            predict=feed,
            stim_duration=prediction_interval
        )
        eeg.stop_acquisition()
        eeg.get_mne()
        mgr.disconnect()
        eeg.data.save("example_ssvep_keyboard-raw.fif")
        eeg.close()


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    main()
