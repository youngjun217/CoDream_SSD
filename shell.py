import sys
from ssd import SSD, SSDOutput, SSDNand
import random


class shell_ftn():
    def __init__(self):
        self.ssd = SSD()
        self.ssd_output = SSDOutput()
        self.ssd_nand = SSDNand()


    def read(self, idx: int):
        self.ssd.read_ssd(idx)
        result = self.ssd_output.read()
        print(f'[Read] LBA {idx}: {result}')
        return

    def write(self, num: int, value: int) -> None:
        if self.ssd.write_ssd(num, value):
            print('[Write] Done')
        pass

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
        for i in range(30):
            r1 = random.randint(0, 0xFFFFFFFF)
            self.write(4, r1)
            self.write(0, r1)
            self.write(3, r1)
            self.write(1, r1)
            self.write(2, r1)

            if r1 != self.ssd_output.read(1):
                print("FAIL")
                return False
            if r1 != self.read(2):
                print("FAIL")
                return False
            if r1 != self.read(3):
                print("FAIL")
                return False
            if r1 != self.read(4):
                print("FAIL")
                return False
        print("PASS")
        return True

    def _read_line(self, line_number):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as f:
            for current_line, line in enumerate(f, start=1):
                if current_line == line_number:
                    parts = line.strip().split()
                    return int(parts[1])
        return None

    def WriteReadAging(self):
        value = random.randint(0, 0xFFFFFFFF)
        for i in range(200):
            self.ssd.write_ssd(0, value)
            self.ssd.write_ssd(99, value)
            if self._read_line(filepath, 1) != self._read_line(filepath, 100):

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
