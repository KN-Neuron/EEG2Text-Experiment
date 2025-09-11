from colour import Color

from ..gui import Gui
from ..types import Point
from .default_config import (
    BACKGROUND_COLOR,
    FIXATION_CROSS_COLOR,
    FIXATION_CROSS_LENGTH_AS_WINDOW_WIDTH_PERCENTAGE,
    FIXATION_CROSS_WIDTH_AS_WINDOW_WIDTH_PERCENTAGE,
)
from .screen import Screen


class FixationCrossScreen(Screen):
    def __init__(
        self,
        *,
        gui: Gui,
        fixation_cross_color: Color = FIXATION_CROSS_COLOR,
        background_color: Color = BACKGROUND_COLOR,
        fixation_cross_width_as_window_width_percentage: float = FIXATION_CROSS_WIDTH_AS_WINDOW_WIDTH_PERCENTAGE,
        fixation_cross_length_as_window_width_percentage: float = FIXATION_CROSS_LENGTH_AS_WINDOW_WIDTH_PERCENTAGE,
    ) -> None:
        self._background_color = background_color
        self._fixation_cross_color = fixation_cross_color
        self._fixation_cross_width_as_window_width_percentage = (
            fixation_cross_width_as_window_width_percentage
        )
        self._fixation_cross_length_as_window_width_percentage = (
            fixation_cross_length_as_window_width_percentage
        )
        super().__init__(gui=gui)

    def show(self) -> None:
        window_size = self._gui.get_window_size()

        center_x = window_size.width // 2
        center_y = window_size.height // 2

        fixation_cross_width = int(
            window_size.width * self._fixation_cross_width_as_window_width_percentage
        )
        fixation_cross_length = int(
            window_size.width * self._fixation_cross_length_as_window_width_percentage
        )

        self._gui.draw_uniform_background(color=self._background_color)
        self._gui.draw_rectangle(
            color=self._fixation_cross_color,
            top_left_point=Point(
                center_x - fixation_cross_width // 2,
                center_y - fixation_cross_length // 2,
            ),
            width=fixation_cross_width,
            height=fixation_cross_length,
        )
        self._gui.draw_rectangle(
            color=self._fixation_cross_color,
            top_left_point=Point(
                center_x - fixation_cross_length // 2,
                center_y - fixation_cross_width // 2,
            ),
            width=fixation_cross_length,
            height=fixation_cross_width,
        )
