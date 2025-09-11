from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Optional

from .eeg_headset import EEGHeadset


class MockEEGHeadset(EEGHeadset):
    def __init__(self, *, logger: Optional[Logger] = None) -> None:
        super().__init__(debug=False, logger=logger)

    def _start(self) -> None:
        self._log_to_console(f"Started EEG acquisition")

    def _stop_and_save_at_path(self, save_path: Path) -> None:
        self._log_to_console(f"EEG saved at {save_path}")

    def _annotate(self, annotation: str) -> None:
        self._log_to_console(f"Annotated with {annotation}")

    def _log_to_console(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"{timestamp}: {message}")
