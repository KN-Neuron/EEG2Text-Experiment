# -*- coding: utf-8 -*-
"""Helper SSVEP keybaord functions"""

from sys import platform
import ctypes

if platform == "linux" or platform == "linux2":
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
import numpy as np
import logging
import time
import feedback_psychopy as feedback
import string


def get_color_map(stimuli, duration: float, main_app, iti_color: float = 1):
    """Get sinusoid color change at monitor refresh rate"""
    frame_rate = int(np.round(main_app.win.getActualFrameRate()))
    print(frame_rate)
    if np.abs(frame_rate - 60) <= 1:
        frame_rate = 60
    elif np.abs(frame_rate - 144) <= 1:
        frame_rate = 144
    elif np.abs(frame_rate - 120) <= 1:
        frame_rate = 120
    logging.info(f"refresh rate: {frame_rate}")
    tm = np.zeros([len(stimuli), int(duration * frame_rate)])
    tmm = np.zeros([len(stimuli), 3, int(duration * frame_rate)])
    for idx, istim in enumerate(stimuli):
        freq = stimuli[istim]["freq"]
        time = np.array([x / frame_rate for x in range(len(tm[idx, :]))])
        phase = stimuli[istim]["phase"]
        Amp = (np.sin(2 * np.pi * freq * time + phase * np.pi)) + iti_color
        tm[idx, :] = Amp / 2
    tmm[:, 0, :] = tm[:, :]
    tmm[:, 1, :] = tm[:, :]
    tmm[:, 2, :] = tm[:, :]
    tmm = tmm.reshape(tmm.shape[0] * tmm.shape[1], tmm.shape[2]).T
    return tmm


def get_simple_keyboard(main_app):
    """Fast vectorized keyboard"""
    letters = string.digits + string.ascii_uppercase + "_" + "<" + "." + ","
    shape_x, shape_y = 5, 8
    letter_pos = np.array([x for x in letters]).reshape(shape_x, shape_y)
    n_text = len(letters)
    text_cap_size = 84
    text_strip_height = n_text * text_cap_size
    text_strip = np.full((text_strip_height, text_cap_size), np.nan)
    text = feedback.visual.TextStim(win=main_app.win, height=92, font="Arial", depth=-6)
    cap_rect_norm = [
        -(text_cap_size / 2.0) / (main_app.win.size[0] / 2.0),  # left
        +(text_cap_size / 2.0) / (main_app.win.size[1] / 2.0),  # top
        +(text_cap_size / 2.0) / (main_app.win.size[0] / 2.0),  # right
        -(text_cap_size / 2.0) / (main_app.win.size[1] / 2.0),  # bottom
    ]
    # capture the rendering of each letter
    for (i_letter, letter) in enumerate(letters):
        text.text = letter.upper()
        buff = feedback.visual.BufferImageStim(
            win=main_app.win, stim=[text], rect=cap_rect_norm
        )
        i_rows = slice(
            i_letter * text_cap_size, i_letter * text_cap_size + text_cap_size
        )
        text_strip[i_rows, :] = (
            np.flipud(np.array(buff.image)[..., 0]) / 255.0 * 2.0 - 1.0
        )
    # need to pad 'text_strip' to pow2 to use as a texture
    new_size = max(
        [
            int(np.power(2, np.ceil(np.log(dim_size) / np.log(2))))
            for dim_size in text_strip.shape
        ]
    )
    pad_amounts = []
    for i_dim in range(2):
        first_offset = int((new_size - text_strip.shape[i_dim]) / 2.0)
        second_offset = new_size - text_strip.shape[i_dim] - first_offset
        pad_amounts.append([first_offset, second_offset])
    text_strip = np.pad(
        array=text_strip, pad_width=pad_amounts, mode="constant", constant_values=0.0
    )
    # position the elements in rows
    x_axis = np.linspace(-700, 700, shape_y)
    y_axis = np.linspace(-400, 400, shape_x)
    xv, yv = np.meshgrid(x_axis, y_axis)
    el_xys = np.array((xv.ravel(), yv.ravel())).T
    # make a central mask to show just one letter
    xs, ys = text_strip.shape
    el_mask = np.ones((xs, ys)) * -1.0
    # start by putting the visible section in the corner
    el_mask[:text_cap_size, :text_cap_size] = 1.0
    # then roll to the middle
    el_mask = np.roll(
        el_mask, (int(new_size / 2) - int(text_cap_size / 2),) * 2, axis=(0, 1)
    )
    # work out the phase offsets for the different letters
    base_phase = ((text_cap_size * (n_text / 2.0)) - (text_cap_size / 2.0)) / new_size
    phase_inc = (text_cap_size) / float(new_size)
    phases = np.array(
        [(0.0, base_phase - i_letter * phase_inc) for i_letter in range(n_text)]
    )
    # starting colours
    colours = np.ones(shape=(n_text, 3))
    els = feedback.visual.ElementArrayStim(
        win=main_app.win,
        units="pix",
        nElements=n_text,
        sizes=text_strip.shape,
        xys=el_xys,
        phases=phases,
        colors=colours,
        elementTex=text_strip,
        elementMask=el_mask,
    )
    return els, colours, shape_x, shape_y, letters


def keyboard_live(
    main_app,
    stim_duration: float = 4,
    eeg=None,
    predict=None,
):
    """Keyboard SSVEP"""
    stimuli = get_simple_keyboard(main_app)
    answer_text = ''
    answer_text_stim = feedback.visual.TextStim(
        win=main_app.win, height=100, font="Arial", depth=-6
    )
    answer_text_stim.text = answer_text
    answer_text_stim.pos = np.array([0, 500])
    frame_rate = main_app.win.getActualFrameRate()
    logging.info(f"refresh rate: {frame_rate}")
    stim_freq_array1 = np.array(
        [14, 14.2, 14.4, 14.6, 14.8, 15, 15.2, 15.4, 15.6, 13.8, 8.4]
    )
    stim_freq_array2 = np.array([11.8, 13, 9.4, 12, 12.4, 13.4, 12.6, 10.2, 11.4, 11.6])
    stim_freq_array3 = np.array([8.6, 12.2, 9.2, 9.6, 9.8, 10, 10.4, 10.6, 10.8])
    stim_freq_array4 = np.array([13.6, 13.2, 9, 12.8, 8.8, 11.2, 11, 8])
    stim_freq_array5 = np.array([15.8, 8.2])
    phase_array1 = np.array([1, 1.5, 0, 0.5, 1, 1.5, 0, 0.5, 1, 0.5, 1])
    phase_array2 = np.array([1.5, 0.5, 1.5, 0, 1, 1.5, 1.5, 1.5, 0.5, 1])
    phase_array3 = np.array([1.5, 0.5, 1, 0, 0.5, 1, 0, 0.5, 1])
    phase_array4 = np.array([0, 1, 0.5, 0, 0, 0, 1.5, 0])
    phase_array5 = np.array([1.5, 0.5])
    stim_freq_array = np.concatenate(
        [
            stim_freq_array1,
            stim_freq_array2,
            stim_freq_array3,
            stim_freq_array4,
            stim_freq_array5,
        ]
    )
    phase_array = np.concatenate(
        [phase_array1, phase_array2, phase_array3, phase_array4, phase_array5]
    )
    all_symbols = {x: "" for x in stimuli[-1]}
    for istim, ifreq, iphase, idx in zip(
        all_symbols.keys(), stim_freq_array, phase_array, range(len(stimuli[-1]))
    ):
        all_symbols[istim] = {
            "freq": ifreq,
            "color": [1, 0, 0],
            "phase": iphase,
            "letter": istim,
            "idx": idx,
        }
    time_map = []
    time_map = get_color_map(all_symbols, stim_duration, main_app, iti_color=1)
    main_app.clear_text()
    stimuli[0].draw()
    main_app.flip()
    orig_col = stimuli[0].colors
    letters = stimuli[-1]
    num_stim = len(stimuli[-1])
    for idx in range(100):
        main_app.flip()
        stimuli[0].colors = orig_col
        stimuli[0].draw()
        answer_text_stim.draw()
        main_app.flip()
        main_app.wait(3)
        main_app.get_keys(keyList=["space", "q", "p"])
        if "q" in main_app.keys:
            break
        if eeg:
            eeg.annotate('0')
        for iframe in time_map:
            stimuli[0].colors = iframe.reshape(num_stim, 3)
            stimuli[0].draw()
            main_app.flip()
        if predict:
            try:
                stimuli[0].colors = orig_col
                stimuli[0].draw()
                main_app.flip()
                time.sleep(.5)
                guess, _ = predict.predict(stim_freq_array)
                new_col = orig_col.copy()
                new_col[guess, :] = [0, 1, 0]
                stimuli[0].colors = new_col
                stimuli[0].draw()
                if letters[guess] == '<':
                    if len(answer_text) > 1:
                        answer_text = answer_text[:-1]
                else:
                    answer_text += letters[guess]
                answer_text_stim.text = answer_text
                answer_text_stim.draw()
                main_app.flip()
                main_app.wait(3)
            except Exception as e:
                stimuli[0].colors = orig_col
                stimuli[0].draw()
                main_app.flip()
                logging.error("failed predict")
                logging.error(e)
    main_app.clear_text()
