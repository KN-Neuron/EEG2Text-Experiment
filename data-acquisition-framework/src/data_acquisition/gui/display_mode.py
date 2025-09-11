from dataclasses import dataclass


@dataclass
class DisplayMode:
    pass


@dataclass
class FullscreenDisplayMode(DisplayMode):
    pass


@dataclass
class WindowedDisplayMode(DisplayMode):
    width: int
    height: int
