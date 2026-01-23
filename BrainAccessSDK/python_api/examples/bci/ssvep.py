# -*- coding: utf-8 -*-
"""Helper SSVEP functions"""

from sys import platform
import ctypes

if platform == "linux" or platform == "linux2":
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()
import numpy as np
import logging


def get_frequencies(
    main_app, cycle: tuple = None, stim_dur: float = 1
) -> dict:
    """Get ssvep frequency parameteres"""
    frame_rate = np.round(main_app.win.getActualFrameRate())
    freq = frame_rate / sum(cycle)
    n_cycles = int(stim_dur * freq)
    return {"cycle": cycle, "freq": freq, "n_cycles": n_cycles}


def get_time_map(stimuli, duration: float, main_app, modulation: float = 0):
    frame_rate = int(np.round(main_app.win.getActualFrameRate()))
    print(frame_rate)
    logging.info(f"refresh rate: {frame_rate}")
    tm = np.zeros([len(stimuli), int(duration * frame_rate)])
    for idx, istim in enumerate(stimuli):
        cycle = sum(stimuli[istim]["cycle"])
        on = stimuli[istim]["cycle"][0]
        of = stimuli[istim]["cycle"][1]
        tm[idx, :] = (
            ([1] * on + [1 * modulation] * of) * int(duration * frame_rate / cycle + 1)
        )[: int(frame_rate * duration)]
    return tm


def stimulation(
    main_app,
    predict=None,
):
    """4 target SSVEP"""
    # Setting stimulus up
    multiplier: int = 16
    stimuli = ["down", "right", "left", "up"]
    stimuli = {f"{x}_{idx}": "" for x in stimuli for idx in range(multiplier)}
    stimuli["mark1"] = ""
    stimuli["mark2"] = ""
    n_stimuli = len(stimuli)
    size_stimuli = 0.1
    stimulus = main_app.get_elementarraystim(
        n_elements=n_stimuli, sizes=size_stimuli, element_mask="None"
    )
    stimulus.sizes[-1, :] = [0.05, 0.05]
    stimulus.sizes[-2, :] = [0.05, 0.05]
    col = np.array([[1, 1, 1] for _ in range(n_stimuli)])
    col[-1, :] = [1, 0, 0]
    col[-2, :] = [1, 0, 0]
    stimulus.colors = col
    # original sizes
    orig_size = stimulus.sizes
    loc = np.zeros([n_stimuli, 2])
    sq_m = int(np.sqrt(multiplier))
    x_axis = np.linspace(-0.2, 0.2, sq_m)
    y_axis = np.linspace(-0.2, 0.2, sq_m)
    xv, yv = np.meshgrid(x_axis, y_axis)
    coords = np.array((xv.ravel(), yv.ravel())).T
    co = np.array([[0.7, 0], [0, 0.7], [-0.7, 0], [0, -0.7]])
    loc[:-2, :] = np.array([x + y for x in co for y in coords])
    stimulus.xys = loc
    # Stimulation frequencies
    stim_freq_cycle = [
        x for x in [(5, 6), (3, 4), (4, 5), (2, 3)] for _ in range(multiplier)
    ]
    stim_freq_cycle.append((30, 30))
    stim_freq_cycle.append((30, 30))
    # Duration of demo
    stim_duration = 400
    for istim, icycle in zip(stimuli.keys(), stim_freq_cycle):
        stimuli[istim] = get_frequencies(main_app, stim_dur=stim_duration, cycle=icycle)
    stim_freq_array = [round(stimuli[x]["freq"], 2) for x in stimuli]
    stim_freq_array = stim_freq_array[:-2][::multiplier]
    # Setting prediction parameters
    if predict:
        predict.frequencies = stim_freq_array
        predict.sample_rate = 250
        predict.start()
    time_map = get_time_map(stimuli, stim_duration, main_app)
    time_map[-1, :] = 1
    time_map[-2, :] = 1
    # Start drawing
    main_app.clear_text()
    stimulus.draw()
    main_app.flip()
    main_app.wait(1)
    main_app.get_keys(keyList=["space", "q", "p"])
    for iframe in time_map.T:
        stimulus.draw()
        main_app.flip()
        if predict:
            if not predict.thread_flag:
                break
            guess, pass_guess = predict.get_guess()
            if pass_guess:
                loc[-1, :] = loc[int(guess * multiplier + sq_m + 6), :]
                loc[-2, :] = loc[int(guess * multiplier + sq_m + 5), :]
                col[-1, :] = [1, 1, 0]
                col[-2, :] = [1, 1, 0]
            else:
                loc[-1, :] = np.array([0, 0])
                loc[-2, :] = np.array([0, 0])
                col[-1, :] = [1, 1, 0]
                col[-2, :] = [1, 1, 0]
                stimulus.colors = col
            stimulus.xys = loc
        stimulus.sizes = iframe.T.reshape(n_stimuli, 1) * orig_size
    stimulus.sizes = orig_size
    stimulus.draw()
    main_app.flip()
    main_app.clear_text()
