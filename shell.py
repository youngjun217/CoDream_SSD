import random

from ssd import SSD, SSDOutput


class shell_ftn():
    def __init__(self):
        self.ssd = SSD()

    def read(self, idx: int):
        if idx < 0 or idx > 99:
            raise ValueError("ERROR")
        if type(idx) != int:
            raise ValueError("ERROR")
        result = self.ssd.read_ssd(idx)
        print(f'[Read] LBA {idx}: {result}')
        return result

    def write(self, num: int, value: int) -> None:
        my_ssd = SSD()
        my_ssd.write_ssd(num, int(value,16))
        my_ssdoutput = SSDOutput()
        if my_ssdoutput == "":
            print('[Write] Done')
        pass

    # help : 프로그램 사용법
    def help(self):
        # 제작자 명시 (팀장/팀원)
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
        if len(str(value)) > 8:
            raise ValueError("ERROR")
        for x in range(100):
            SSD().write_ssd(x, value)
        print("[Full Write] Done")

    def fullread(self):
        ssd_nand = open("ssd_nand.txt", "r")
        ssd_output = None

        print("[Full Read]")

        for idx in range(100):
            try:
                self.ssd.read_ssd(idx)
                ssd_output = open("ssd_output.txt", "r")
                output = ssd_output.readline()

                if output == "ERROR" or len(output.split()) < 2:
                    print(output)
                    continue

                print(f"LBA {output.split()[0]} : {output.split()[1]}")

            except Exception as e:
                raise e
            finally:
                ssd_output.close()

        ssd_nand.close()

    def FullWriteAndReadCompare(self):
        for start_idx in range(0, 100, 5):
            rand_num = random.randint(0x00000000, 0xFFFFFFFF)
            rand_num_list = [rand_num] * 5
            for x in range(5):
                SSD().write_ssd(start_idx + x, rand_num_list[x])
                if SSD().read_ssd(start_idx + x) == rand_num_list[x]:
                    pass

    def PartialLBAWrite(self):
        partialLBA_index_list = [4, 0, 3, 1, 2]
        for _ in range(30):
            for write_index in range(5):
                random_write_value = random.randint(0, 0xFFFFFFFF)
                self.write(partialLBA_index_list[write_index], random_write_value)

            check_read_value = self.read(0)
            if check_read_value != self.read(1):
                print("FAIL")
                return False
            if check_read_value != self.read(2):
                print("FAIL")
                return False
            if check_read_value != self.read(3):
                print("FAIL")
                return False
            if check_read_value != self.read(4):
                print("FAIL")
                return False
        print("PASS")
        return True

    def _read_line(self, filepath, line_number):
        with open(filepath, 'r', encoding='utf-8') as f:
            for current_line, line in enumerate(f, start=1):
                if current_line == line_number:
                    parts = line.strip().split()
                    return int(parts[1])
        return None

    def WriteReadAging(self, filepath):
        value = random.randint(0, 0xFFFFFFFF)
        ssd = SSD()
        for i in range(200):
            ssd.write_ssd(0, value)
            ssd.write_ssd(99, value)
            if self._read_line(filepath, 1) != self._read_line(filepath, 100):
                print('FAIL')
                return
        print('PASS')

    def testScript(self, test_intro):
        if test_intro == '1_':
            self.FullWriteAndReadCompare()
        elif test_intro == '2_':
            self.PartialLBAWrite()
        elif test_intro == '3_':
            self.WriteReadAging()

    def main_function(self, args):
        if args[0].lower() == "read" and len(args) == 2:
            self.read(int(args[1]))  # idx
        elif args[0].lower() == "write" and len(args) == 3:
            self.write(int(args[1]), args[2])  # idx, value
        elif args[0].lower() == "fullwrite" and len(args) == 2:
            self.fullwrite(args[1])  # value
        elif args[0].lower() == "fullread" and len(args) == 1:
            self.fullread()
        elif args[0][0:2] in ['1_', '2_', '3_'] and len(args) == 1:
            test_intro = args[0][0:2]
            self.testScript(test_intro)
        elif args[0].lower() =='help':
            self.help()
        else:
            raise ValueError("INVALID COMMAND")

    def main(self):
        while True:
            command = input("Shell>")
            args = command.split()
            if args == []: raise ValueError("INVALID COMMAND")
            if args[0].lower() == "exit":
                # print("Exiting the program...")
                break
            self.main_function(args)


if __name__ == "__main__":
    shell_ftn().main()
