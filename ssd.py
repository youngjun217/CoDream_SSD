class SSD():
    def __init__(self):
        self._output_txt = SSDOutput()

    @property
    def output_txt(self):
        return self._output_txt

    def read_ssd(self, index):
        if not self.check_input_validity(index):
            with open("ssd_output.txt", "w") as file:
                file.write("ERROR")
            raise ValueError("ERROR")

        ssd_nand_txt = ""
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.read()
        lines = ssd_nand_txt.splitlines()
        target_line = lines[index]

        self._output_txt.write(target_line)

    # write 함수
    def write_ssd(self, lba, value):
        if not self.check_input_validity(lba, value):
            self._output_txt.write("ERROR")
            raise ValueError("ERROR")

        # ssd_nand.txt 파일 읽기
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.readlines()

        newline = f"{lba:02d} 0x{value:08X}\n"
        ssd_nand_txt[lba] = newline

        # 파일 다시 쓰기
        with open("ssd_nand.txt", "w") as file:
            file.writelines(ssd_nand_txt)

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


class SSDOutput:
    def __init__(self):
        self.write("")

    def read(self):
        with open("ssd_output.txt", 'r', encoding='utf-8') as file:
            return file.read()

    def write(self, output):
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write(output)
