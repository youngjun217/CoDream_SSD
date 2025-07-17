import os

from ssd import SSD

EMPTY = 0
EMPTY_VALUE = 0x00000000
WRITE = 1
ERASE = 2

class Buffer:

    def __init__(self):
        self.folder_path = './buffer'
        self.buf_lst = []
        self.create()
        self.ssd = SSD()
        self.command_memory = [EMPTY] * 100
        self.value_memory = [EMPTY_VALUE] * 100

    def create(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        for i in range(1, 6):
            file_name = f'{i}_empty'
            file_path = os.path.join(self.folder_path, f'{i}_empty')
            open(file_path, 'a').close()
            self.buf_lst.append(file_name)

    def write(self, command, lba, value=None):
        empty_idx = -1
        for idx, file_name in enumerate(self.buf_lst):
            splited_file_name = file_name.split("_")
            if splited_file_name[1] == "empty":
                empty_idx = idx + 1
                break

        if empty_idx == -1:
            self.flush()
            empty_idx=1

        old_name = f"{self.folder_path}/{empty_idx}_empty"
        new_name = f"{self.folder_path}/{empty_idx}_{command}_{lba}_{value}"
        if empty_idx != -1:
            os.rename(old_name, new_name)
            self.buf_lst[empty_idx - 1] = f"{empty_idx}_{command}_{lba}_{value}"

    def execute(self):
        for file_name in self.buf_lst:
            _, command, lba, value = file_name.split("_")
            self.ssd.run([None, command, lba, value])

    def flush(self):
        self.execute()
        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        self.buf_lst.clear()
        self.create()

    def run(self, sys_argv):
        self.set_buffer(sys_argv)
        cmd = sys_argv[1]
        lba = int(sys_argv[2])

        if cmd == "R":
            self.ssd._output_txt.write(f"{lba:02d} 0x{self.value_memory[lba]:08X}\n")  #f"0x{value:08X}"
        if cmd == "W":
            self.ssd._output_txt.write("")

        #if buffer size is over 6, flush feature is needed. it's not developed yet.

    def set_buffer(self, sys_argv):
        self.buf_lst = []
        cmd = sys_argv[1]
        lba = int(sys_argv[2])
        value = int(sys_argv[3]) if cmd != "R" else 0

        if cmd == "W":
            self.command_memory[lba] = WRITE
            self.value_memory[lba] = value

        if cmd == "E":
            for erase_lba in range(lba, lba+value):
                self.command_memory[erase_lba] = ERASE
                self.value_memory[erase_lba] = EMPTY_VALUE

        #update buffer
        prev_command = EMPTY
        start_lba = -1
        erase_size = 0
        for memory_lba, saved_command in enumerate(self.command_memory):
            if saved_command == WRITE:
                self.buf_lst.append(f"{len(self.buf_lst)+1}_W_{memory_lba}_0x{self.value_memory[memory_lba]:08X}")
                if prev_command == ERASE:
                    self.buf_lst.append(f"{len(self.buf_lst)+1}_E_{start_lba}_{erase_size}")
                prev_command = WRITE
                continue

            if saved_command == EMPTY:
                if prev_command == ERASE:
                    self.buf_lst.append(f"{len(self.buf_lst)+1}_E_{start_lba}_{erase_size}")
                prev_command = EMPTY
                continue

            if saved_command == ERASE:
                if prev_command != ERASE:
                    start_lba = memory_lba
                    erase_size = 1
                    prev_command = ERASE
                else:
                    erase_size += 1
                    if erase_size == 10:
                        self.buf_lst.append(f"{len(self.buf_lst)+1}_E_{start_lba}_{erase_size}")
                        prev_command = EMPTY

        while len(self.buf_lst) != 5:
            self.buf_lst.append(f"{len(self.buf_lst)+1}_empty")