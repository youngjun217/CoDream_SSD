class SSD():
    def read_ssd(self, index):
        if type(index) is not int:
            raise ValueError("ERROR")
        if not 0 <= index < 100:
            raise ValueError("ERROR")

        ssd_nand_txt = ""
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.read()
        lines = ssd_nand_txt.splitlines()
        target_line = lines[index]

        with open("ssd_output.txt", "w") as file:
            file.write(target_line)

    # write 함수
    def write_ssd(self, lba, value):
        if not self.check_input_validity(lba, value):
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
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write("")

    def check_input_validity(self, lba, value):
        if type(lba) is not int:
            return False
        if type(value) is not int:
            return False
        if not 0 <= lba < 100:
            return False
        if not 0 <= value <= 0xFFFFFFFF:
            return False
        return True
