from abc import ABC, abstractmethod

from ssd_texts import SSDNand, SSDOutput


class SSDCommand(ABC):
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()

    def run_command(self, args: list):
        self.args_parser(args)
        self.execute()

    def _raise_error(self):
        self._output_txt.write("ERROR")
        raise ValueError("ERROR")

    def check_input_validity(self, args: list):
        if not self._check_input_validity(args):
            self._raise_error()

    @abstractmethod
    def _check_input_validity(self, args: list):
        pass

    @abstractmethod
    def args_parser(self, args: list):
        pass

    @abstractmethod
    def execute(self):
        pass


class SSDErrorCommand(SSDCommand):
    def __init__(self):
        super().__init__()

    def _check_input_validity(self, args: list):
        return False

    def args_parser(self, args: list): pass

    def execute(self): pass


class SSDReadCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0

    def _check_input_validity(self, args: list):
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


class SSDWriteCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0
        self._value = 0

    def _check_input_validity(self, args: list):
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


class SSDEraseCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0
        self._size = 0

    def _check_input_validity(self, args: list):
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


class SSDFlushCommand(SSDCommand):
    def __init__(self):
        super().__init__()
        self._lba = 0
        self._size = 0

    def _check_input_validity(self, args: list):
        if args:
            return False
        return True

    def args_parser(self, args: list): pass

    def execute(self): pass