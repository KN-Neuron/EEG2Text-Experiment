import time
import string
import pathlib
from os import environ
from collections import defaultdict

import click
import mne
import numpy as np

from brainaccess.connect.P300 import P300
from brainaccess.utils import acquisition
from brainaccess.connect import processor
from brainaccess.core.eeg_manager import EEGManager

from sys import platform
import ctypes
if platform == "linux" or platform == "linux2":
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import feedback_psychopy as feedback


class Predict:
    def __init__(self, main_app, eeg) -> None:
        self.eeg = eeg
        self.main_app = main_app
        self.proc = processor
        self.p300 = P300(model_number=0)

        self.row_labels = ["ABCDEF", "GHIJKL", "MNOPQR", "STUVWX", "YZ0123", "456789"]
        self.col_labels = ["AGMSY4", "BHNTZ5", "CIOU06", "DJPV17", "EKQW28", "FLRX39"]
        self.char_count = 0

    def get_processed_data(self, data):
        events, event_ids = mne.events_from_annotations(data, verbose=False)
        data.filter(1, 40, verbose=False).apply_function(
            self.proc.ewma_standardize, channel_wise=False
        )

        row_epochs, col_epochs = [], []
        for row_label in self.row_labels:
            row_events = np.where(events[:, 2] == event_ids[row_label])[0][
                self.char_count * 1 : (self.char_count + 1) * 1
            ]
            epochs = mne.Epochs(
                data,
                events=events[row_events],
                event_id={row_label: event_ids[row_label]},
                tmin=-0.2,
                tmax=0.5,
                baseline=None,
                preload=True,
                verbose=False,
            )
            row_epochs.append(epochs.pick_types(eeg=True).get_data())

        for col_label in self.col_labels:
            col_events = np.where(events[:, 2] == event_ids[col_label])[0][
                self.char_count * 1 : (self.char_count + 1) * 1
            ]
            epochs = mne.Epochs(
                data,
                events=events[col_events],
                event_id={col_label: event_ids[col_label]},
                tmin=-0.2,
                tmax=0.5,
                baseline=None,
                preload=True,
                verbose=False,
            )
            col_epochs.append(epochs.pick_types(eeg=True).get_data())

        row_epochs, col_epochs = np.array(row_epochs), np.array(col_epochs)
        return row_epochs, col_epochs

    def pred_NN(self):
        data = self.eeg.get_mne().pick_channels(
            ["F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2"], ordered=True
        )
        row_data, col_data = self.get_processed_data(data)

        row_preds = [self.p300.predict(i[0]) for i in row_data]
        col_preds = [self.p300.predict(i[0]) for i in col_data]

        self.char_count += 1

        row_num, col_num = np.argmax(row_preds), np.argmax(col_preds)

        row_string, col_string = self.row_labels[row_num], self.col_labels[col_num]
        pred_char = list(set(row_string).intersection(col_string))[0]
        return pred_char


def get_keyboard(main_app):
    letters = string.ascii_uppercase + string.digits
    shape_x, shape_y = 6, 6

    x_axis = np.linspace(-350, 350, shape_y)
    y_axis = np.linspace(-350, 350, shape_x).T
    xv, yv = np.meshgrid(x_axis, y_axis)
    xys = np.array((xv.ravel(), yv.ravel())).T

    stimuli = defaultdict()
    stim_height = 65
    for id_letter, letter in enumerate(letters):
        stimuli[letter] = feedback.visual.TextStim(
            win=main_app.win, height=stim_height, font="Arial", depth=-6
        )
        stimuli[letter].text = letter
        stimuli[letter].pos = xys[id_letter]

    for id in range(6):
        stimuli[f"face{id}"] = feedback.visual.ImageStim(
            win=main_app.win,
            image = pathlib.Path(__file__).parent.joinpath('assets/gan_face1.png'),
            size=stim_height,
        )
    return stimuli


def get_face_combinations(multiplier: int = 1):
    for _ in range(multiplier):
        values = np.arange(36).reshape(6, 6)
        values = np.concatenate((values, values.T))
        random_index = np.arange(len(values))
        np.random.shuffle(random_index)
        values = values[random_index]
        for col in values:
            yield col


def P3_Live(
    main_app,
    stim_duration: float = 0.8,
    iti: float = 4.5,
    eeg=None,
    isi: float = 0.35,
    save_name: str = "test",
    predict=None,
):

    stimuli = get_keyboard(main_app)
    letters = np.array(list(stimuli.keys()))

    answer_text = ""
    answer_text_stim = feedback.visual.TextStim(
        win=main_app.win, height=65, font="Arial", depth=-6
    )
    answer_text_stim.text = "_"
    answer_text_stim.pos = np.array([0, 475])

    main_app.clear_text()

    while True:
        main_app.clear_text()

        for stim in stimuli:
            if "face" not in stim:
                stimuli[stim].draw()
        answer_text_stim.draw()
        main_app.flip()
        time.sleep(iti)

        face_combination_list = list(get_face_combinations())

        for col in face_combination_list:
            annot = ""
            for nr, x in enumerate(list(col)):
                stimuli[f"face{nr}"].pos = stimuli[letters[x]].pos
                annot = "".join([annot, letters[x]])

            for stim in stimuli:
                stimuli[stim].draw()
            answer_text_stim.draw()
            main_app.flip()

            if eeg:
                eeg.annotate(annot)
            time.sleep(stim_duration)

            for stim in stimuli:
                if "face" not in stim:
                    stimuli[stim].draw()
            answer_text_stim.draw()
            main_app.flip()
            time.sleep(isi)

            main_app.get_keys(keyList=["space", "q", "p"])
            if "q" in main_app.keys:
                break

        if "q" in main_app.keys:
            break
        if predict:
            guess = predict.pred_NN()
            answer_text += guess
            answer_text_stim.text = answer_text
            answer_text_stim.draw()
            for stim in stimuli:
                if "face" not in stim:
                    stimuli[stim].draw()
            main_app.flip()
            time.sleep(1)


@click.command()
@click.option(
    "--name", type=str, help="Device name", default="BA MINI 001"
)
def main(name: str):
    main_app = feedback.Feedback()
    main_app.window(
        size=[800, 800],
        fullscr=True,
        screen=0,
        win_type="pyglet",
        units="pix",
        color=[0, 0, 0],
    )

    eeg = acquisition.EEG()
    cap: dict = {
        0: "F3",
        1: "F4",
        2: "C3",
        3: "C4",
        4: "P3",
        5: "P4",
        6: "O1",
        7: "O2",
    }
    with EEGManager() as mgr:
        eeg.setup(mgr, device_name=name, bias=[0], cap=cap)
        eeg.start_acquisition()

        text = "press space key to start"
        main_app.wait_for_press(text, height=100)
        main_app.cross(height=100)

        pred = Predict(main_app, eeg)

        time.sleep(1)
        P3_Live(main_app, stim_duration=0.5, iti=4.5, isi=0.35, eeg=eeg, predict=pred)
        text = "Press space key to exit"
        main_app.wait_for_press(text, height=100)

        eeg.stop_acquisition()
        eeg.get_mne()
        mgr.disconnect()
    eeg.close()


if __name__ == "__main__":
    main()
