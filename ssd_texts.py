from abc import ABC, abstractmethod

MAX_NAND_SIZE = 100


class SSDText(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @abstractmethod
    def read(self):  pass

    @abstractmethod
    def write(self, output): pass


class SSDNand(SSDText):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            ssd_nand_txt = []
            for i in range(0, MAX_NAND_SIZE):
                newline = f"{i:02d} 0x0000000O\n"
                ssd_nand_txt.append(newline)
            self.write(ssd_nand_txt)

    def read(self):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            lines = file.readlines()
            fixed_size_lines = lines + ["\n"] * (MAX_NAND_SIZE - len(lines))
            fixed_size_lines = fixed_size_lines[:MAX_NAND_SIZE]
            return fixed_size_lines

    def write(self, output):
        with open("ssd_nand.txt", 'w', encoding='utf-8') as file:
            file.writelines(output)


class SSDOutput(SSDText):
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.write("")

    def read(self):
        with open("ssd_output.txt", 'r', encoding='utf-8') as file:
            return file.read().rstrip('/n')

    def write(self, output):
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write(output)
