class SSD():
    def read(self, index):
        ssd_nand_txt = ""
        with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
            ssd_nand_txt = file.read()
        lines = ssd_nand_txt.splitlines()
        target_line = lines[index]
        
        with open("ssd_output.txt", "w") as file:
            file.write(target_line)


    def read_ssd(self,idx):
        pass

    def write_ssd(self,idx, value):
        pass
