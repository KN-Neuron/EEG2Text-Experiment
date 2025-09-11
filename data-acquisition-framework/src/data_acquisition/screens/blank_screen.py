from colour import Color

from ..gui import Gui
from .default_config import BACKGROUND_COLOR
from .screen import Screen


class BlankScreen(Screen):
    def __init__(
        self,
        *,
        gui: Gui,
        background_color: Color = BACKGROUND_COLOR,
    ) -> None:
        self._background_color = background_color
        super().__init__(gui=gui)

    def show(self) -> None:
        self._gui.draw_uniform_background(color=self._background_color)
