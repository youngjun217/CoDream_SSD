import sys
from ssd import SSD, SSDOutput, SSDNand
import random


class shell_ftn():
    def __init__(self):
        self.ssd = SSD()
        self.ssd_output = SSDOutput()
        self.ssd_nand = SSDNand()


    def read(self, idx: int) -> None:
        self.ssd.read_ssd(idx)
        result = self.ssd_output.read()
        value = result.split()[1]
        print(f'[Read] LBA {idx}: {value}')



    def write(self, num: int, value: str) -> None:
        self.ssd.write_ssd(num, value)
        if self.ssd_output.read() == '':
            print('[Write] Done')
            return True
        return False

    # help : 프로그램 사용법
    def help(self):
        print('[Help]\n',
              'CoDream Team : our dreaming code\n',
              '팀장 : 조영준\n',
              '팀원 : 민동학, 박승욱, 이재원, 최일묵, 한재원 \n\n',
              'How to Use???============================================\n',
              'Rule 1. Index in 0~99\n',
              'Rule 2. Value in 0x00000000~0xFFFFFFFF\n\n',
              'read Index : read memory[Index] value                        ex)[Read] LBA 00 : 0x00000000\n',
              'write Index Value : write value in memory[Index]             ex)[Write] Done\n',
              'exit : exit program\n',
              'fullwrite Value : write value all memory Index               ex)[Full Write] Done\n',
              'fullread : read all memory Index value                       ex)[Full Read] ...\n',
              '1_FullWriteAndReadCompare : compare write and read on every 5 Index \n',
              '2_PartialLBAWrite : Write a random value at the 0~4 index and check if the values are the same 30 times.\n',
              '3_WriteReadAging : Write a random value at index 0.99 and check if the values are the same 200 times.\n',
              )

    def fullwrite(self, value):
        for x in range(100):
            self.ssd.write_ssd(x, value)
        print("[Full Write] Done")

    def fullread(self):
        print("[Full Read]")

        for idx in range(100):
            try:
                self.ssd.read_ssd(idx)
                output = self.ssd_output.read()

                if output == "ERROR" or len(output.split()) < 2:
                    print(output)
                    continue

                print(f"LBA {output.split()[0]} : {output.split()[1]}")

            except Exception as e:
                raise e

    def FullWriteAndReadCompare(self):
        for start_idx in range(0, 100, 5):
            for x in range(5):
                rand_num = random.randint(0, 0xFFFFFFFF)
                hex_str = f"0x{rand_num:08X}"
                self.ssd.write_ssd(start_idx + x, rand_num)
                if self.ssd_nand.readline(start_idx + x).split()[1] != hex_str:
                    print('FAIL')
                    return
        print('PASS')

    def PartialLBAWrite(self):
        partialLBA_index_list = [4, 0, 3, 1, 2]
        for _ in range(30):
            random_write_value = random.randint(0, 0xFFFFFFFF)
            for x in range(5):
                self.ssd.write_ssd(partialLBA_index_list[x], random_write_value)
            check_ref = self.ssd_nand.readline(0).split()[1]
            for x in range(1,5):
                if check_ref != self.ssd_nand.readline(x).split()[1]:
                    print('FAIL')
                    return
        print("PASS")


    def WriteReadAging(self):
        value = random.randint(0, 0xFFFFFFFF)
        for i in range(200):
            self.ssd.write_ssd(0, value)
            self.ssd.write_ssd(99, value)
            if self.ssd_nand.readline(0).split()[1] != self.ssd_nand.readline(99).split()[1]:
                print('FAIL')
                return
        print('PASS')

    def main_function(self, args):
        if not (args[0].lower(), len(args)) in self.command_dictionary(args):
            raise ValueError("INVALID COMMAND")
        self.command_dictionary(args)[(args[0].lower(), len(args))]()

    def command_dictionary(self,args):
        command_dict = {
            ("read", 2): lambda: self.read(int(args[1])),
            ("write", 3): lambda: self.write(int(args[1]), int(args[2], 16)),
            ("fullwrite", 2): lambda: self.fullwrite(int(args[1], 16)),
            ("fullread", 1): lambda: self.fullread(),
            ('1_', 1): lambda: self.FullWriteAndReadCompare(),
            ('2_', 1): lambda: self.PartialLBAWrite(),
            ('3_', 1): lambda: self.WriteReadAging(),
            ('help', 1): lambda: self.help()
        }
        return command_dict

    def main(self):
        while True:
            command = input("Shell>")
            if command.split()[0].lower() == "exit": break
            self.main_function(command.split())


if __name__ == "__main__":
    shell_ftn().main()
