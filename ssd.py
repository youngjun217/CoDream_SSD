import sys
# from buffer import Buffer
import os

from ssd_commands import SSDCommand, ErrorCommand, WriteCommand, ReadCommand, EraseCommand
from ssd_texts import SSDNand, SSDOutput


class SSD():
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()
        self._command: SSDCommand = ErrorCommand()
        self.buffer = None  # Buffer()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def _check_buffer(self, cmd, lba, sys_argv):
        buffer_lst = self.buffer.buf_lst
        if (cmd == 'R'):
            for buffer_cmd in buffer_lst:
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1] == 'W' and int(cmd_lst[2]) == lba:
                    self._output_txt.write(f"{lba:02d} {cmd_lst[3]}\n")
                    return True
                if cmd_lst[1] == 'E':
                    start_lba = int(cmd_lst[2])
                    size = int(cmd_lst[3])
                    if start_lba <= lba < start_lba + size:
                        self._output_txt.write(f"{lba:02d} 0x00000000\n")
                        return True
            return False

        elif cmd == 'W':
            combine_idx = -1
            for idx, buffer_cmd in enumerate(buffer_lst):
                if 'empty' in buffer_cmd:
                    break
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1] == 'W' and int(cmd_lst[2]) == lba:
                    combine_idx = idx
                if cmd_lst[1] == 'E' and int(cmd_lst[2]) == lba and int(cmd_lst[3]) == 1:
                    combine_idx = idx

            if combine_idx >= 0:
                value = int(sys_argv[3], 16)
                old_name = f"./buffer/{buffer_lst[combine_idx]}"
                new_name = f"./buffer/{combine_idx}_{cmd}_{lba}_{value}"
                os.rename(old_name, new_name)

        elif (cmd == 'E'):
            size = int(sys_argv[3])
            self.erase_ssd(lba, size)
            # 기능 추가 필요

    def run(self, sys_argv):
        cmd = sys_argv[1]
        # lba = int(sys_argv[2])
        # if self._check_buffer(cmd, lba, sys_argv):
        #     return

        self._command = self.get_command(cmd)
        self._command.run_command(sys_argv[2:])

    def get_command(self, cmd):
        if (cmd == 'W'):
            return WriteCommand()
        elif (cmd == 'R'):
            return ReadCommand()
        elif (cmd == 'E'):
            return EraseCommand()
        else:
            return ErrorCommand()


if __name__ == "__main__":
    # sys.argv[0] = 'ssd.py'
    # sys.argv[1] = 'W'
    # sys.argv[2] = '3'

    ssd = SSD()
    ssd.run(sys.argv)
