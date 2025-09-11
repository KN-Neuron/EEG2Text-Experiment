from threading import Thread

from colour import Color

from src.data_acquisition.gui import PygameGui
from src.data_acquisition.gui.display_mode import WindowedDisplayMode
from src.data_acquisition.gui.event_types import TimeoutEventType
from src.data_acquisition.screens import BlankScreen, FixationCrossScreen, TextScreen

DEFAULT_SCREEN_DURATION_MILLIS = 1000


class ScreenTester:
    def __init__(
        self, *, screen_duration_millis: int = DEFAULT_SCREEN_DURATION_MILLIS
    ) -> None:
        self._screen_duration_millis = screen_duration_millis

    def run(self) -> None:
        self._gui = PygameGui(
            WindowedDisplayMode(width=800, height=600), window_title="Screens Test"
        )

        self._screens = [
            TextScreen(gui=self._gui, text="Hello World!"),
            TextScreen(
                gui=self._gui,
                text="Hello World!",
                text_color=Color("red"),
                background_color=Color("blue"),
            ),
            BlankScreen(gui=self._gui),
            BlankScreen(gui=self._gui, background_color=Color("green")),
            FixationCrossScreen(gui=self._gui),
            FixationCrossScreen(
                gui=self._gui, fixation_cross_length_as_window_width_percentage=0.5
            ),
            FixationCrossScreen(
                gui=self._gui, fixation_cross_length_as_window_width_percentage=0.7
            ),
            FixationCrossScreen(
                gui=self._gui, fixation_cross_width_as_window_width_percentage=0.05
            ),
            FixationCrossScreen(
                gui=self._gui, fixation_cross_width_as_window_width_percentage=0.06
            ),
            FixationCrossScreen(
                gui=self._gui,
                fixation_cross_color=Color("red"),
                background_color=Color("blue"),
            ),
        ]
        self._screens_idx = 0

        self._gui.on_init(lambda: Thread(target=self._show_next_screen).start())
        self._gui.start()

    def _show_next_screen(self) -> None:
        if self._screens_idx >= len(self._screens):
            self._gui.stop()
            return

        self._gui.subscribe_to_event_and_get_id(
            event=TimeoutEventType(timeout_millis=self._screen_duration_millis),
            callback=self._show_next_screen,
        )

        screen = self._screens[self._screens_idx]
        screen.show()
        self._screens_idx += 1


class LongSentencesScreenTester:
    def __init__(
        self, *, screen_duration_millis: int = DEFAULT_SCREEN_DURATION_MILLIS
    ) -> None:
        self._screen_duration_millis = screen_duration_millis

    def run(self) -> None:
        self._gui = PygameGui(
            WindowedDisplayMode(width=800, height=600), window_title="Screens Test"
        )

        self._screens = [
            TextScreen(gui=self._gui, font_size=40, text="Hello World!"),
            TextScreen(
                gui=self._gui,
                font_size=40,
                text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            ),
            TextScreen(
                gui=self._gui,
                font_size=40,
                text="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
            ),
            TextScreen(
                gui=self._gui,
                font_size=40,
                text="Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
            ),
            TextScreen(gui=self._gui, font_size=40, text="Hello World!"),
            TextScreen(
                gui=self._gui,
                text="Hello World!",
                text_color=Color("red"),
                background_color=Color("blue"),
            ),
        ]
        self._screens_idx = 0

        self._gui.on_init(lambda: Thread(target=self._show_next_screen).start())
        self._gui.start()

    def _show_next_screen(self) -> None:
        if self._screens_idx >= len(self._screens):
            self._gui.stop()
            return

        self._gui.subscribe_to_event_and_get_id(
            event=TimeoutEventType(timeout_millis=self._screen_duration_millis),
            callback=self._show_next_screen,
        )

        screen = self._screens[self._screens_idx]
        screen.show()
        self._screens_idx += 1
