import time
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Optional, Sequence

from brainaccess.utils import acquisition

from ..eeg_headset import EEGHeadset
from .constants import AFTER_START_ACQUISITION_DELAY_SECS, BEFORE_SAVE_EEG_DELAY_SECS


class BrainAccessHeadset(EEGHeadset, ABC):
    _eeg_acquisition: acquisition.EEG

    def __init__(
        self,
        *,
        device_channels: Sequence[str],
        after_start_acquisition_delay_secs: int = AFTER_START_ACQUISITION_DELAY_SECS,
        before_save_eeg_delay_secs: int = BEFORE_SAVE_EEG_DELAY_SECS,
        debug: bool = False,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(debug=debug, logger=logger)

        self._device_channels = device_channels
        self._after_start_acquisition_delay_secs = after_start_acquisition_delay_secs
        self._before_save_eeg_delay_secs = before_save_eeg_delay_secs

    def _start(self) -> None:
        self._connect()
        self._eeg_acquisition.start_acquisition()
        time.sleep(self._after_start_acquisition_delay_secs)

    @abstractmethod
    def _connect(self) -> None:
        pass

    def _convert_devices_to_dict(
        self, device_channels: Sequence[str]
    ) -> dict[int, str]:
        return {idx: channel for idx, channel in enumerate(device_channels)}

    def _annotate(self, annotation: str) -> None:
        self._eeg_acquisition.annotate(annotation)

    def _stop_and_save_at_path(self, save_path: Path) -> None:
        time.sleep(self._before_save_eeg_delay_secs)
        self._stop_and_save_at_path_after_delay(save_path)

    @abstractmethod
    def _stop_and_save_at_path_after_delay(self, save_path: Path) -> None:
        pass
