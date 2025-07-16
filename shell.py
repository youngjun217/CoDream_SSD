import contextlib
import io
import os
import sys
from time import sleep

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


class Shell():
    def __init__(self):
        self.ssd = SSD()
        self.ssd_output = SSDOutput()
        self.ssd_nand = SSDNand()
        self.logger = Logger()

    def _send_command(self, command, lba, value = None):
        if (command == 'W'):
            if type(value) is int:
                value = hex(value).upper()
            return self.ssd.run([None, 'W', lba, value])
        if (command == 'R'):
            return self.ssd.run([None, 'R', lba])
        if (command == 'E'):
            return self.ssd.run([None, 'E', lba, value])

    def read(self, idx: int) -> None:
        self._send_command('R', idx)
        result = self.ssd_output.read()
        value = result.split()[1]
        print(f'[Read] LBA {idx}: {value}')
        self.logger.print(f"{self.read.__qualname__}()", f"LBA {idx}: {value}")

    def write(self, num: int, value: str) -> bool:
        self._send_command('W', num, value)
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
            self._send_command('E', lba + offset, erase_size)
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
            self._send_command('W', x, value)
        print("[Full Write] Done")
        self.logger.print(f"{self.read.__qualname__}()", "DONE")

    def fullread(self):
        print("[Full Read]")

        for idx in range(100):
            try:
                self._send_command('R', idx)
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
                self._send_command('W', start_idx + x, rand_num)
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
                self._send_command('W', partialLBA_index_list[x], random_write_value)
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
            self._send_command('W', 0, value)
            self._send_command('W', 99, value)
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

    def option_dict(self):
        option_dict = {
            ('1_'): 5,
            ('2_'): 13,
            ('3_'): 15,
            ('4_'): 11
        }
        return option_dict

    def option_main(self,path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                command_lines = file.readlines()
            for command in command_lines:
                print(command[0:-1]+' '*self.option_dict()[command[0:2]]+ '___   Run...', end=' ',flush=True)
                output_capture = io.StringIO()
                with contextlib.redirect_stdout(output_capture):
                    self.command_dictionary(command[0:2])[(command[0:2], 1)]()
                print(output_capture.getvalue().strip())
                if(output_capture.getvalue().strip())=='FAIL':return
        else:print("ERROR")


if __name__ == "__main__":
    if len(sys.argv)==1:
        Shell().main()
    elif len(sys.argv)==2:
        Shell().option_main(sys.argv[1])


