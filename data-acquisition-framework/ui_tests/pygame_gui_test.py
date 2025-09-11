from threading import Thread

from colour import Color

from src.data_acquisition.gui import PygameGui
from src.data_acquisition.gui.display_mode import WindowedDisplayMode
from src.data_acquisition.gui.event_types import (
    Key,
    KeyPressEventType,
    TimeoutEventType,
)
from src.data_acquisition.types import Point

COLOR_WHITE = Color("white")
COLOR_BLACK = Color("black")


class GuiTester:
    def test(self) -> None:
        self._gui = PygameGui(
            WindowedDisplayMode(width=800, height=600), window_title="Pygame GUI Test"
        )
        self._gui.on_init(lambda: Thread(target=self._run_test).start())
        self._gui.start()

    def _run_test(self) -> None:
        self._gui.subscribe_to_event_and_get_id(
            event=TimeoutEventType(timeout_millis=5000),
            callback=lambda: self._gui.stop(),
        )
        self._gui.subscribe_to_event_and_get_id(
            event=KeyPressEventType(key=Key.SHIFT_LEFT), callback=self._draw_text
        )
        self._gui.subscribe_to_event_and_get_id(
            event=KeyPressEventType(key=Key.SHIFT_RIGHT), callback=self._draw_rect
        )

        self._gui.draw_uniform_background(COLOR_WHITE)

    def _draw_text(self) -> None:
        self._gui.draw_uniform_background(COLOR_WHITE)
        self._gui.draw_text(font_size=16, text="Hello", color=COLOR_BLACK)

    def _draw_rect(self) -> None:
        self._gui.draw_uniform_background(COLOR_BLACK)

        size = self._gui.get_window_size()
        x_center = size.width // 2
        y_center = size.height // 2
        one_fourth_width = x_center // 2
        one_fourth_height = y_center // 2

        self._gui.draw_rectangle(
            color=COLOR_WHITE,
            top_left_point=Point(x_center, y_center),
            width=one_fourth_width,
            height=one_fourth_height,
        )
