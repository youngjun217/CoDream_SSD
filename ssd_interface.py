from abc import ABC, abstractmethod


class SSDInterface(ABC):
    @abstractmethod
    def run(self, args):
        ...

    @abstractmethod
    def get_response(self):
        ...


