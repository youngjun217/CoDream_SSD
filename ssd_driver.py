from abc import ABC, abstractmethod


class SSDDriver(ABC):
    @abstractmethod
    def run(self, args):
        ...

    @abstractmethod
    def get_response(self):
        ...


