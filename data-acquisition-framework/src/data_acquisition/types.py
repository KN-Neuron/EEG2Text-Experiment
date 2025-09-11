from typing import Callable, NamedTuple, TypeAlias, TypeVar

T = TypeVar("T")

EventCallback: TypeAlias = Callable[[], None]
ResultEventCallback: TypeAlias = Callable[[T], None]

Point = NamedTuple("Point", [("x", int), ("y", int)])
ElementSize = NamedTuple("ElementSize", [("width", int), ("height", int)])
