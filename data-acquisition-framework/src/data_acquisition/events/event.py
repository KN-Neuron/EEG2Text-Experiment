from abc import ABC, abstractmethod
from logging import Logger
from typing import Optional
from unittest.mock import MagicMock

from ..types import EventCallback
from .errors import IncorrectMethodCallOrderError


class Event(ABC):
    def __init__(self, *, logger: Optional[Logger] = None) -> None:
        self._is_listening = False
        self._subscribers: list[EventCallback] = []

        self._logger = logger if logger is not None else MagicMock()

    def start_listening(self) -> None:
        self._check_is_not_listening()

        self._is_listening = True

        self._log("Starting to listen for events")

        self._start_listening()

    def _log(self, message: str) -> None:
        self._logger.debug(f"{self.__class__.__name__}: {message}")

    def _check_is_not_listening(self) -> None:
        if self._is_listening:
            raise IncorrectMethodCallOrderError("Event is already listening.")

    @abstractmethod
    def _start_listening(self) -> None:
        pass

    def stop_listening(self) -> None:
        self._check_is_listening()

        self._log("Stopping listening for events")

        self._stop_listening()

        self._is_listening = False

    def _check_is_listening(self) -> None:
        if not self._is_listening:
            raise IncorrectMethodCallOrderError("Event has not started listening yet.")

    @abstractmethod
    def _stop_listening(self) -> None:
        pass

    def subscribe(self, callback: EventCallback) -> None:
        self._log(f"Subscribing callback: {callback}")

        self._subscribers.append(callback)

    def unsubscribe(self, callback: EventCallback) -> None:
        self._log(f"Unsubscribing callback: {callback}")

        self._subscribers.remove(callback)

    def _trigger_callbacks(self) -> None:
        self._log(f"Triggering callbacks")

        for subscriber in self._subscribers:
            subscriber()

    @abstractmethod
    def clone(self) -> "Event":
        """
        Method used to create a clone of the event, so that it can be used as a prototype and reused by event managers.

        :return: A new instance of the same type as this event, with the same configuration.
        """

        pass
