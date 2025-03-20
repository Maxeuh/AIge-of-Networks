import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from model.ai import AI


class Strategy(ABC):
    def __init__(self, ai: "AI"):
        self.__ai = ai

    @abstractmethod
    def execute(self):
        pass

    def get_ai(self):
        return self.__ai
