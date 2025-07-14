class SSD():
    def read(self, lba):
        index = lba
        ssd_nand_txt = ""
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.read()
        lines = ssd_nand_txt.splitlines()
        target_line = lines[lba]

        with open("ssd_output.txt", "w") as file:
            file.write(target_line)


