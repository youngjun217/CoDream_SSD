import os

from ssd_texts import SSDOutput, SSDText

EMPTY = 0
EMPTY_VALUE = 0x00000000
ERASE_VALUE = 0x00000000
WRITE = 1
ERASE = 2
BUFFER_SIZE = 5
MAX_ERASE_SIZE = 10
BUFFER_FOLDER_PATH = "./buffer"


class Buffer:

    def __init__(self):
        self._folder_path = BUFFER_FOLDER_PATH
        self._buf_lst = [''] * BUFFER_SIZE
        self._buffer_cnt = 0
        self._output_txt: SSDText = SSDOutput()
        self._run_command = []
        self._buffer_cmd_memory = [[EMPTY, EMPTY_VALUE] for _ in range(100)]

        self.create()

    def create(self):
        if not os.path.exists(self._folder_path):
            os.makedirs(self._folder_path)

        self.get_exist_files()
        self._make_absent_files()

    def get_exist_files(self):
        file_list = os.listdir(self._folder_path)
        for file_name in file_list:
            splited_file_name = file_name.split("_")
            new_index = int(splited_file_name[0]) - 1
            self._buf_lst[new_index] = file_name
            if file_name[2:] != 'empty':
                self._buffer_cnt += 1
                cmd, lba, value = self._get_buf_information(file_name)
                if cmd == 'W':
                    value = int(value, 16)
                    self._set_buffer_with_write(WRITE, lba, value)
                else:
                    size = int(value)
                    self._set_buffer_with_erase(ERASE, lba, size)

    def _set_buffer_with_write(self, set_cmd, lba, value):
        self._buffer_cmd_memory[lba][0] = WRITE if set_cmd == WRITE else EMPTY
        self._buffer_cmd_memory[lba][1] = value if set_cmd == WRITE else EMPTY_VALUE

    def _set_buffer_with_erase(self, set_cmd, lba, size):
        for index in range(lba, lba + size):
            self._buffer_cmd_memory[index][0] = ERASE if set_cmd == ERASE else EMPTY
            self._buffer_cmd_memory[index][1] = ERASE_VALUE if set_cmd == ERASE else EMPTY_VALUE

    def _make_absent_files(self):
        for index, buf in enumerate(self._buf_lst):
            if buf != '':
                continue
            file_name = f'{index}_empty'
            file_path = os.path.join(self._folder_path, f'{index}_empty')
            open(file_path, 'a').close()
            self._buf_lst[index] = file_name

    def _get_buf_information(self, buf_val):
        _, cmd, lba, value = buf_val.split("_")
        return cmd, int(lba), value

    def run(self, sys_argv):
        self._run_command = []
        cmd = sys_argv[1]
        if cmd == 'R':
            self._check_buffer_read(sys_argv)
        elif cmd == 'W':
            self._check_buffer_write(sys_argv)
        elif cmd == 'E':
            self._check_buffer_erase(sys_argv)
        else:
            self._flush(self._buffer_cnt)

        self._update_buffer_files()
        return self._run_command

    def _check_buffer_read(self, sys_argv):
        lba = int(sys_argv[2])

        if self._buffer_cmd_memory[lba][0] != EMPTY:
            self._output_txt.write(f"{lba:02d} 0x{self._buffer_cmd_memory[lba][1]:08X}\n")  # f"0x{value:08X}"
        else:
            self._run_command.append(sys_argv)

    def _check_buffer_write(self, sys_argv):
        lba = int(sys_argv[2])
        value = int(sys_argv[3], 16)

        if self._buffer_cmd_memory[lba][0] != WRITE and self._buffer_cnt == BUFFER_SIZE:
            self._flush(self._buffer_cnt)

        self._set_buffer_all_empty()
        self._merge_erases()

        self._set_buffer_with_write(WRITE, lba, value)
        self._merge_writes()

        self._output_txt.write("")

    def _check_buffer_erase(self, sys_argv):
        lba = int(sys_argv[2])
        size = int(sys_argv[3])

        self._set_buffer_all_empty()
        self._set_buffer_with_erase(ERASE, lba, size)

        self._merge_erases()
        self._merge_writes()

    def _set_buffer_all_empty(self):
        self._buffer_cnt = 0
        for index in range (BUFFER_SIZE):
            self._buf_lst[index] = f'{index+1}_empty'

    def _merge_writes(self):
        for lba, memory_value in enumerate(self._buffer_cmd_memory):
            if memory_value[0] != WRITE:
                continue
            if self._buffer_cnt == BUFFER_SIZE:
                self._flush(self._buffer_cnt)

            self._buf_lst[self._buffer_cnt] = f"{self._buffer_cnt + 1}_W_{lba}_0x{memory_value[1]:08X}"
            self._buffer_cnt += 1

    def _merge_erases(self):
        erase_cnt = 0
        first_lba = 0
        for lba, memory_value in enumerate(self._buffer_cmd_memory):
            if memory_value[0] != ERASE:
                if erase_cnt > 0:
                    erase_cnt = self._set_erace_command(first_lba, erase_cnt)
                continue

            first_lba = lba if erase_cnt == 0 else first_lba
            erase_cnt += 1

            if erase_cnt == MAX_ERASE_SIZE:
                erase_cnt = self._set_erace_command(first_lba, erase_cnt)

    def _set_erace_command(self, lba, size):
        if self._buffer_cnt == BUFFER_SIZE:
            self._flush(self._buffer_cnt)

        self._buf_lst[self._buffer_cnt] = f"{self._buffer_cnt + 1}_E_{lba}_{size}"
        self._buffer_cnt += 1
        return 0

    def _flush(self, cnt):
        for i in range(cnt):
            self._remove_buffer_and_put_run_command(i)
            self._buf_lst[i] = f"{i + 1}_empty"
            self._buffer_cnt -= 1

    def _remove_buffer_and_put_run_command(self, index):
        flushed_cmd, flushed_lba, flushed_value = self._get_buf_information(self._buf_lst[index])
        if flushed_cmd == "W":
            self._set_buffer_with_write(EMPTY, flushed_lba, flushed_value)
        if flushed_cmd == "E":
            flushed_size = int(flushed_value)
            self._set_buffer_with_erase(EMPTY, flushed_lba, flushed_size)
        self._run_command.append([None, flushed_cmd, flushed_lba, flushed_value])

    def _update_buffer_files(self):
        for filename in os.listdir(self._folder_path):
            file_path = os.path.join(self._folder_path, filename)
            os.remove(file_path)
        for buf in self._buf_lst:
            file_path = os.path.join(self._folder_path, buf)
            open(file_path, 'a').close()
