from pathlib import Path
from unittest import TestCase

from src.data_acquisition.eeg_headset import EEGHeadset
from src.data_acquisition.eeg_headset.errors import EEGHeadsetError


class ExampleEEGHeadset(EEGHeadset):
    def __init__(self, *, debug: bool = False) -> None:
        super().__init__(debug=debug)

        self._was_any_method_called = False

    @property
    def was_any_method_called(self) -> bool:
        return self._was_any_method_called

    def _start(self) -> None:
        self._was_any_method_called = True

    def _stop_and_save_at_path(self, save_path: Path) -> None:
        self._was_any_method_called = True

    def _annotate(self, annotation: str) -> None:
        self._was_any_method_called = True


class TestEEGHeadset(TestCase):
    def setUp(self) -> None:
        self._headset = ExampleEEGHeadset()

    def test_methods_called_in_normal_mode(self) -> None:
        self._headset.start()
        self._headset.annotate("dummy_annotation")
        self._headset.stop_and_save_at_path(Path("dummy_path"))

        self.assertTrue(self._headset.was_any_method_called)

    def test_methods_not_called_in_debug_mode(self) -> None:
        headset = ExampleEEGHeadset(debug=True)

        headset.start()
        headset.annotate("dummy_annotation")
        headset.stop_and_save_at_path(Path("dummy_path"))

        self.assertFalse(headset.was_any_method_called)

    def test_throws_if_stop_called_before_start(self) -> None:
        with self.assertRaises(EEGHeadsetError):
            self._headset.stop_and_save_at_path(Path("dummy_path"))

    def test_throws_if_annotate_called_before_start(self) -> None:
        with self.assertRaises(EEGHeadsetError):
            self._headset.annotate("dummy_annotation")

    def test_throws_if_start_called_twice(self) -> None:
        self._headset.start()

        with self.assertRaises(EEGHeadsetError):
            self._headset.start()
