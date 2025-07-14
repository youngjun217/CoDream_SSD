class SSD():
    ...
    # 초기 ssd_nand.txt 파일 생성

    # read함수

    # write 함수
    def write(self, lba, value):
        if type(lba) is not int:
            raise ValueError("ERROR")
        if lba < 0:
            raise ValueError("ERROR")
        if lba >= 100:
            raise ValueError("ERROR")

        # ssd_nand.txt 파일 읽기
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.readlines()

        newline = f"{lba:02X} 0x{value:08X}\n"
        ssd_nand_txt[lba] = newline

        # 파일 다시 쓰기
        with open("ssd_nand.txt", "w") as file:
            file.writelines(ssd_nand_txt)

        # sse_output.txt 파일 초기화
        with open("ssd_output.txt", 'w', encoding='utf-8') as file:
            file.write("")