import sys
import os
from ssd_commands import SSDCommand, SSDErrorCommand, SSDWriteCommand, SSDReadCommand, SSDEraseCommand
from ssd_texts import SSDNand, SSDOutput

class SSD:
    def __init__(self):
        self._nand_txt = SSDNand()
        self._output_txt = SSDOutput()
        self._command: SSDCommand = SSDErrorCommand()

    @property
    def nand_txt(self):
        return self._nand_txt

    @property
    def output_txt(self):
        return self._output_txt

    def run(self, sys_argv):
        cmd = sys_argv[1]

        self._command = self.get_command(cmd)
        self._command.run_command(sys_argv[2:])

    def get_command(self, cmd):
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
