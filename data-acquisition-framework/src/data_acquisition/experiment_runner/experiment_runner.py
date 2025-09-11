from logging import Logger
from typing import Callable, Generic, Optional, TypeVar
from unittest.mock import MagicMock

from ..eventful_screen import EventfulScreen
from ..gui import Gui
from ..sequencers import ScreenSequencer
from .errors import ExperimentRunnerError

T = TypeVar("T")


class ExperimentRunner(Generic[T]):
    def __init__(
        self,
        *,
        gui: Gui,
        screen_sequencer: ScreenSequencer[T],
        end_callback: Callable[[], None] = lambda: None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._gui = gui
        self._gui.on_init(self._mark_as_should_run)

        self._screen_sequencer = screen_sequencer
        self._previous_screen: Optional[EventfulScreen[T]] = None

        self._end_callback = end_callback

        self._logger = logger if logger is not None else MagicMock()

        self._should_run = False
        self._is_running = True

    def _mark_as_should_run(self):
        self._should_run = True

    def run(self) -> None:
        while not self._should_run:
            pass

        self._log("Starting experiment")

        self._run_first_screen()

        while self._is_running:
            pass

        self._end_callback()

    def _log(self, message: str) -> None:
        self._logger.info(f"{self.__class__.__name__}: {message}")

    def _run_first_screen(self) -> None:
        first_screen = self._screen_sequencer.get_next()

        self._log(f"Showing a screen")

        self._previous_screen = first_screen
        first_screen.show(end_callback=self._go_to_next_screen)

    def _go_to_next_screen(self, result: T) -> None:
        if self._previous_screen is None:
            raise ExperimentRunnerError("No previous screen found.")

        self._previous_screen.exit()

        self._screen_sequencer.pass_previous_result(result)

        try:
            next_screen = self._screen_sequencer.get_next()
        except StopIteration:
            self._is_running = False
            return

        self._log(f"Showing a screen")

        self._previous_screen = next_screen
        next_screen.show(end_callback=self._go_to_next_screen)
