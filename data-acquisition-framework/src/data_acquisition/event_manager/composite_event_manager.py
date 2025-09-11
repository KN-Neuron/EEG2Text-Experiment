from logging import Logger
from typing import Generic, Optional, Sequence, TypeVar

from .event_manager import EventManager

T = TypeVar("T")


class CompositeEventManager(EventManager[T], Generic[T]):
    def __init__(
        self,
        *,
        event_managers: Sequence[EventManager[T]],
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(logger=logger)

        self._event_managers = event_managers

    def _start(self) -> None:
        for event_manager in self._event_managers:
            event_manager.register_callback(self._trigger_callbacks)

            event_manager.start()

    def _stop(self) -> None:
        for event_manager in self._event_managers:
            event_manager.stop()

    def clone(self) -> "CompositeEventManager[T]":
        submanager_clones = [
            event_manager.clone() for event_manager in self._event_managers
        ]

        for event_manager in submanager_clones:
            event_manager._clone_registered_callbacks_from(self)

        return CompositeEventManager(event_managers=submanager_clones)
