import contextlib
import datetime
import glob
import inspect
import io
import os
import random
import sys
import time
from abc import ABC, abstractmethod
from ssd_interface import SSDInterface, SSDConcreteInterface


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

    def print(self, header, message):
        self.rotate_log_if_needed()
        with open("latest.log", 'a', encoding='utf-8') as file:
            now = datetime.datetime.now()
            log = f"[{now.strftime('%y.%m.%d %H:%M')}] {header}\t: {message}\n"
            log = log.expandtabs(tabsize=70)
            file.write(log)

    def rotate_log_if_needed(self):
        if os.path.exists(self.LOG_FILE) and os.path.getsize(self.LOG_FILE) > self.MAX_SIZE:
            for existing in glob.glob("until_*.log"):
                os.rename(existing, existing.replace(".log", ".zip"))

            timestamp = time.strftime("until_%y%m%d_%Hh_%Mm_%Ss")
            new_name = f"{timestamp}.log"
            os.rename(self.LOG_FILE, new_name)
            time.sleep(0.3)


class Command(ABC):
    def __init__(self, shell):
        self.shell = shell

    @abstractmethod
    def execute(self):
        pass


class ShellReadCommand(Command):
    def __init__(self, shell, lba):
        super().__init__(shell)
        self.lba = lba

    def execute(self) -> None:
        self.shell.send_command('R', self.lba)
        value = self.shell.get_response_value()
        print(f'[Read] LBA {self.lba}: {value}')
        self.shell.logger.print(f"{self.execute.__qualname__}()", f"LBA {self.lba}: {value}")


class ShellWriteCommand(Command):
    def __init__(self, shell, lba: int, value: int):
        super().__init__(shell)
        self.lba = lba
        self.value = value

    def execute(self) -> bool:
        self.shell.send_command('W', self.lba, self.value)
        if self.shell.get_response_value() == '':
            print('[Write] Done')
            self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")
            return True

        self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
        return False


class ShellEraseCommand(Command):
    def __init__(self, shell, st_lba: int, erase_size: int):
        super().__init__(shell)
        self.st_lba = st_lba
        self.erase_size = erase_size

    def execute(self):
        if (0 > self.st_lba or self.st_lba > 99) or (1 > self.erase_size or self.erase_size > 100) or (self.st_lba + self.erase_size > 100):
            self.shell.logger.print(f"{self.execute.__qualname__}()", f"FAIL")
            raise Exception()

        offset = 0
        while self.erase_size > 0:
            erase_size = min(self.erase_size, 10)
            self.shell.send_command('E', self.st_lba + offset, erase_size)
            offset += 10
            self.erase_size -= erase_size


        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class ShellEraseRangeCommand(Command):
    def __init__(self, shell, st_lba: int, en_lba: int):
        super().__init__(shell)
        self.st_lba = st_lba
        self.en_lba = en_lba

    def execute(self) -> None:
        if self.st_lba > self.en_lba or self.st_lba < 0 or self.en_lba > 100:
            raise ValueError

        erase_range = self.en_lba - self.st_lba + 1  # inclusive range
        erase_cmd = ShellEraseCommand(self.shell, self.st_lba, erase_range)
        erase_cmd.execute()


class ShellFullWriteCommand(Command):
    def __init__(self, shell, value):
        super().__init__(shell)
        self.value = value

    def execute(self):
        for lba in range(100):
            self.shell.send_command('W', lba, self.value)

        print("[Full Write] Done")
        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class ShellFullReadCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        print("[Full Read]")
        for lba in range(100):
            try:
                self.shell.send_command('R', lba)
                value = self.shell.get_response_value()
                if value == "ERROR":
                    print(value)
                print(f"LBA {lba} : {value}")
            except Exception as e:
                self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                raise e

        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class ShellFullWriteAndReadCompareCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        for st_lba in range(0, 100, 5):
            for offset in range(5):
                random_value = random.randint(0, 0xFFFFFFFF)
                self.shell.send_command('W', st_lba + offset, random_value)
                self.shell.send_command('R', st_lba + offset)
                if self.shell.get_response_value() != f"0x{random_value:08X}":
                    print('FAIL')
                    self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                    return

        print('PASS')
        self.shell.logger.print(f"{self.execute.__qualname__}()", "PASS")

class ShellPartialLBAWriteCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        lba_list = [4, 0, 3, 1, 2]
        for _ in range(30):
            random_value = random.randint(0, 0xFFFFFFFF)
            for i in range(5):
                self.shell.send_command('W', lba_list[i], random_value)

            self.shell.send_command('R', 0)
            ref_value = self.shell.get_response_value()
            for lba in range(1, 5):
                self.shell.send_command('R', lba)
                comp_value = self.shell.get_response_value()
                if ref_value != comp_value:
                    print('FAIL')
                    self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                    return

        print("PASS")
        self.shell.logger.print(f"{self.execute.__qualname__}()", "PASS")

class ShellEraseAndWriteAgingCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def _aging(self, lba):
        random_value1, random_value2 = [random.randint(0, 0xFFFFFFFF) for _ in range(2)]
        self.shell.send_command('W', lba, random_value1)
        self.shell.send_command('W', lba, random_value2)
        ShellEraseRangeCommand(self.shell, lba, min(lba + 2, 99)).execute()

    def execute(self):
        self.shell.send_command('E', 0, 3)
        for _ in range(30):
            for lba in range(2, 100, 2):
                try:
                    self._aging(lba)
                except Exception as e:
                    print('FAIL')
                    self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                    raise e

        print('PASS')
        self.shell.logger.print(f"{self.execute.__qualname__}()", "PASS")


class ShellWriteReadAgingCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        random_value = random.randint(0, 0xFFFFFFFF)
        for _ in range(200):
            self.shell.send_command('W', 0, random_value)
            self.shell.send_command('W', 99, random_value)

            self.shell.send_command('R', 0)
            ref_value = self.shell.get_response_value()

            self.shell.send_command('R', 99)
            comp_value = self.shell.get_response_value()

            if ref_value != comp_value:
                print('FAIL')
                self.shell.logger.print(f"{self.execute.__qualname__}()", "FAIL")
                return

        print('PASS')
        self.shell.logger.print(f"{self.execute.__qualname__}()", "PASS")


class ShellFlushCommand:
    def __init__(self, shell):
        super().__init__(shell)

    def execute(self):
        self.shell.ssd_interface.run()
        pass

class ShellHelpCommand(Command):
    def __init__(self, shell):
        super().__init__(shell)
    def execute(self):
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
        self.shell.logger.print(f"{self.execute.__qualname__}()", "DONE")

class Shell:
    def __init__(self):
        self.logger = Logger()
        self.ssd_interface: SSDInterface = SSDConcreteInterface()

    def send_command(self, command, lba, value=None):
        if command == 'W':
            if type(value) is int:
                value = f"0x{value:08X}"
            return self.ssd_interface.run([None, 'W', lba, value])
        if command == 'R':
            return self.ssd_interface.run([None, 'R', lba])
        if command == 'E':
            return self.ssd_interface.run([None, 'E', lba, value])
        if command == 'F':
            return self.ssd_interface.run([None, 'F'])
        return None

    def get_response(self):
        return self.ssd_interface.get_response()

    def get_response_value(self):
        output = self.ssd_interface.get_response()
        if len(output.split()) == 2:
            return output.split()[1]
        return output

    # help : 프로그램 사용법


    def main_function(self, args):
        if not (args[0], len(args)) in self.command_dictionary(args):
            raise ValueError("INVALID COMMAND")
        #self.command_dictionary(args)[(args[0], len(args))]()
        shellCommand : Command = self.command_dictionary(args)[(args[0], len(args))]()
        shellCommand.execute()

    def command_dictionary(self, args):
        command_dict = {
            ("read", 2): lambda: ShellReadCommand(self, int(args[1])),
            ("write", 3): lambda: ShellWriteCommand(self, int(args[1]), int(args[2], 16)),
            ("fullwrite", 2): lambda: ShellFullWriteCommand(self, int(args[1], 16)),
            ("fullread", 1): lambda: ShellFullReadCommand(self),
            ('1_', 1): lambda: ShellFullWriteAndReadCompareCommand(self),
            ('2_', 1): lambda: ShellPartialLBAWriteCommand(self),
            ('3_', 1): lambda: ShellWriteReadAgingCommand(self),
            ('4_', 1): lambda: ShellEraseAndWriteAgingCommand(self),
            ('1_FullWriteAndReadCompare', 1): lambda: ShellFullWriteAndReadCompareCommand(self),
            ('2_PartialLBAWrite', 1): lambda: ShellPartialLBAWriteCommand(self),
            ('3_WriteReadAging', 1): lambda: ShellWriteReadAgingCommand(self),
            ('4_EraseAndWriteAging', 1): lambda: ShellEraseAndWriteAgingCommand(self),
            ('help', 1): lambda: ShellHelpCommand(self),
            ('erase', 3): lambda: ShellEraseCommand(self, int(args[1]), int(args[2])),
            ('erase_range', 3): lambda: ShellEraseRangeCommand(self, int(args[1]), int(args[2])),
            ('flush',1): lambda:ShellFlushCommand(self)
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
            ('3_'): 14,
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
                    # self.command_dictionary(command[0:2])[(command[0:2], 1)]()
                    shellCommand: Command = self.command_dictionary(command[0:2])[(command[0:2], 1)]()
                    shellCommand.execute()
                print(output_capture.getvalue().strip())
                if (output_capture.getvalue().strip()) == 'FAIL': return
        else:
            print("ERROR")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        Shell().main()
    elif len(sys.argv) == 2:
        Shell().option_main(sys.argv[1])
