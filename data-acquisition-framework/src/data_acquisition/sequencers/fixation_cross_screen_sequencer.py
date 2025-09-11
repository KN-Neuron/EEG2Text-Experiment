from logging import Logger
from typing import Callable, Generic, Optional, TypeVar, cast

from ..event_manager import EventManager
from ..eventful_screen import EventfulScreen
from ..gui import Gui
from ..screens import FixationCrossScreen
from .screen_sequencer import ScreenSequencer
from .simple_screen_sequencer import SimpleScreenSequencer

T = TypeVar("T")


class FixationCrossScreenSequencer(SimpleScreenSequencer[T], Generic[T]):
    def __init__(
        self,
        *,
        gui: Gui,
        subsequencer: ScreenSequencer[T],
        fixation_screen_event_manager: EventManager[T],
        screen_show_callback: Callable[[str], None] = lambda _: None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        :param gui:
        :param subsequencer: A subsequencer that provides the screens to be shown after fixation crosses.
        :param fixation_screen_event_manager: An event manager that ends the fixation cross screen.
        """

        super().__init__(
            gui=gui, screen_show_callback=screen_show_callback, logger=logger
        )

        self._subsequencer = subsequencer
        self._fixation_screen_event_manager = fixation_screen_event_manager

        self._idx = 0
        self._next_subsequencer_screen: Optional[EventfulScreen[T]] = None

    def _get_next(self) -> EventfulScreen[T]:
        self._pass_previous_result_if_needed()
        self._get_next_subsequencer_screen_if_needed_or_raise_stop()

        is_at_fixation_cross = self._is_at_fixation_cross()
        self._idx += 1

        if is_at_fixation_cross:
            fixation_cross_screen = FixationCrossScreen(gui=self._gui)

            return EventfulScreen(
                screen=fixation_cross_screen,
                event_manager=self._fixation_screen_event_manager.clone(),
            )

        return cast(EventfulScreen[T], self._next_subsequencer_screen)

    def _pass_previous_result_if_needed(self) -> None:
        if self._should_pass_previous_result():
            self._subsequencer.pass_previous_result(self._previous_result)

    def _should_pass_previous_result(self) -> bool:
        return self._was_first_element_gotten and self._is_at_fixation_cross()

    def _is_at_fixation_cross(self) -> bool:
        return self._idx % 2 == 0

    def _get_next_subsequencer_screen_if_needed_or_raise_stop(self) -> None:
        if not self._was_first_element_gotten or self._is_at_fixation_cross():
            try:
                self._next_subsequencer_screen = self._subsequencer.get_next()
            except StopIteration:
                raise StopIteration

    def reset(self) -> None:
        """
        Resets the sequencer so that the next returned screen will be a fixation cross screen.

        Does not reset the subsequencer.
        """

        self._idx -= 1
