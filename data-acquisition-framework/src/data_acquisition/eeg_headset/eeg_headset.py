from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock

from .errors import EEGHeadsetError


class EEGHeadset(ABC):
    def __init__(self, *, debug: bool = False, logger: Optional[Logger] = None) -> None:
        """
        :param debug: If True, the EEG device will not actually be used and no recording will be made.
        """

        self._is_debug_mode = debug
        self._is_running = False
        self._was_disconnected = False

        self._logger = logger if logger is not None else MagicMock()

    def start(self) -> None:
        """
        Starts EEG data acquisition.

        :raises EEGHeadsetError: If the EEG headset is already running, or if it had been disconnected.
        """

        self._check_not_disconnected()
        self._check_not_running()
        self._is_running = True

        self._log("Starting EEG headset")

        if self._is_debug_mode:
            return

        self._start()

    def _check_not_disconnected(self) -> None:
        if self._was_disconnected:
            raise EEGHeadsetError(
                "EEG headset has been disconnected and cannot be started again."
            )

    def _check_not_running(self) -> None:
        if self._is_running:
            raise EEGHeadsetError(
                "EEG headset has already been started and not stopped."
            )

    def _log(self, message: str) -> None:
        self._logger.info(f"{self.__class__.__name__}: {message}")

    @abstractmethod
    def _start(self) -> None:
        pass

    def stop_and_save_at_path(self, save_path: Path) -> None:
        """
        Stops EEG data acquisition and saves the recording at given path.

        :param save_path: Path to save the EEG recording.
        :raises EEGHeadsetError: If the EEG headset is not running, or if it had been disconnected.
        """

        self._check_not_disconnected()
        self._check_running()
        self._is_running = False

        self._log(f"Stopping EEG headset and saving at path: {save_path}")

        if self._is_debug_mode:
            return

        self._stop_and_save_at_path(save_path)

    def _check_running(self) -> None:
        if not self._is_running:
            raise EEGHeadsetError("EEG headset has not been started.")

    @abstractmethod
    def _stop_and_save_at_path(self, save_path: Path) -> None:
        pass

    def annotate(self, annotation: str) -> None:
        """
        Makes an annotation in the EEG recording.

        :param annotation: Annotation text.
        :raises EEGHeadsetError: If the EEG headset is not running, or if it had been disconnected.
        """

        self._check_not_disconnected()
        self._check_running()

        self._log(f"Adding annotation: {annotation}")

        if self._is_debug_mode:
            return

        self._annotate(annotation)

    @abstractmethod
    def _annotate(self, annotation: str) -> None:
        pass

    def disconnect(self) -> None:
        """
        Should be called after the EEG headset is no longer needed. Some EEG devices may perform cleanup operations here. If called, the object cannot be used anymore.

        :raises EEGHeadsetError: If the EEG headset has already been disconnected.
        """

        self._check_not_disconnected()
        self._disconnect()

    def _disconnect(self) -> None:
        pass
