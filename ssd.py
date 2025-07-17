import sys
import os

from buffer import Buffer
from ssd_commands import SSDCommand, SSDErrorCommand, SSDWriteCommand, SSDReadCommand, SSDEraseCommand, SSDFlushCommand
from ssd_texts import SSDNand, SSDOutput

class SSD:
    def __init__(self, no_buf_mode = False):
        self._no_buf_mode = no_buf_mode

    def run(self, sys_argv):

        command, args = self._get_command(sys_argv)
        command.check_input_validity(args)

        if self._no_buf_mode:
            command.run_command(args)
            return

        buffer = Buffer()
        run_command_lst = buffer.run(sys_argv)

        if not run_command_lst:
            return

        for argv in run_command_lst:
            command, args = self._get_command(argv)
            command.run_command(args)

    def _get_command(self, sys_argv) -> (SSDCommand, list):
        cmd = sys_argv[1]

        if cmd == 'W':
            return SSDWriteCommand(), sys_argv[2:]
        elif cmd == 'R':
            return SSDReadCommand(), sys_argv[2:]
        elif cmd == 'E':
            return SSDEraseCommand(), sys_argv[2:]
        elif cmd == 'F':
            return SSDFlushCommand(), sys_argv[2:]
        else:
            return SSDErrorCommand(), []


if __name__ == "__main__":
    # sys.argv[0] = 'ssd.py'
    # sys.argv[1] = 'W'
    # sys.argv[2] = '3'

    ssd = SSD()
    ssd.run(sys.argv)
