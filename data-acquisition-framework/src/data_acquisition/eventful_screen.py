from typing import Callable, Generic, TypeVar

from .event_manager import EventManager
from .screens import Screen
from .types import ResultEventCallback

T = TypeVar("T")


class EventfulScreen(Generic[T]):
    def __init__(
        self,
        *,
        screen: Screen,
        event_manager: EventManager[T],
        screen_show_callback: Callable[[], None] = lambda: None,
    ) -> None:
        self._screen = screen
        self._event_manager = event_manager
        self._screen_show_callback = screen_show_callback

    def show(self, *, end_callback: ResultEventCallback[T]) -> None:
        """
        Starts the event manager and shows the screen.
        """

        self._end_callback = end_callback

        self._event_manager.register_callback(end_callback)
        self._event_manager.start()
        self._screen.show()

        self._screen_show_callback()

    def exit(self) -> None:
        """
        Stops the event manager after exiting the screen.
        """

        self._event_manager.deregister_callback(self._end_callback)
        self._event_manager.stop()
