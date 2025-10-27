# gui.py - IMPROVED VERSION

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
        
        # Comfortable gray background
        self.bg_color = '#D3D3D3'  # Light gray - easier on the eyes
        self.root.configure(bg=self.bg_color)
        
        self.root.update()
        
        self.screen_width = self.root.winfo_width()
        self.screen_height = self.root.winfo_height()
        self.logger.info(f"GUI initialized with screen size: {self.screen_width}x{self.screen_height}")
        
        # Font sizes
        base_size = min(self.screen_width, self.screen_height) // 8
        self.text_font = font.Font(family='Arial', size=base_size, weight='bold')
        self.instruction_font = font.Font(family='Arial', size=base_size // 2, weight='bold')
        self.small_instruction_font = font.Font(family='Arial', size=base_size // 3)
        
        fixation_size = min(self.screen_width, self.screen_height) // 10
        self.fixation_font = font.Font(family='Arial', size=fixation_size, weight='bold')
        
        # Feedback font
        self.feedback_font = font.Font(family='Arial', size=base_size // 2, weight='bold')
        
        self.logger.info(f"Font sizes - Text: {base_size}, Instruction: {base_size//2}, Fixation: {fixation_size}")
        
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg=self.bg_color,
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

    def show_colored_instruction(self, title: str, text: str, color: str = '#E8F4F8'):
        """
        Show instruction screen with colored background
        
        Args:
            title: Title text (e.g., "NORMAL READING")
            text: Instruction text
            color: Background color hex code
        """
        self.clear()
        
        # Set colored background
        self.canvas.configure(bg=color)
        
        # Title at top (larger, bold)
        title_y = self.screen_height // 5
        self.canvas.create_text(
            self.screen_width // 2,
            title_y,
            text=title,
            font=font.Font(family='Arial', size=self.instruction_font.cget('size') + 10, weight='bold'),
            fill='#2C3E50',  # Dark blue-gray
            justify='center'
        )
        
        # Main instruction text in center
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=self.instruction_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.85
        )
        
        # "Press SPACE to continue" at bottom
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height - 80,
            text="Press SPACE to continue",
            font=self.small_instruction_font,
            fill='#555555',
            justify='center'
        )
        
        self.root.update()
        self.wait_for_space()
        
        # Reset to normal gray background
        self.canvas.configure(bg=self.bg_color)

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
        
        cx, cy = self.screen_width // 2, self.screen_height // 2
        
        # Draw plus sign
        self.canvas.create_text(
            cx, cy,
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
            justify='center',
            width=self.screen_width * 0.9
        )
        self.root.update()
        if duration_ms:
            self.root.after(duration_ms, self.root.quit)
            self.root.mainloop()
        else:
            self.wait_for_space()
    
    def show_question(self, question: str, options: List[str]) -> int:
        """Display a multiple choice question and return the selected option index."""
        self.clear()
        
        # Display question at the top
        question_y = self.screen_height // 4
        self.canvas.create_text(
            self.screen_width // 2,
            question_y,
            text=question,
            font=self.instruction_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.9
        )
        
        # Display options with numbers
        option_start_y = self.screen_height // 2
        option_spacing = max(60, self.screen_height // 15)
        
        for i, option in enumerate(options):
            y_pos = option_start_y + (i * option_spacing)
            self.canvas.create_text(
                self.screen_width // 2,
                y_pos,
                text=f"{i+1}. {option}",
                font=self.instruction_font,
                fill='black',
                justify='center',
                width=self.screen_width * 0.8
            )
        
        # Instructions at bottom
        instruction_y = self.screen_height - 100
        self.canvas.create_text(
            self.screen_width // 2,
            instruction_y,
            text=f"Press the number key (1-{len(options)}) for your answer",
            font=self.small_instruction_font,
            fill='#555555',
            justify='center'
        )
        
        self.root.update()
        
        # Wait for number key press
        valid_keys = [str(i+1) for i in range(len(options))]
        key = self.wait_for_key(valid_keys)
        
        # Return the index (0-based)
        return int(key) - 1 if key else 0

    def show_feedback(self, is_correct: bool, correct_index: int, options: List[str], 
                     duration_ms: int = 2000):
        """
        Show feedback after a question is answered
        
        Args:
            is_correct: Whether the answer was correct
            correct_index: Index of the correct answer
            options: List of all options
            duration_ms: How long to show feedback
        """
        self.clear()
        
        if is_correct:
            # Green background for correct
            bg_color = '#C8E6C9'  # Light green
            self.canvas.configure(bg=bg_color)
            
            # Large checkmark or "Correct!"
            self.canvas.create_text(
                self.screen_width // 2,
                self.screen_height // 3,
                text="✓ CORRECT!",
                font=font.Font(family='Arial', size=self.feedback_font.cget('size') + 20, weight='bold'),
                fill='#2E7D32',  # Dark green
                justify='center'
            )
            
            message = "Well done!"
            
        else:
            # Light red background for incorrect
            bg_color = '#FFCDD2'  # Light red
            self.canvas.configure(bg=bg_color)
            
            # Large X or "Incorrect"
            self.canvas.create_text(
                self.screen_width // 2,
                self.screen_height // 3,
                text="✗ INCORRECT",
                font=font.Font(family='Arial', size=self.feedback_font.cget('size') + 20, weight='bold'),
                fill='#C62828',  # Dark red
                justify='center'
            )
            
            # Show correct answer
            correct_option = options[correct_index]
            message = f"The correct answer was:\n{correct_index + 1}. {correct_option}"
        
        # Additional message
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 + 50,
            text=message,
            font=self.instruction_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.8
        )
        
        self.root.update()
        self.root.after(duration_ms, self.root.quit)
        self.root.mainloop()
        
        # Reset to normal gray background
        self.canvas.configure(bg=self.bg_color)
            
    def show_instruction_overlay(self, text: str):
        y_pos = self.screen_height - 120
        rect_height = 100
        self.canvas.create_rectangle(
            0, y_pos - 20,
            self.screen_width, self.screen_height,
            fill=self.bg_color,
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
        self.clear()
        
        # Light green background for completion
        self.canvas.configure(bg='#E8F5E9')
        
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 - 50,
            text="🎉 EXPERIMENT COMPLETE! 🎉",
            font=font.Font(family='Arial', size=self.instruction_font.cget('size') + 10, weight='bold'),
            fill='#2E7D32',
            justify='center'
        )
        
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 + 50,
            text="Thank you for your participation!\n\nYour data has been saved.\n\nPress SPACE to exit.",
            font=self.instruction_font,
            fill='black',
            justify='center'
        )
        
        self.root.update()
        self.wait_for_space()
        
        # Reset background
        self.canvas.configure(bg=self.bg_color)

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