import sys
from ssd import SSD, SSDOutput, SSDNand
import random
import datetime
import os
import time
import glob

class Logger:
    _instance = None
    LOG_FILE = 'latest.log'
    MAX_SIZE = 10 * 1024  # 10KB
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        if os.path.exists(self.LOG_FILE):
            os.remove(self.LOG_FILE)

    def print(self, header, message):
        self.rotate_log_if_needed()
        with open("latest.log", 'a', encoding='utf-8') as file:
            now = datetime.datetime.now()
            log = f"[{now.strftime('%y.%m.%d %H:%M')}] {header}\t: {message}\n"
            log = log.expandtabs(tabsize=48)
            file.write(log)
    def rotate_log_if_needed(self):
        if os.path.exists(self.LOG_FILE) and os.path.getsize(self.LOG_FILE) > self.MAX_SIZE:
            for existing in glob.glob("until_*.log"):
                os.rename(existing, existing.replace(".log", ".zip"))

            timestamp = time.strftime("until_%y%m%d_%Hh_%Mm_%Ss")
            new_name = f"{timestamp}.log"
            os.rename(self.LOG_FILE, new_name)


class shell_ftn():
    def __init__(self):
        self.ssd = SSD()
        self.ssd_output = SSDOutput()
        self.ssd_nand = SSDNand()
        self.logger = Logger()

    def read(self, idx: int) -> None:
        self.ssd.read_ssd(idx)
        result = self.ssd_output.read()
        value = result.split()[1]
        print(f'[Read] LBA {idx}: {value}')
        self.logger.print(f"{self.read.__qualname__}()", f"LBA {idx}: {value}")


    def write(self, num: int, value: str) -> bool:
        self.ssd.write_ssd(num, value)
        if self.ssd_output.read() == '':
            print('[Write] Done')
            self.logger.print(f"{self.read.__qualname__}()", "DONE")
            return True
        self.logger.print(f"{self.read.__qualname__}()", "FAIL")
        return False

    def erase(self, lba: int, size: int):
        if (0 > lba or lba > 99) or (1 > size or size > 100) or (lba + size > 99):
            self.logger.print(f"{self.read.__qualname__}()", "FAIL")
            raise Exception()

        offset = 0
        while size > 0:
            erase_size = min(size, 10)
            SSD.erase_ssd(lba + offset, erase_size)
            offset += 10
            size -= erase_size
        self.logger.print(f"{self.read.__qualname__}()", "DONE")

    def erase_range(self, st_lba: int, en_lba: int):
        if st_lba > en_lba or st_lba < 0 or en_lba > 99:
            raise ValueError("Invalid LBA range")

        size = en_lba - st_lba + 1  # inclusive range
        self.erase(st_lba, size)

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
        self.logger.print(f"{self.read.__qualname__}()", "DONE")

    def fullwrite(self, value):
        for x in range(100):
            self.ssd.write_ssd(x, value)
        print("[Full Write] Done")
        self.logger.print(f"{self.read.__qualname__}()", "DONE")

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
                self.logger.print(f"{self.read.__qualname__}()", "FAIL")
                raise e

        self.logger.print(f"{self.read.__qualname__}()", "DONE")

    def FullWriteAndReadCompare(self):
        for start_idx in range(0, 100, 5):
            for x in range(5):
                rand_num = random.randint(0, 0xFFFFFFFF)
                hex_str = f"0x{rand_num:08X}"
                self.ssd.write_ssd(start_idx + x, rand_num)
                if self.ssd_nand.readline(start_idx + x).split()[1] != hex_str:
                    print('FAIL')
                    self.logger.print(f"{self.read.__qualname__}()", "FAIL")
                    return
        print('PASS')
        self.logger.print(f"{self.read.__qualname__}()", "PASS")

    def PartialLBAWrite(self):
        partialLBA_index_list = [4, 0, 3, 1, 2]
        for _ in range(30):
            random_write_value = random.randint(0, 0xFFFFFFFF)
            for x in range(5):
                self.ssd.write_ssd(partialLBA_index_list[x], random_write_value)
            check_ref = self.ssd_nand.readline(0).split()[1]
            for x in range(1, 5):
                if check_ref != self.ssd_nand.readline(x).split()[1]:
                    print('FAIL')
                    self.logger.print(f"{self.read.__qualname__}()", "FAIL")
                    return
        print("PASS")
        self.logger.print(f"{self.read.__qualname__}()", "PASS")

    def WriteReadAging(self):
        value = random.randint(0, 0xFFFFFFFF)
        for i in range(200):
            self.ssd.write_ssd(0, value)
            self.ssd.write_ssd(99, value)
            if self.ssd_nand.readline(0).split()[1] != self.ssd_nand.readline(99).split()[1]:
                print('FAIL')
                self.logger.print(f"{self.read.__qualname__}()", "FAIL")
                return
        print('PASS')
        self.logger.print(f"{self.read.__qualname__}()", "PASS")

    def main_function(self, args):
        if not (args[0].lower(), len(args)) in self.command_dictionary(args):
            raise ValueError("INVALID COMMAND")
        self.command_dictionary(args)[(args[0].lower(), len(args))]()

    def command_dictionary(self, args):
        command_dict = {
            ("read", 2): lambda: self.read(int(args[1])),
            ("write", 3): lambda: self.write(int(args[1]), int(args[2], 16)),
            ("fullwrite", 2): lambda: self.fullwrite(int(args[1], 16)),
            ("fullread", 1): lambda: self.fullread(),
            ('1_', 1): lambda: self.FullWriteAndReadCompare(),
            ('2_', 1): lambda: self.PartialLBAWrite(),
            ('3_', 1): lambda: self.WriteReadAging(),
            ('help', 1): lambda: self.help(),
            ('erase', 2): lambda: self.erase(int(args[1]), int(args[2])),
            ('erase_range', 2): lambda: self.erase(int(args[1]), int(args[2]))
        }
        return command_dict

    def main(self):
        while True:
            command = input("Shell>")
            if command.split()[0].lower() == "exit": break
            self.main_function(command.split())


if __name__ == "__main__":
    shell_ftn().main()
