# -*- coding: utf-8 -*-
"""Helper functions for experiments with psychopy"""

# fmt: off
from os import environ
environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from typing import List, Optional
import time
import numpy as np
#  from psychopy import prefs
#  prefs.hardware['audioLib'] = ['PTB', 'pyo'] # type: ignore
from psychopy import visual, core, event, sound, gui, __version__
from psychopy.hardware import keyboard
import gc

# fmt: on


class Feedback:
    """BCI feedback visualisation."""

    def __init__(self):
        self.oval_size = None
        self.win: Optional[visual.Window] = None
        self.default_keyboard = None
        self.text: Optional[visual.TextStim] = None
        self.image: Optional[visual.ImageStim] = None
        self.circle_in = None
        self.circle_out = None
        self.keys = []
        self.text_color = [1, 1, 1]

    def get_experiment_info(self, sub: str, task: str, task_name: str):
        info = {
            "Subject": sub,
            "Task": task,
            "Task Name": task_name,
            "PsychoPy Version": __version__,
        }
        infoDlg = gui.DlgFromDict(
            dictionary=info,
            title="Experiment Information",
            order=["PsychoPy Version", "Subject", "Task"],
            tip={
                "Subject": "Number 01, 22 etc",
                "Task": "General task name",
                "Task Name": "Detailed name",
            },
            fixed=["PsychoPy Version"],
        )
        if infoDlg.OK:
            print(info)
        else:
            print("User Cancelled")
            core.quit()
        return info

    def performance(
        self,
        process_priority: str = "realtime",
        disable_gc: bool = True,
        fbo: bool = False,
    ):
        self.process_priority = process_priority
        if process_priority == "normal":
            pass
        elif process_priority == "high":
            core.rush(True)
        elif process_priority == "realtime":
            # Only makes a diff compared to 'high' on Windows.
            core.rush(True, realtime=True)
        else:
            print(
                "Invalid process priority:",
                process_priority,
                "Process running at normal.",
            )
            process_priority = "normal"
        self.disable_gc = disable_gc
        if disable_gc:
            gc.disable()
        self.fbo = fbo
        if not fbo:
            visual.useFBO = False  # ignore

    def performance_restore(self):
        if self.process_priority != "normal":
            core.rush(False)
            self.process_priority = "normal"
        if self.disable_gc:
            gc.enable()
            self.disable_gc = False

    def window(
        self,
        fullscr: bool = True,
        screen: int = 0,
        win_type: str = "glfw",
        size: list = [800, 800],
        color: list = [-1, -1, -1],
        units: Optional[str] = None,
    ):
        """Main window to draw on."""
        self.win = visual.Window(
            size=size,
            fullscr=fullscr,
            screen=screen,
            winType=win_type,
            allowGUI=True,
            monitor="testMonitor",
            color=color,
            colorSpace="rgb",
            useFBO=False,
            units=units,
        )
        self.win.mouseVisible = False
        self.default_keyboard = keyboard.Keyboard()
        self.text = visual.TextStim(
            win=self.win,
            name="text_cross",
            text="",
            font="Arial",
            pos=(0, 0),
            height=0.3,
            wrapWidth=None,
            ori=0,
            color="white",
            colorSpace="rgb",
            opacity=1,
            languageStyle="LTR",
            depth=-1.0,
        )
        self.text.setAutoDraw(True)
        self.win.flip()
        return self

    def wait(self, time: float = 1):
        """wait for time seconds"""
        core.wait(time)

    def get_grating(
        self,
        phase=0,
        mask=None,
        tex="sin",
        ori=0,
        pos=[0, 0],
        size=80,
        sf=0.2,
        color=(0, 1, 0),
    ):
        return visual.GratingStim(
            win=self.win,  # type: ignore
            mask=mask,
            tex=tex,
            ori=ori,
            pos=pos,
            color=color,
            size=size,
            sf=sf,
            phase=phase,
            #  color=self.text_color,
            colorSpace="rgb",
            opacity=1,
        )

    def get_elementarraystim(self, element_mask="circle", n_elements=1, sizes=1):
        return visual.ElementArrayStim(
            self.win,
            elementTex=None,  # ignore: type
            elementMask=element_mask,
            nElements=n_elements,
            sizes=sizes,
        )

    def get_image_stim(self, image="./images/00.png/", size=(0.2, 0.2), pos=(0.5, 0.5)):
        return visual.ImageStim(win=self.win, image=image, size=size, pos=pos)

    def get_buffer_image_stim(self, imgl):
        return visual.BufferImageStim(win=self.win, stim=imgl)  # ignore: type

    def get_TextStim(self, win, height, font, pos=[0, 0]):
        return visual.TextStim(
            win=win, height=height, font=font, pos=pos, color=self.text_color
        )

    def flip(self):
        """Update window elements."""
        self.win.flip()

    def close(self):
        """Close window."""
        self.win.close()
        core.quit()

    def wait_for_press(
        self, txt: str, buttons: List[str] = ["space"], height: float = 0.1
    ) -> str:
        """Stop and wait until the button is pressed

        Parameters
        ----------
        txt : str :
            Text displayed on window
        button:List[str] :
            (Default value = ['space'])
            list of button names to exit wait_for_press cycle
        """
        button = ""
        event.clearEvents()
        self.text.setText(txt)
        self.text.color = self.text_color
        self.text.setAutoDraw(True)
        self.text.height = height
        self.flip()
        continue_routine = True
        while continue_routine:
            keys = self.default_keyboard.getKeys(keyList=buttons)
            for pressed_button in buttons:
                if pressed_button in keys:
                    continue_routine = False
                    self.text.setAutoDraw(False)
                    self.win.flip()
                    button = pressed_button
        return button

    def wait_untill_press(self, button: List[str] = ["space"]) -> None:
        """Wait for button press and do nothing else

        Parameters:
            button(List[str]): list of button names to exit application(q) or continue

        """
        event.clearEvents()
        wait = True
        while wait:
            keys = self.default_keyboard.getKeys(keyList=button)
            for key in button:
                if key in keys:
                    wait = False
        self.win.flip()

    def cross(self, height: float = 0.1):
        """Shortcut to display +"""
        self.text.setText("+")
        self.text.color = self.text_color
        self.text.height = height
        self.text.setAutoDraw(True)
        self.win.flip()

    def timer(self, tim: int = 1000):
        """Display timer up to tim ms"""
        timer_time = time.time()
        while time.time() - timer_time < tim / 1000:
            time.sleep(0.1)
            self.draw_text(f"{time.time()-timer_time:.2}")
            self.get_keys()
            if "space" in self.keys:
                break
            if "q" in self.keys:
                self.close()
        return time.time() - timer_time

    def draw_text(self, txt: str, pos=np.array([0, 0]), height: float = 0.1):
        """Change text on window

        Parameters
        ----------
        txt : str:
            Text displayed on the window
        """
        self.text.setText(txt)
        self.text.height = height
        self.text.color = self.text_color
        self.text.setAutoDraw(True)
        self.text.pos = pos
        self.win.flip()

    def clear_text(self):
        """Clear text on the window."""
        self.text.setAutoDraw(False)
        self.win.flip()

    def get_keys(self, keyList: List = ["space", "q"]):
        self.keys = self.default_keyboard.getKeys(keyList=keyList)

    def draw_oval(self, color):
        """Draw circles

        Parameters
        ----------
        color :
            color of the inner circle
        """
        self.circle_out = visual.Circle(
            win=self.win,
            units="pix",
            radius=150,
            fillColor=None,  # [0, 0, 0],
            lineColor=[-1, -1, -1],
            lineWidth=3,
            edges=128,
        )
        self.circle_in = visual.Circle(
            win=self.win,
            units="pix",
            radius=75,
            #  fillColor=[0, 1, 0],
            fillColor=color,
            lineColor=[-0, -0, -0],
            lineWidth=0,
            edges=128,
            opacity=0.5,
        )
        self.circle_out.draw()
        self.circle_in.draw()
        self.win.flip()

    def update_oval(self, a, b, color):
        """Redraw circles with different radius

        Parameters
        ----------
        a :
           Last test value
        b :
           Original test test value
        color :
           color of the inner circle
        """
        self.circle_in.radius = self.circle_out.radius * a / b
        self.circle_in.fillColor = color
        self.circle_in.draw()
        self.circle_out.draw()
        self.win.flip()

    def update_oval2(self, a, b, color):
        """Redraw circles with different radius

        Parameters
        ----------
        a :
           Last test value
        b :
           Original test value
        color :
           color of the inner circle
        """
        newradius = self.circle_out.radius * (a / b)
        oldradius = self.circle_in.radius
        adjustment = (newradius - oldradius) / 10
        for _ in range(10):
            oldradius = oldradius + adjustment
            self.circle_in.radius = oldradius
            self.circle_in.fillColor = color
            self.circle_in.draw()
            self.circle_out.draw()
            self.win.flip()
            time.sleep(0.01)

    def sound_warning(self, note: str = "A", duration: float = 0.5):
        my_sound = sound.Sound(note, secs=duration)
        my_sound.play()
