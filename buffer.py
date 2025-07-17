import os

from ssd_texts import SSDOutput

EMPTY = 0
EMPTY_VALUE = 0x00000000
WRITE = 1
ERASE = 2
BUFFER_SIZE = 5
BUFFER_FOLDER_PATH = "./buffer"

class Buffer:

    def __init__(self):
        self.folder_path = BUFFER_FOLDER_PATH
        self.buf_lst = [''] * (BUFFER_SIZE + 1)
        self.create()
        self._output_txt = SSDOutput()
        self._run_command = []
        self.command_memory = [EMPTY] * 100
        self.value_memory = [EMPTY_VALUE] * 100

    def create(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

        file_list = os.listdir(self.folder_path)
        for file_name in file_list:
            splited_file_name = file_name.split("_")
            new_index = int(splited_file_name[0])
            self.buf_lst[new_index] = file_name

        for index, buf in enumerate(self.buf_lst):
            if index == 0 or buf != '':
                continue
            file_name = f'{index}_empty'
            file_path = os.path.join(self.folder_path, f'{index}_empty')
            open(file_path, 'a').close()
            self.buf_lst[index] = file_name

    def run(self, sys_argv):
        self.set_buffer(sys_argv)
        cmd = sys_argv[1]
        lba = int(sys_argv[2])

        if cmd == "R":
            self._output_txt.write(f"{lba:02d} 0x{self.value_memory[lba]:08X}\n")  #f"0x{value:08X}"
        if cmd == "W":
            self._output_txt.write("")

    def set_buffer(self, sys_argv):
        self.buf_lst = []
        cmd = sys_argv[1]
        lba = int(sys_argv[2])

        if cmd == "W":
            value = int(sys_argv[3], 16)
            self.command_memory[lba] = WRITE
            self.value_memory[lba] = value
            self._output_txt.write("")

        if cmd == "E":
            size = int(sys_argv[3])
            for erase_lba in range(lba, lba+size):
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

        flashed = False
        while len(self.buf_lst) > 5:
            #flash
            flashed = True
            for i in range(5):
                _, flushed_cmd, flushed_lba, flushed_value = self.buf_lst[i].split("_")
                flushed_lba = int(flushed_lba)
                if flushed_cmd == "W":
                    self.command_memory[int(flushed_lba)] = EMPTY
                if flushed_cmd == "E":
                    flushed_value = int(flushed_value)
                    for flush_erase_idx in range(flushed_lba, flushed_lba+flushed_value):
                        self.command_memory[int(flush_erase_idx)] = EMPTY

            self.buf_lst = self.buf_lst[5:]

        for buf_idx, buf in enumerate(self.buf_lst):
            self.buf_lst[buf_idx] = f"{buf_idx+1}_{buf[2:]}"

        while len(self.buf_lst) < 5:
            self.buf_lst.append(f"{len(self.buf_lst)+1}_empty")


        if flashed:
            for filename in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, filename)
                os.remove(file_path)
            for buf in self.buf_lst:
                file_path = os.path.join(self.folder_path, buf)
                open(file_path, 'a').close()


            for idx, filename in enumerate(os.listdir(self.folder_path)):
                if self.buf_lst[idx] != filename:
                    file_path = os.path.join(self.folder_path, filename)
                    os.rename(file_path, f"{self.folder_path}/{self.buf_lst[idx]}")
