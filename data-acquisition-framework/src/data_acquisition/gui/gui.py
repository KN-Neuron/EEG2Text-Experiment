from abc import ABC, abstractmethod
from pathlib import Path

from colour import Color

from ..types import ElementSize, EventCallback, Point
from .event_types import EventType


class Gui(ABC):
    @abstractmethod
    def on_init(self, callback: EventCallback) -> None:
        """
        Used to register a callback function that will be called when the GUI is ready.
        """

        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_window_size(self) -> ElementSize:
        pass

    @abstractmethod
    def draw_uniform_background(self, color: Color) -> None:
        pass

    @abstractmethod
    def draw_text(self, *, font_size: int, text: str, color: Color) -> None:
        pass

    @abstractmethod
    def draw_rectangle(
        self, *, color: Color, top_left_point: Point, width: int, height: int
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_image(self, image_path: Path) -> None:
        pass

    @abstractmethod
    def play_sound(self, sound_path: Path) -> None:
        pass

    @abstractmethod
    def subscribe_to_event_and_get_id(
        self, *, event: EventType, callback: EventCallback
    ) -> int:
        """
        :return: An event ID that can be used to unsubscribe from the event later.
        """

        pass

    @abstractmethod
    def unsubscribe_from_event_by_id(self, event_id: int) -> None:
        """
        :param: event_id: The ID of the event to unsubscribe from, returned by the subscribe method.
        """

        pass
