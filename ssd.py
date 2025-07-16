import sys
from abc import ABC, abstractmethod
from buffer import Buffer
import os

class SSD():
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()
        self._command: SSDCommand = ErrorCommand()
        self.buffer = Buffer()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def _check_buffer(self, cmd, lba, sys_argv):
        buffer_lst = self.buffer.buf_lst
        if (cmd == 'R'):
            for buffer_cmd in buffer_lst:
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1] == 'W' and int(cmd_lst[2]) == lba:
                    self._output_txt.write(f"{lba:02d} {cmd_lst[3]}\n")
                    return True
                if cmd_lst[1] == 'E':
                    start_lba = int(cmd_lst[2])
                    size = int(cmd_lst[3])
                    if start_lba <= lba < start_lba + size:
                        self._output_txt.write(f"{lba:02d} 0x00000000\n")
                        return True
            return False

        elif cmd == 'W':
            combine_idx = -1
            for idx, buffer_cmd in enumerate(buffer_lst):
                if 'empty' in buffer_cmd:
                    break
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1] == 'W' and int(cmd_lst[2]) == lba:
                    combine_idx = idx
                if cmd_lst[1] == 'E' and int(cmd_lst[2]) == lba and int(cmd_lst[3]) == 1:
                    combine_idx = idx

            if combine_idx >= 0:
                value = int(sys_argv[3], 16)
                old_name = f"./buffer/{buffer_lst[combine_idx]}"
                new_name = f"./buffer/{combine_idx}_{cmd}_{lba}_{value}"
                os.rename(old_name, new_name)

        elif (cmd == 'E'):
            size = int(sys_argv[3])
            self.erase_ssd(lba, size)
            # 기능 추가 필요


    def run(self, sys_argv):
        cmd = sys_argv[1]
        lba = int(sys_argv[2])
        if self._check_buffer(cmd, lba, sys_argv):
            return

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

    def _read_ssd(self, lba):
        self._command = self.get_command('R')
        self._command.run_command([lba])

    def _write_ssd(self, lba, value):
        self._command = self.get_command('W')
        self._command.run_command([lba, hex(value).upper])

    def _erase_ssd(self, lba, size):
        self._command = self.get_command('E')
        self._command.run_command([lba, size])

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
    def check_input_validity(self, args: list): pass

    @abstractmethod
    def args_parser(self, args: list): pass

    @abstractmethod
    def execute(self): pass

class ErrorCommand(SSDCommand):
    def __init__(self):
        super().__init__()

    def check_input_validity(self, args: list):
        return False

    def args_parser(self, args: list): pass
    def execute(self): pass

class ReadCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0

    def check_input_validity(self, args: list):
        if len(args) != 1:
            return False

        self.args_parser(args)
        if not 0 <= self._lba < 100:
            return False
        return True

    def args_parser(self, args: list):
        try:
            self._lba = int(args[0])
        except ValueError:
            self._raise_error()

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
        if not 0 <= self._lba < 100:
            return False
        if not 0 <= self._value <= 0xFFFFFFFF:
            return False
        return True

    def args_parser(self, args: list):
        try:
            self._lba = int(args[0])
            self._value = int(args[1], 16)
        except ValueError:
            self._raise_error()

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
        if not 0 <= self._lba < 100:
            return False
        if not 1 <= self._size <= 10:
            return False
        return True

    def args_parser(self, args: list):
        try:
            self._lba = int(args[0])
            self._size = int(args[1])
        except ValueError:
            self._raise_error()

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
    def read(self): pass

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


if __name__ == "__main__":
    # sys.argv[0] = 'ssd.py'
    # sys.argv[1] = 'W'
    # sys.argv[2] = '3'

    ssd = SSD()
    ssd.run(sys.argv)
