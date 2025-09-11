from logging import Logger
from typing import Optional
from unittest.mock import MagicMock

from src.data_acquisition.events import Event
from src.data_acquisition.gui import Gui
from src.data_acquisition.gui.event_types import Key


class MockEvent(Event):
    def _start_listening(self) -> None:
        pass

    def _stop_listening(self) -> None:
        pass

    def clone(self) -> Event:
        return MagicMock()

    def trigger_callbacks(self) -> None:
        self._trigger_callbacks()


class MockKeyPressEvent(MockEvent):
    _INSTANCES: dict[Key, "list[MockKeyPressEvent]"] = {}

    def __init__(self, *, gui: Gui, key: Key, logger: Optional[Logger] = None) -> None:
        super().__init__()

        self._INSTANCES.setdefault(key, []).append(self)

    @classmethod
    def reset_instances(cls) -> None:
        cls._INSTANCES = {}

    @classmethod
    def get_instance_for_key(cls, key: Key) -> "list[MockKeyPressEvent]":
        return cls._INSTANCES.get(key, [])


class MockTimeoutEvent(MockEvent):
    _INSTANCES: "list[MockTimeoutEvent]" = []

    def __init__(
        self, *, gui: Gui, timeout_millis: int, logger: Optional[Logger] = None
    ) -> None:
        super().__init__()

        self._timeout_millis = timeout_millis
        self._INSTANCES.append(self)

    @classmethod
    def reset_instances(cls) -> None:
        cls._INSTANCES = []

    @classmethod
    def get_instance_count(cls) -> int:
        return len(cls._INSTANCES)

    @classmethod
    def trigger_callback_for_all_instances(cls) -> None:
        for instance in cls._INSTANCES:
            instance.trigger_callbacks()

    @classmethod
    def get_first_instance_timeout(cls) -> int:
        return cls._INSTANCES[0]._timeout_millis
