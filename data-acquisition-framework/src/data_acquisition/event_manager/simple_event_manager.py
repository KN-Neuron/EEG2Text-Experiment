from abc import ABC, abstractmethod
from logging import Logger
from typing import Generic, Optional, Sequence, TypeVar

from ..events import Event
from .event_manager import EventManager

T = TypeVar("T")


class SimpleEventManager(EventManager[T], Generic[T], ABC):
    def __init__(
        self, *, events: Sequence[Event], logger: Optional[Logger] = None
    ) -> None:
        super().__init__(logger=logger)

        self._events = events

    def _start(self) -> None:
        self._setup()

        for event in self._events:
            event.start_listening()

    @abstractmethod
    def _setup(self) -> None:
        pass

    def _stop(self) -> None:
        for event in self._events:
            event.stop_listening()

    def clone(self) -> "SimpleEventManager[T]":
        cloned_manager = self._clone()
        cloned_manager._clone_registered_callbacks_from(self)
        return cloned_manager

    @abstractmethod
    def _clone(self) -> "SimpleEventManager[T]":
        pass
