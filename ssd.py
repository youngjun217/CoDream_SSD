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

    def read_ssd(self, index):
        if not self.check_input_validity(index):
            self._output_txt.write("ERROR")
            raise ValueError("ERROR")

        lines = self._nand_txt.read()
        target_line = lines[index]

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


class SSDNand:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            ssd_nand_txt = []
            for i in range(0, 100):
                newline = f"{i:02d} 0x00000000\n"
                ssd_nand_txt.append(newline)

            self.write(ssd_nand_txt)
            self.initialized = True

    def read(self):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            return file.readlines()

    def readline(self, index):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            return file.readlines()[index]

    def write(self, output):
        with open("ssd_nand.txt", 'w', encoding='utf-8') as file:
            file.writelines(output)

class SSDOutput:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.write("")
            self.initialized = True

    def read(self):
        with open("ssd_output.txt", 'r', encoding='utf-8') as file:
            return file.read()

    def write(self, output):
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write(output)
