from colour import Color

from ..gui import Gui
from .default_config import BACKGROUND_COLOR, FONT_SIZE, TEXT_COLOR
from .screen import Screen


class TextScreen(Screen):
    def __init__(
        self,
        *,
        gui: Gui,
        text: str,
        font_size: int = FONT_SIZE,
        text_color: Color = TEXT_COLOR,
        background_color: Color = BACKGROUND_COLOR,
    ) -> None:
        self._text = text
        self._font_size = font_size
        self._text_color = text_color
        self._background_color = background_color
        super().__init__(gui=gui)

    def show(self) -> None:
        self._gui.draw_uniform_background(color=self._background_color)
        self._gui.draw_text(
            font_size=self._font_size, text=self._text, color=self._text_color
        )
