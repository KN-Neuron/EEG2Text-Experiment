from abc import ABC, abstractmethod
from logging import Logger
from typing import Generic, Optional, TypeVar, cast
from unittest.mock import MagicMock

from ..eventful_screen import EventfulScreen
from ..sequencers.errors import (
    IncorrectMethodCallOrderError,
    ScreenSequencerStopIteration,
)

T = TypeVar("T")


class ScreenSequencer(Generic[T], ABC):
    def __init__(self, *, logger: Optional[Logger] = None) -> None:
        self._logger = logger if logger is not None else MagicMock()

        self.__previous_result: Optional[T] = None
        self._was_first_element_gotten = False
        self._was_previous_result_provided = False

    @property
    def _previous_result(self) -> T:
        self._check_previous_result_provided()

        return cast(T, self.__previous_result)

    def _check_previous_result_provided(self) -> None:
        if self._was_first_element_gotten and not self._was_previous_result_provided:
            raise IncorrectMethodCallOrderError(
                "Previous result must be passed before getting the next element."
            )

    def get_next(self) -> EventfulScreen[T]:
        """
        :return: The next screen in the sequence.

        :raises IncorrectMethodCallOrderError: If the result of the previous screen was not provided (unless it's the first screen).
        :raises StopIteration: If there is no next screen in the sequence.
        """

        self._check_previous_result_provided()

        try:
            result = self._get_next()
        except ScreenSequencerStopIteration:
            self._log("No more screens in the sequence, raising StopIteration")

            raise StopIteration

        self._was_first_element_gotten = True
        self._was_previous_result_provided = False

        self._log(f"Got next screen: {result}")

        return result

    def _log(self, message: str) -> None:
        self._logger.debug(f"{self.__class__.__name__}: {message}")

    def pass_previous_result(self, result: T) -> None:
        """
        :param result: The result of the previous screen.

        :raises IncorrectMethodCallOrderError: If the result of the previous screen was already provided or before getting the first screen.
        """

        if not self._was_first_element_gotten:
            raise IncorrectMethodCallOrderError("First element not yet gotten.")

        if self._was_previous_result_provided:
            raise IncorrectMethodCallOrderError("Previous result already provided.")

        self._log(f"Got previous result: {result}")

        self.__previous_result = result
        self._was_previous_result_provided = True

    @abstractmethod
    def _get_next(self) -> EventfulScreen[T]:
        pass
