import contextlib
import datetime
import glob
import io
import os
import random
import sys
import time
from abc import ABC, abstractmethod

from ssd import SSD, SSDOutput, SSDNand


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


class Command(ABC):
    def __init__(self, shell):
        self.shell = shell

    @abstractmethod
    def execute(self):
        pass


class ReadCommand(Command):
    def __init__(self, shell, idx):
        super().__init__(shell)
        self.idx = idx

    def execute(self) -> None:
        self.shell._send_command('R', self.idx)
        result = self.shell.ssd_output.read()
        value = result.split()[1]
        print(f'[Read] LBA {self.idx}: {value}')
        self.shell.logger.print(f"{self.execute.__qualname__}()", f"LBA {self.idx}: {value}")


class WriteCommand(Command):
    def __init__(self, shell, idx: int, value: int):
        super().__init__(shell)
        self.idx = idx
        self.value = value

    def execute(self) -> bool:
        self.shell._send_command('W', self.idx, self.value)
        if self.shell.ssd_output.read() == '':
            print('[Write] Done')
            self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")
            return True
        self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
        return False


class EraseCommand(Command):
    def __init__(self, shell, lba: int, size: int):
        super().__init__(shell)
        self.lba = lba
        self.size = size

    def execute(self):
        if (0 > self.lba or self.lba > 99) or (1 > self.size or self.size > 100) or (self.lba + self.size > 100):
            self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
            raise Exception()

        offset = 0
        while self.size > 0:
            erase_size = min(self.size, 10)
            self.shell._send_command('E', self.lba + offset, erase_size)
            offset += 10
            self.size -= erase_size
        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")


class EraseRangeCommand(Command):
    def __init__(self, shell, st_lba: int, en_lba: int):
        super().__init__(shell)
        self.st_lba = st_lba
        self.en_lba = en_lba

    def execute(self) -> None:
        if self.st_lba > self.en_lba or self.st_lba < 0 or self.en_lba > 99:
            raise ValueError("Invalid LBA range")

        size = self.en_lba - self.st_lba + 1  # inclusive range
        erase_cmd = EraseCommand(self.shell, self.st_lba, size)
        erase_cmd.execute()


class FullWriteCommand(Command):
    def __init__(self, shell, value):
        super().__init__(shell)
        self.value = value
    def execute(self):
        for x in range(100):
            self.shell._send_command('W', x, self.value)
        print("[Full Write] Done")
        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class FullReadCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)
    def execute(self):
        print("[Full Read]")
        for idx in range(100):
            try:
                self.shell._send_command('R', idx)
                output = self.shell.ssd_output.read()

                if output == "ERROR" or len(output.split()) < 2:
                    print(output)
                    continue

                print(f"LBA {output.split()[0]} : {output.split()[1]}")

            except Exception as e:
                self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                raise e

        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class FullWriteAndReadCompareCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        for start_idx in range(0, 100, 5):
            for x in range(5):
                rand_num = random.randint(0, 0xFFFFFFFF)
                hex_str = f"0x{rand_num:08X}"
                self.shell._send_command('W', start_idx + x, rand_num)
                if self.shell.ssd_nand.readline(start_idx + x).split()[1] != hex_str:
                    print('FAIL')
                    self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                    return
        print('PASS')
        self.shell.logger.print(f"{self.execute.__qualname__}()", "PASS")




class Shell():
    def __init__(self):
        self.ssd = SSD()
        self.ssd_output = SSDOutput()
        self.ssd_nand = SSDNand()
        self.logger = Logger()

    def _send_command(self, command, lba, value=None):
        if (command == 'W'):
            if type(value) is int:
                value = hex(value).upper()
            return self.ssd.run([None, 'W', lba, value])
        if (command == 'R'):
            return self.ssd.run([None, 'R', lba])
        if (command == 'E'):
            return self.ssd.run([None, 'E', lba, value])

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
              '4_EraseAndWriteAging :Performs 30 cycles of writing two random values to each even LBA (2–98), followed by erasing the next two LBA blocks to simulate aging behavior.\n',
              )
        self.logger.print(f"{self.help.__qualname__}()", "DONE")


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
                    self.logger.print(f"{self.PartialLBAWrite.__qualname__}()", "FAIL")
                    return
        print("PASS")
        self.logger.print(f"{self.PartialLBAWrite.__qualname__}()", "PASS")

    def WriteReadAging(self):
        value = random.randint(0, 0xFFFFFFFF)
        for i in range(200):
            self._send_command('W', 0, value)
            self._send_command('W', 99, value)
            if self.ssd_nand.readline(0).split()[1] != self.ssd_nand.readline(99).split()[1]:
                print('FAIL')
                self.logger.print(f"{self.WriteReadAging.__qualname__}()", "FAIL")
                return
        print('PASS')
        self.logger.print(f"{self.WriteReadAging.__qualname__}()", "PASS")

    def _aging(self, idx):
        value1, value2 = [random.randint(0, 0xFFFFFFFF) for _ in range(2)]
        self.write(idx, value1)
        self.write(idx, value2)
        self.erase_range(idx, min(idx + 2, 99))

    def EraseAndWriteAging(self):
        self.erase_range(0, 2)
        for i in range(30):
            for idx in range(2, 100, 2):
                self._aging(idx)

    def main_function(self, args):
        if not (args[0].lower(), len(args)) in self.command_dictionary(args):
            raise ValueError("INVALID COMMAND")
        self.command_dictionary(args)[(args[0].lower(), len(args))]()

    def command_dictionary(self, args):
        command_dict = {
            # ("read", 2): lambda: self.read(int(args[1])),
            ("read", 2): lambda: ReadCommand(self, int(args[1])).execute(),
            ("write", 3): lambda: WriteCommand(self, int(args[1]), int(args[2], 16)).execute(),
            ("fullwrite", 2): lambda: FullWriteCommand(self,int(args[1], 16)).execute(),
            ("fullread", 1): lambda: FullReadCommand(self).execute(),
            ('1_', 1): lambda: FullWriteAndReadCompareCommand(self).execute(),
            ('2_', 1): lambda: self.PartialLBAWrite(),
            ('3_', 1): lambda: self.WriteReadAging(),
            ('4_', 1): lambda: self.EraseAndWriteAging(),
            ('help', 1): lambda: self.help(),
            ('erase', 3): lambda: EraseCommand(self, int(args[1]), int(args[2])).execute(),
            ('erase_range', 3): lambda: EraseRangeCommand(self,int(args[1]), int(args[2])).execute()
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

    def option_main(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                command_lines = file.readlines()
            for command in command_lines:
                print(command[0:-1] + ' ' * self.option_dict()[command[0:2]] + '___   Run...', end=' ', flush=True)
                output_capture = io.StringIO()
                with contextlib.redirect_stdout(output_capture):
                    self.command_dictionary(command[0:2])[(command[0:2], 1)]()
                print(output_capture.getvalue().strip())
                if (output_capture.getvalue().strip()) == 'FAIL': return
        else:
            print("ERROR")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        Shell().main()
    elif len(sys.argv) == 2:
        Shell().option_main(sys.argv[1])
