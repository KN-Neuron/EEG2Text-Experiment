from dataclasses import dataclass

from .event_type import EventType


@dataclass(frozen=True)
class TimeoutEventType(EventType):
    timeout_millis: int
