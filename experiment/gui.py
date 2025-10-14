# gui.py

import tkinter as tk
from tkinter import font
import logging
import time
from typing import List, Optional

class ExperimentGUI:
    def __init__(self, logger: logging.Logger, debug_mode: bool = False):
        self.logger = logger
        self.debug_mode = debug_mode
        self.root = tk.Tk()
        self.root.title("EEG2Text Experiment" + (" [DEBUG]" if debug_mode else ""))
        
        self.root.attributes('-fullscreen', True)
        self.logger.info("Fullscreen mode enabled")

        
        if not debug_mode:
            self.root.config(cursor="none")
        
        self.root.configure(bg='white')
        
        self.root.update()
        
        self.screen_width = self.root.winfo_width()
        self.screen_height = self.root.winfo_height()
        self.logger.info(f"GUI initialized with screen size: {self.screen_width}x{self.screen_height}")
        
        # Make text MUCH larger - about 1/8 of screen height
        base_size = min(self.screen_width, self.screen_height) // 8
        self.text_font = font.Font(family='Arial', size=base_size, weight='bold')
        self.instruction_font = font.Font(family='Arial', size=base_size // 2, weight='bold')
        
        # Make fixation cross smaller - about 1/10 of screen height
        fixation_size = min(self.screen_width, self.screen_height) // 10
        self.fixation_font = font.Font(family='Arial', size=fixation_size, weight='bold')
        
        self.logger.info(f"Font sizes - Text: {base_size}, Instruction: {base_size//2}, Fixation: {fixation_size}")
        
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg='white',
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')
        self.root.bind('<Escape>', lambda e: self.close())
        self.waiting_for_key = False
        self.key_pressed = None

    def show_welcome(self):
        self.clear()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text="Welcome to the EEG2Text Experiment\n\nPress SPACE to begin",
            font=self.instruction_font,
            fill='black',
            justify='center'
        )
        self.root.update()
        self.wait_for_space()

    def show_instruction(self, text: str):
        self.clear()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=self.instruction_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.9 
        )
        self.root.update()
        self.wait_for_space()

    def show_sentence(self, text: str):
        self.clear()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=self.text_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.9
        )
        self.root.update()

    def show_fixation(self, duration_ms: int):
        self.clear()
        # Draw a plus sign with thick lines
        line_thickness = max(4, min(self.screen_width, self.screen_height) // 150)
        line_length = min(self.screen_width, self.screen_height) // 15  # Smaller cross
        cx, cy = self.screen_width // 2, self.screen_height // 2
        
        # Horizontal line
        self.canvas.create_line(
            cx - line_length, cy, 
            cx + line_length, cy, 
            fill='black', width=line_thickness
        )
        
        # Vertical line
        self.canvas.create_line(
            cx, cy - line_length, 
            cx, cy + line_length, 
            fill='black', width=line_thickness
        )
        
        # Alternative method: draw a "+" character with a large font
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text="+",
            font=self.fixation_font,
            fill='black'
        )
        
        self.root.update()
        self.root.after(duration_ms, self.root.quit)
        self.root.mainloop()

    def show_blank(self, duration_ms: int):
        self.clear()
        self.root.update()
        self.root.after(duration_ms, self.root.quit)
        self.root.mainloop()

    def show_message(self, text: str, duration_ms: Optional[int] = None):
        self.clear()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=self.instruction_font,
            fill='black',
            justify='center'
        )
        self.root.update()
        if duration_ms:
            self.root.after(duration_ms, self.root.quit)
            self.root.mainloop()
        else:
            self.wait_for_space()
            
    def show_instruction_overlay(self, text: str):
        y_pos = self.screen_height - 120
        rect_height = 100
        self.canvas.create_rectangle(
            0, y_pos - 20,
            self.screen_width, self.screen_height,
            fill='white',
            outline=''
        )
        self.canvas.create_text(
            self.screen_width // 2,
            y_pos + rect_height // 2 - 20,
            text=text,
            font=self.instruction_font,
            fill='black',
            justify='center'
        )
        self.root.update()

    def show_rest(self, duration_ms: int):
        self.clear()
        end_time = time.time() + duration_ms / 1000.0
        
        text_id = self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2,
            text="", font=self.instruction_font, fill='black', justify='center'
        )

        while time.time() < end_time:
            seconds_left = int(round(end_time - time.time()))
            if seconds_left < 0: seconds_left = 0
            self.canvas.itemconfig(
                text_id,
                text=f"Rest Period\n\n{seconds_left} seconds remaining\n\nRelax and blink freely..."
            )
            self.root.update()
            time.sleep(1.0)

        self.canvas.itemconfig(text_id, text="Get Ready...\n\nNext block starting soon")
        self.root.update()
        time.sleep(2.0)
        self.clear()

    def show_completion(self):
        self.show_message(
            "Experiment Complete!\n\n"
            "Thank you for your participation.\n\n"
            "Press SPACE to exit.",
            duration_ms=None
        )

    def _on_key_press(self, event, valid_keys):
        if event.keysym.lower() in valid_keys:
            self.key_pressed = event.keysym
            self.waiting_for_key = False
            self.root.quit()

    def wait_for_space(self):
        self.wait_for_key(['space'])

    def wait_for_key(self, valid_keys: List[str]):
        self.key_pressed = None
        self.waiting_for_key = True
        
        valid_keys_lower = [k.lower() for k in valid_keys]
        
        handler_id = self.root.bind(
            '<KeyPress>', 
            lambda event: self._on_key_press(event, valid_keys_lower)
        )
        
        self.root.focus_set()
        self.root.mainloop() 
        
        self.root.unbind('<KeyPress>', handler_id)
        return self.key_pressed

    def clear(self):
        self.canvas.delete('all')
        self.root.update_idletasks()

    def close(self):
        try:
            if self.root.winfo_exists():
                self.root.quit()
                self.root.destroy()
        except tk.TclError:
            pass