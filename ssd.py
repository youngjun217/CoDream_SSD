import sys
from abc import ABC, abstractmethod
from buffer import Buffer


class SSD():
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()
        self.buffer = Buffer()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def run(self, sys_argv):
        cmd = sys_argv[1]
        if not self._check_command_validity(cmd, len(sys_argv)):
            self._raise_error()

        lba = int(sys_argv[2])
        if (cmd == 'W'):
            value = int(sys_argv[3], 16)
            self.write_ssd(lba, value)
        elif (cmd == 'R'):
            buffer_lst = self.buffer.buf_lst

            for buffer_cmd in buffer_lst:
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1]=='W' and cmd_lst[2]==lba:
                    return cmd_lst[3]
                if cmd_lst[1]=='E' and int(cmd_lst[2])<=lba<int(cmd_lst[2])+int(cmd_lst[3]):
                    return 0x00000000
            self.read_ssd(lba)

        elif (cmd == 'E'):
            size = int(sys_argv[3])
            self.erase_ssd(lba, size)

    def read_ssd(self, lba):
        if not self._check_input_validity(lba):
            self._raise_error()

        lines = self._nand_txt.read()
        target_line = lines[lba]

        self._output_txt.write(target_line)

    # write 함수
    def write_ssd(self, lba, value):
        if not self._check_input_validity(lba, value):
            self._raise_error()

        # ssd_nand.txt 파일 읽기
        ssd_nand_txt = self._nand_txt.read()

        newline = f"{lba:02d} 0x{value:08X}\n"
        ssd_nand_txt[lba] = newline

        # 파일 다시 쓰기
        self._nand_txt.write(ssd_nand_txt)

        # sse_output.txt 파일 초기화
        self._output_txt.write("")


    # erase 함수
    def erase_ssd(self, lba, size):
        if not self._check_input_validity(lba, size=size):
            self._raise_error()

        end_index = lba + size
        if end_index > 100:
            end_index = 100

        ssd_nand_txt = self._nand_txt.read()
        for i in range(lba, end_index):
            ssd_nand_txt[i] = f"{i:02d} 0x00000000\n"
        self._nand_txt.write(ssd_nand_txt)


    def _raise_error(self):
        self._output_txt.write("ERROR")
        raise ValueError("ERROR")

    def _check_command_validity(self, cmd, len_sys_argv):
        return ((cmd == 'W') and (len_sys_argv == 4)) or ((cmd == 'R') and (len_sys_argv == 3)) or (
                    (cmd == 'E') and (len_sys_argv == 4))

    def _check_input_validity(self, lba, value=0x00000000, size=10):
        if type(lba) is not int:
            return False
        if type(value) is not int:
            return False
        if not 0 <= lba < 100:
            return False
        if not 0 <= value <= 0xFFFFFFFF:
            return False
        if not 1 <= size <= 10:
            return False
        return True


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
