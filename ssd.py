import pdb
import sys
from abc import ABC, abstractmethod
from multiprocessing.spawn import get_command_line


class SSD():
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()
        self._command: SSDCommand = ErrorCommand()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def run(self, sys_argv):
        cmd = sys_argv[1]
        self._command = self.get_command(cmd)
        self._command.run_command(sys_argv[2:])

    def get_command(self, cmd):
        if (cmd == 'W'):
            return WriteCommand()
        elif (cmd == 'R'):
            return ReadCommand()
        elif (cmd == 'E'):
            return EraseCommand()
        else:
            return ErrorCommand()


class SSDCommand(ABC):
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()

    def run_command(self, args: list):
        if not self.check_input_validity(args):
            self._raise_error()
        self.execute()

    def _raise_error(self):
        self._output_txt.write("ERROR")
        raise ValueError("ERROR")

    @abstractmethod
    def check_input_validity(self, args: list):
        pass

    @abstractmethod
    def args_parser(self, args: list):
        pass

    @abstractmethod
    def execute(self):
        pass

class ErrorCommand(SSDCommand):
    def __init__(self):
        super().__init__()

    def check_input_validity(self, args: list): pass
    def args_parser(self, args: list): pass
    def execute(self):
        self._raise_error()

class ReadCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0

    def check_input_validity(self, args: list):
        if len(args) != 1:
            return False

        self.args_parser(args)
        if type(self._lba) is not int:
            return False
        if not 0 <= self._lba < 100:
            return False
        return True

    def args_parser(self, args: list):
        self._lba = int(args[0])

    def execute(self):
        lines = self._nand_txt.read()
        target_line = lines[self._lba]
        self._output_txt.write(target_line)


class WriteCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0
        self._value = 0

    def check_input_validity(self, args: list):
        # pdb.set_trace()
        if len(args) != 2:
            return False

        self.args_parser(args)
        if type(self._lba) is not int:
            return False
        if type(self._value) is not int:
            return False
        if not 0 <= self._lba < 100:
            return False
        if not 0 <= self._value <= 0xFFFFFFFF:
            return False
        return True

    def args_parser(self, args: list):
        self._lba = int(args[0])
        self._value = int(args[1], 16)

    def execute(self):
        # ssd_nand.txt 파일 읽기
        ssd_nand_txt = self._nand_txt.read()

        newline = f"{self._lba:02d} 0x{self._value:08X}\n"
        ssd_nand_txt[self._lba] = newline

        # 파일 다시 쓰기
        self._nand_txt.write(ssd_nand_txt)

        # sse_output.txt 파일 초기화
        self._output_txt.write("")


class EraseCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0
        self._size = 0

    def check_input_validity(self, args: list):
        if len(args) != 2:
            return False

        self.args_parser(args)
        if type(self._lba) is not int:
            return False
        if type(self._size) is not int:
            return False
        if not 0 <= self._lba < 100:
            return False
        if not 1 <= self._size <= 10:
            return False
        return True

    def args_parser(self, args: list):
        self._lba = int(args[0])
        self._size = int(args[1])

    def execute(self):
        end_index = self._lba + self._size
        if end_index > 100:
            end_index = 100

        ssd_nand_txt = self._nand_txt.read()
        for i in range(self._lba, end_index):
            ssd_nand_txt[i] = f"{i:02d} 0x00000000\n"
        self._nand_txt.write(ssd_nand_txt)


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
    def read(self):
        pass

    @abstractmethod
    def write(self, output):
        pass


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


if __name__ == "__main__":
    # sys.argv[0] = 'ssd.py'
    # sys.argv[1] = 'W'
    # sys.argv[2] = '3'

    ssd = SSD()
    ssd.run(sys.argv)
