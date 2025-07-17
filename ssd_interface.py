from abc import ABC, abstractmethod
from ssd import SSD
from ssd_texts import SSDOutput, SSDText


class SSDInterface(ABC):
    @abstractmethod
    def run(self, args):
        ...

    @abstractmethod
    def get_response(self):
        ...


class SSDConcreteInterface(SSDInterface):
    def run(self, args):
        ssd = SSD()
        ssd.run(args)

    def get_response(self):
        ssd_output_txt: SSDText = SSDOutput()
        return ssd_output_txt.read()
