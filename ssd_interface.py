from abc import ABC, abstractmethod

from buffer import Buffer
from ssd import SSDOutput


class SSDInterface(ABC):
    @abstractmethod
    def run(self, args):
        ...

    @abstractmethod
    def get_response(self):
        ...


class SSDConcreteInterface(SSDInterface):
    def run(self, args):
        buffer = Buffer()
        buffer.run(args)

    def get_response(self):
        ssd_output_txt = SSDOutput()
        return ssd_output_txt.read()
