# -*- coding: utf-8 -*-
""" 4 target ssvep bci with constant prediction

4 target SSVEP classification

Concentrate on one of the four rectangles. Live prediction is updated every 4 seconds

Press q to quit.

Usage
------
To print help:
    python bci_ssvep_4_target.py --help

Standard run if device name is BA MINI 001
    python bci_ssvep_4_target.py --name BA MINI 001 --prediction_interval 4 --full_screen True

"""

import threading
import time
from copy import copy
import click
import logging

from brainaccess.connect.SSVEP import SSVEP
from brainaccess.core.eeg_manager import EEGManager
import ssvep
import feedback_psychopy as feedback
from brainaccess.utils import acquisition


class Predict:
    """Prediction logic of SSVEP"""

    def __init__(
        self,
        main_app,
        eeg,
        prediction_time: float = 4,
    ) -> None:
        self.mutex = threading.Lock()
        self.eeg = eeg
        self.main_app = main_app
        self.guess: int = 9
        self.passed: bool = False
        self.sample_rate: int = 250
        self.prediction_time: float = prediction_time
        self.threshold = 1.5
        self.clf = SSVEP()
        self.frequencies = [10, 11, 12, 13]

    def prep_data(self, annot: bool = True):
        data = self.eeg.get_mne(
            tim=self.prediction_time, annotations=annot
        ).pick_channels(["O1", "O2"], ordered=True)
        data = data.filter(1, 90, method="fir", verbose=False)
        return data.get_data()

    def get_guess(self):
        guess = None
        pass_guess = False
        try:
            with self.mutex:
                guess = copy(self.guess)
                pass_guess = copy(self.passed)
        except Exception:
            logging.error("failed get guess")
        return guess, pass_guess

    def _pred(self):
        while self.thread_flag:
            time.sleep(1)
            data = self.prep_data(annot=False)
            try:
                guess, score = self.clf.predict(data, frequencies=self.frequencies, sample_rate=self.sample_rate)
                with self.mutex:
                    self.guess = guess
                    self.score = score
                self.passed = self.score > self.threshold
            except Exception:
                self.guess = 9
                self.passed = False
            self.main_app.get_keys()
            if "q" in self.main_app.keys:
                self.thread_flag = False
                logging.info("user quit by pressing q")
                break

    def start(self):
        self.thread_flag = True
        self.feed_thread = threading.Thread(target=self._pred)
        self.feed_thread.start()

    def stop(self):
        self.thread_flag = False
        self.feed_thread.join()


@click.command()
@click.option(
    "--full_screen", type=bool, help="Display stimulation full screen?", default=True
)
@click.option(
    "--prediction_interval",
    type=float,
    help="Prediction interval (sec)",
    default=4,
)
@click.option(
    "--name", type=str, help="Device name", default="BA MINI 001"
)
def main(
    full_screen: bool = False,
    prediction_interval: float = 4,
    name: str = "BA MINI 001",
):
    """4 target SSVEP BCI"""
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        # filename=f'{time.strftime("%Y%m%d_%H%M")}.log',
        # filemode="w",
        level=logging.INFO,
        format=log_fmt,
    )
    logging.info("Start live 4 targets session")

    main_app = feedback.Feedback()
    main_app.window(fullscr=full_screen, screen=1, win_type="pyglet")
    main_app.draw_text("Initializing...\n During the demo press q to exit")

    cap: dict = {
      0: "Fp1",
      1: "Fp2",
      2: "O1",
      3: "O2",
    }

    eeg = acquisition.EEG(mode='roll')

    with EEGManager() as mgr:
        eeg.setup(mgr, device_name=name, zeros_at_start=int(250*20), bias=[0], cap=cap)
        prediction_class = Predict(main_app, eeg, prediction_interval)
        eeg.start_acquisition()
        ssvep.stimulation(
            main_app,
            predict=prediction_class,
        )
        eeg.stop_acquisition()
        mgr.disconnect()

    eeg.close()

    main_app.draw_text("Thank you")
    main_app.wait_untill_press(button=['space', 'q'])
    main_app.close()


if __name__ == "__main__":
    main()
