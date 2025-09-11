from abc import ABC, abstractmethod

from ..gui import Gui


class Screen(ABC):
    def __init__(self, *, gui: Gui) -> None:
        self._gui = gui

    @abstractmethod
    def show(self) -> None:
        """
        Displays the screen using the provided GUI.
        """

        pass
