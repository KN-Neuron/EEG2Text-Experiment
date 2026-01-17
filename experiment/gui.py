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

        self.bg_color = '#D3D3D3'
        self.root.configure(bg=self.bg_color)

        # Kluczowa linia dla odświeżenia geometrii
        self.root.update()

        # Poprawny pomiar ekranu po update()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.logger.info(f"GUI initialized with CORRECT screen size: {self.screen_width}x{self.screen_height}")

        # Skalowanie czcionek względem rozdzielczości
        base_size_calc = min(self.screen_width, self.screen_height) // 25
        self.base_font_size = base_size_calc

        self.text_font = ('Arial', self.base_font_size, 'bold')
        self.instruction_font = ('Arial', int(self.base_font_size * 0.85), 'bold')
        self.feedback_font = ('Arial', self.base_font_size, 'bold')
        self.small_instruction_font = ('Arial', int(self.base_font_size * 0.7), 'normal')

        fixation_size = self.base_font_size * 4
        self.fixation_font = ('Arial', fixation_size, 'bold')

        self.logger.info(f"Font sizes - Calculated Base: {self.base_font_size}, Fixation: {fixation_size}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.canvas.pack(expand=True, fill='both')

        # Wyjście awaryjne Escape
        self.root.bind('<Escape>', lambda e: self.close())

        self.waiting_for_key = False
        self.key_pressed = None

    def show_welcome(self):
        self.clear()
        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text="Witaj w badaniu EEG2Text\n\nNaciśnij SPACJĘ by rozpocząć",
            font=self.instruction_font,
            fill='black',
            justify='center'
        )
        self.root.update()
        self.wait_for_space()

    def show_colored_instruction(self, title: str, text: str, color: str = '#E8F4F8'):
        self.clear()
        self.canvas.configure(bg=color)

        title_y = self.screen_height // 15
        self.canvas.create_text(
            self.screen_width // 2,
            title_y,
            text=title,
            font=('Arial', self.base_font_size + 7, 'bold'),
            fill='#2C3E50',
            justify='center'
        )

        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2,
            text=text,
            font=self.instruction_font,
            fill='black',
            justify='center',
            width=self.screen_width * 0.85
        )

        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height - 80,
            text="Naciśnij SPACJĘ by kontynuować",
            font=self.small_instruction_font,
            fill='#555555',
            justify='center'
        )

        self.root.update()
        self.wait_for_space()
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
        self.canvas.create_text(
            cx, cy,
            text="+",
            font=self.fixation_font,
            fill='black'
        )
        self.root.update()
        # Używamy after+mainloop jako nieblokującej pauzy (dla systemu operacyjnego)
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
        self.clear()

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

        option_start_y = self.screen_height // 2
        option_spacing = max(60, self.screen_height // 15)

        for i, option in enumerate(options):
            y_pos = option_start_y + (i * option_spacing)
            self.canvas.create_text(
                self.screen_width // 2,
                y_pos,
                text=f"{i + 1}. {option}",
                font=self.instruction_font,
                fill='black',
                justify='center',
                width=self.screen_width * 0.8
            )

        instruction_y = self.screen_height - 100
        self.canvas.create_text(
            self.screen_width // 2,
            instruction_y,
            text=f"Naciśnij klawisz (1-{len(options)}) by udzielić odpowiedź",
            font=self.small_instruction_font,
            fill='#555555',
            justify='center'
        )

        self.root.update()

        # Oczekiwanie na klawisze numeryczne odpowiadające liczbie opcji
        valid_keys = [str(i + 1) for i in range(len(options))]
        key = self.wait_for_key(valid_keys)

        # Zwraca indeks (0, 1, 2...)
        return int(key) - 1 if key else 0

    def show_feedback(self, is_correct: bool, correct_index: int, options: List[str],
                      duration_ms: int = 2000):
        self.clear()

        if is_correct:
            bg_color = '#C8E6C9'
            self.canvas.configure(bg=bg_color)
            self.canvas.create_text(
                self.screen_width // 2,
                self.screen_height // 3,
                text="✓ CORRECT!",
                font=('Arial', self.base_font_size + 20, 'bold'),
                fill='#2E7D32',
                justify='center'
            )
            message = "Dobra robota!"
        else:
            bg_color = '#FFCDD2'
            self.canvas.configure(bg=bg_color)
            self.canvas.create_text(
                self.screen_width // 2,
                self.screen_height // 3,
                text="✗ BŁĄD",
                font=('Arial', self.base_font_size + 20, 'bold'),
                fill='#C62828',
                justify='center'
            )
            correct_option = options[correct_index]
            message = f"Poprawną odpowiedzią było:\n{correct_index + 1}. {correct_option}"

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
        self.canvas.configure(bg=self.bg_color)

    def show_instruction_overlay(self, text: str):
        # Pasek na dole ekranu (np. do "Słuchanie...")
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

        # Odliczanie czasu przerwy
        while time.time() < end_time:
            seconds_left = int(round(end_time - time.time()))
            if seconds_left < 0: seconds_left = 0

            # POPRAWIONE LITERÓWKI
            self.canvas.itemconfig(
                text_id,
                text=f"Czas na odpoczynek\n\n{seconds_left} sekund pozostało\n\nZrelaksuj się, możesz pomrugać..."
            )
            self.root.update()
            time.sleep(1.0)

        self.canvas.itemconfig(text_id, text="Przygotuj się...\n\nNastępny blok zaraz się rozpocznie")
        self.root.update()
        time.sleep(2.0)
        self.clear()

    def show_completion(self):
        self.clear()
        self.canvas.configure(bg='#E8F5E9')

        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 - 50,
            text="🎉 EKSPERYMENT ZAKOŃCZONY! 🎉",
            font=('Arial', self.base_font_size + 10, 'bold'),
            fill='#2E7D32',
            justify='center'
        )

        self.canvas.create_text(
            self.screen_width // 2,
            self.screen_height // 2 + 50,
            text="Dziękujemy za Twój udział!\n\nDane EEG zostały zapisane.\n\nNaciśnij SPACJĘ by wyjść.",
            font=self.instruction_font,
            fill='black',
            justify='center'
        )

        self.root.update()
        self.wait_for_space()
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