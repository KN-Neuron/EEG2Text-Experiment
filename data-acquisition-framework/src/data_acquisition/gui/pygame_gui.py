from collections import deque
from functools import partial, wraps
from logging import Logger
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, cast
from unittest.mock import MagicMock

import pygame
from colour import Color

from ..types import ElementSize, EventCallback, Point
from .display_mode import DisplayMode, FullscreenDisplayMode, WindowedDisplayMode
from .errors import DrawError, GuiError
from .event_types import EventType
from .event_types.key_press_event_type import KEY_MAPPING, KeyPressEventType
from .event_types.timeout_event_type import TimeoutEventType
from .gui import Gui

T = TypeVar("T", bound=Callable[..., None])


class PygameGui(Gui):
    def __init__(
        self,
        display_mode: DisplayMode,
        window_title: str,
        logger: Optional[Logger] = None,
    ):
        super().__init__()

        self._display_mode = display_mode
        self._window_title = window_title

        self._task_queue: deque[Callable[..., None]] = deque()
        self._subscribed_events: dict[int, tuple[EventType, Callable[..., None]]] = {}
        self._is_running = False

        self._logger = logger if logger is not None else MagicMock()

        self._clock = pygame.time.Clock()

    def get_window_size(self) -> ElementSize:
        return ElementSize(self._width, self._height)

    def _add_task_to_queue(self, task: Callable[..., None]) -> None:
        self._task_queue.append(task)

    def on_init(self, callback: EventCallback) -> None:
        self._task_queue.append(callback)

    def _handle_events(self, event: pygame.event.Event) -> None:
        for event_id, (subscribed_event, callback) in self._subscribed_events.items():
            if (
                isinstance(subscribed_event, KeyPressEventType)
                and event.type == pygame.KEYDOWN
            ):
                if event.key == KEY_MAPPING[subscribed_event.key]:
                    callback()

            elif event.type == event_id:
                callback()

    def start(self) -> None:
        self._log("Starting GUI")

        pygame.init()
        pygame.font.init()

        self._init_window()

        pygame.display.set_caption(self._window_title)

        self._is_running = True
        while self._is_running:
            self._run_tasks_from_queue()

            for event in pygame.event.get():
                self._run_tasks_from_queue()

                if event.type == pygame.QUIT:
                    self.stop()

                self._handle_events(event)

            self._clock.tick()

        self._log("Stopping GUI")
        pygame.quit()

    def _log(self, message: str) -> None:
        self._logger.debug(f"{self.__class__.__name__}: {message}")

    def _init_window(self) -> None:
        if isinstance(self._display_mode, FullscreenDisplayMode):
            self._window = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN | pygame.NOFRAME
            )
        elif isinstance(self._display_mode, WindowedDisplayMode):
            self._width, self._height = (
                self._display_mode.width,
                self._display_mode.height,
            )
            self._window = pygame.display.set_mode((self._width, self._height))
        else:
            raise GuiError(f"Unknown display mode: {self._display_mode}")

        self._width, self._height = self._window.get_size()

    def _run_tasks_from_queue(self) -> None:
        while self._task_queue:
            self._task_queue.popleft()()

            pygame.display.update()

    def stop(self) -> None:
        self._is_running = False

    @staticmethod
    def submit_execution(func: T) -> T:
        @wraps(func)
        def wrapper(self: "PygameGui", *args: Any, **kwargs: Any) -> None:
            self._add_task_to_queue(partial(func, self, *args, **kwargs))

        return cast(T, wrapper)

    @submit_execution
    def draw_uniform_background(self, color: Color) -> None:
        self._window.fill(color.get_hex_l())

    @submit_execution
    def draw_rectangle(
        self, *, color: Color, top_left_point: Point, width: int, height: int
    ) -> None:
        rect = pygame.Rect(*top_left_point, width, height)
        if not rect.colliderect(pygame.Rect((0, 0, self._width, self._height))):
            raise DrawError("Rectangle must be inside the view!")
        pygame.draw.rect(self._window, color.get_hex_l(), rect)

    @submit_execution
    def draw_text(self, *, font_size: int, text: str, color: Color) -> None:
        font = pygame.font.SysFont(None, font_size)

        lines: list[str] = []
        current_line = []

        for word in text.split(" "):
            test_line = " ".join(current_line + [word])
            test_width = font.size(test_line)[0]

            if test_width <= 0.9 * self._width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        line_height = font.get_linesize()
        total_height = len(lines) * line_height

        y_pos = (self._height - total_height) // 2

        for line in lines:
            text_surface = font.render(line, True, color.get_hex_l())
            text_rect = text_surface.get_rect(
                center=(self._width // 2, y_pos + line_height // 2)
            )
            self._window.blit(text_surface, text_rect)
            y_pos += line_height

    @submit_execution
    def draw_image(self, image_path: Path) -> None:
        raise NotImplementedError

    @submit_execution
    def play_sound(self, sound_path: Path) -> None:
        raise NotImplementedError

    def _subscribe_to_event(
        self, *, event_id: int, event: EventType, callback: EventCallback
    ) -> None:
        self._log(f"Subscribing to event {event_id} with callback {callback}")

        self._subscribed_events[event_id] = (event, callback)

        if isinstance(event, TimeoutEventType):
            self._add_task_to_queue(
                lambda: pygame.time.set_timer(event_id, event.timeout_millis)
            )

    def subscribe_to_event_and_get_id(
        self, *, event: EventType, callback: EventCallback
    ) -> int:
        event_id = pygame.event.custom_type()

        self._add_task_to_queue(
            lambda: self._subscribe_to_event(
                event_id=event_id, event=event, callback=callback
            )
        )

        return event_id

    def _unsubscribe_from_event_by_id(self, event_id: int) -> None:
        self._log(f"Unsubscribing from event {event_id}")

        if event_id not in self._subscribed_events:
            raise GuiError(f"Event ID {event_id} is not subscribed.")

        del self._subscribed_events[event_id]

    def unsubscribe_from_event_by_id(self, event_id: int) -> None:
        self._add_task_to_queue(lambda: self._unsubscribe_from_event_by_id(event_id))
