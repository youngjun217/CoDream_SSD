from abc import ABC, abstractmethod


class SSDText(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    @abstractmethod
    def read(self):  pass

    @abstractmethod
    def write(self, output): pass


class SSDNand(SSDText):
    def __init__(self):
        super().__init__()
        ssd_nand_txt = []
        for i in range(0, 100):
            newline = f"{i:02d} 0x00000000\n"
            ssd_nand_txt.append(newline)
        self.write(ssd_nand_txt)

    def read(self):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            return file.readlines()

    def readline(self, lba):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            return file.readlines()[lba]

    def write(self, output):
        with open("ssd_nand.txt", 'w', encoding='utf-8') as file:
            file.writelines(output)


class SSDOutput(SSDText):
    def __init__(self):
        super().__init__()
        self.write("")

    def read(self):
        with open("ssd_output.txt", 'r', encoding='utf-8') as file:
            return file.read()

    def write(self, output):
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write(output)
