import sys
import os

from buffer import Buffer
from ssd_commands import SSDCommand, SSDErrorCommand, SSDWriteCommand, SSDReadCommand, SSDEraseCommand
from ssd_texts import SSDNand, SSDOutput

class SSD:

    def run(self, sys_argv):
        cmd = sys_argv[1]
        args = sys_argv[2:]

        command: SSDCommand = self.get_command(cmd)
        command.check_input_validity(args)

        buffer = Buffer()
        buffer.run(sys_argv)

        command.run_command(args)

    def get_command(self, cmd) -> SSDCommand:
        if (cmd == 'W'):
            return SSDWriteCommand()
        elif (cmd == 'R'):
            return SSDReadCommand()
        elif (cmd == 'E'):
            return SSDEraseCommand()
        else:
            return SSDErrorCommand()


if __name__ == "__main__":
    # sys.argv[0] = 'ssd.py'
    # sys.argv[1] = 'W'
    # sys.argv[2] = '3'

    ssd = SSD()
    ssd.run(sys.argv)
