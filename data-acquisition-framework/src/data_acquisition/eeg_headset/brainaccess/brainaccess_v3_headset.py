from logging import Logger
from pathlib import Path
from typing import Optional, Sequence

from brainaccess.core.eeg_manager import EEGManager
from brainaccess.utils import acquisition

from .brainaccess_headset import BrainAccessHeadset


class BrainAccessV3Headset(BrainAccessHeadset):
    def __init__(
        self,
        *,
        device_name: str,
        device_channels: Sequence[str],
        debug: bool = False,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(device_channels=device_channels, debug=debug, logger=logger)

        self._device_name = device_name
        self._was_already_connected = False

    def _connect(self) -> None:
        if not self._was_already_connected:
            self._eeg_manager = EEGManager()
            self._eeg_acquisition = acquisition.EEG()

            device_dict = self._convert_devices_to_dict(self._device_channels)

            self._setup(device_dict)

            self._was_already_connected = True

    def _setup(self, device_dict: dict[int, str]) -> None:
        device_dict = self._convert_devices_to_dict(self._device_channels)

        self._eeg_acquisition.setup(
            self._eeg_manager, device_name=self._device_name, cap=device_dict
        )

    def _stop_and_save_at_path_after_delay(self, save_path: Path) -> None:
        self._eeg_acquisition.get_mne()
        self._eeg_acquisition.stop_acquisition()

        self._eeg_acquisition.data.save(str(save_path))

        self._eeg_manager.clear_annotations()
        self._eeg_acquisition.data = acquisition.EEGData(
            self._eeg_acquisition.data.eeg_info,
            lock=self._eeg_acquisition.lock,
            zeros_at_start=0,
        )

    def disconnect(self) -> None:
        self._eeg_manager.disconnect()
        self._eeg_manager.destroy()

        self._eeg_acquisition.close()
