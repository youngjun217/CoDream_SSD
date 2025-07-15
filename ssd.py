import sys
from abc import ABC, abstractmethod

class SSD():
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def run(self, sys_argv):
        cmd = sys_argv[1]
        lba = int(sys_argv[2])
        if (cmd == 'W'):
            if len(sys_argv) != 4:
                print("Usage: python ssd.py <command> <lba> <value>")
                sys.exit(1)
            value = int(sys_argv[3], 16)
            print(f"command({cmd!r}, {lba}, {hex(value):010})")
            self.write_ssd(lba, value)
        elif (cmd == 'R'):
            if len(sys_argv) != 3:
                print("Usage: python ssd.py <command> <lba>")
                sys.exit(1)
            print(f"command({cmd!r}, {lba})")
            self.read_ssd(lba)
        else:
            print("Usage: python ssd.py <command == W or R> <lba> <value: if command == W>")
            sys.exit(1)
        # 실제 동작 코드 작성

    def read_ssd(self, lba):
        if not self.check_input_validity(lba):
            self._output_txt.write("ERROR")
            raise ValueError("ERROR")

        lines = self._nand_txt.read()
        target_line = lines[lba]

        self._output_txt.write(target_line)

    # write 함수
    def write_ssd(self, lba, value):
        if not self.check_input_validity(lba, value):
            self._output_txt.write("ERROR")
            raise ValueError("ERROR")

        # ssd_nand.txt 파일 읽기
        ssd_nand_txt = self._nand_txt.read()

        newline = f"{lba:02d} 0x{value:08X}\n"
        ssd_nand_txt[lba] = newline

        # 파일 다시 쓰기
        self._nand_txt.write(ssd_nand_txt)

        # sse_output.txt 파일 초기화
        self._output_txt.write("")

    def check_input_validity(self, lba, value = 0x00000000):
        if type(lba) is not int:
            return False
        if type(value) is not int:
            return False
        if not 0 <= lba < 100:
            return False
        if not 0 <= value <= 0xFFFFFFFF:
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