from logging import Logger
from pathlib import Path
from typing import Optional, Sequence

from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
from brainaccess.core.version import Version
from brainaccess.utils import acquisition

from .brainaccess_headset import BrainAccessHeadset


class BrainAccessV2Headset(BrainAccessHeadset):
    def __init__(
        self,
        *,
        bacore_version: Version,
        device_channels: Sequence[str],
        connection_port: str,
        debug: bool = False,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(device_channels=device_channels, debug=debug, logger=logger)

        self._connection_port = connection_port

        core.init(bacore_version)

    def _connect(self) -> None:
        self._eeg_manager = EEGManager()
        self._eeg_acquisition = acquisition.EEG()

        device_dict = self._convert_devices_to_dict(self._device_channels)

        self._setup(device_dict)

    def _setup(self, device_dict: dict[int, str]) -> None:
        self._eeg_acquisition.setup(
            self._eeg_manager, device_dict, port=self._connection_port
        )

    def _stop_and_save_at_path_after_delay(self, save_path: Path) -> None:
        self._eeg_acquisition.get_mne()
        self._eeg_acquisition.data.save(str(save_path))

        self._eeg_acquisition.stop_acquisition()

        self._eeg_manager.disconnect()
        self._eeg_manager.destroy()

        self._eeg_acquisition.close()
