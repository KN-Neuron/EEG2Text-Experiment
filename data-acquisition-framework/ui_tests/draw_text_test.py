from threading import Thread

from colour import Color

from src.data_acquisition.gui import PygameGui
from src.data_acquisition.gui.display_mode import WindowedDisplayMode
from src.data_acquisition.gui.event_types import TimeoutEventType

DEFAULT_SCREEN_DURATION_MILLIS = 1000

TEST_SENTENCES = [
    "Wczorajsze warsztaty rozwinęły moje umiejętności negocjacyjne i komunikacyjne.",
    "Badania terenowe dostarczają unikalnych danych.",
    "The researchers documented every aspect of their groundbreaking experiment.",
    "Rain fell steadily during the long night.",
]


class DrawTextTester:
    def __init__(
        self, *, screen_duration_millis: int = DEFAULT_SCREEN_DURATION_MILLIS
    ) -> None:
        self._screen_duration_millis = screen_duration_millis

    def run(self) -> None:
        self._gui = PygameGui(
            WindowedDisplayMode(width=800, height=600), window_title="Draw Text Test"
        )

        self._sentences_idx = 0

        self._gui.on_init(lambda: Thread(target=self._show_next_screen).start())
        self._gui.start()

    def _show_next_screen(self) -> None:
        if self._sentences_idx >= len(TEST_SENTENCES):
            self._gui.stop()
            return

        self._gui.subscribe_to_event_and_get_id(
            event=TimeoutEventType(timeout_millis=self._screen_duration_millis),
            callback=self._show_next_screen,
        )

        sentence = TEST_SENTENCES[self._sentences_idx]

        self._gui.draw_uniform_background(Color("white"))
        self._gui.draw_text(font_size=32, text=sentence, color=Color("black"))

        self._sentences_idx += 1
