import os
from ssd import SSD


class Buffer:

    def __init__(self):
        self.folder_path = './buffer'
        self.buf_lst = []
        self.create()
        self.ssd = SSD()

    def create(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        for i in range(1,6):
            file_name = f'{i}_empty'
            file_path = os.path.join(self.folder_path, f'{i}_empty')
            open(file_path, 'a').close()
            self.buf_lst.append(file_name)

    def write(self, command, lba, value):
        if command == 'R':
            return

        empty_idx = -1
        for idx, file_name in enumerate(self.buf_lst):
            splited_file_name = file_name.split("_")
            if splited_file_name[1] == "empty":
                empty_idx = idx+1
                break

        if empty_idx == -1:
            self.flush()

        old_name = f"{self.folder_path}/{empty_idx}_empty"
        new_name = f"{self.folder_path}/{empty_idx}_{command}_{lba}_{value}"
        if empty_idx != -1:
            os.rename(old_name, new_name)

    def execute(self):
        ssd = SSD()
        for file_name in self.buf_lst:
            idx, command, lba, value = file_name.split("_")
            if command == "W":
                ssd.write_ssd(lba, value)
            if command == "E":
                ssd.erase_ssd(lba, value)


    def flush(self):
        self.execute()
        for idx, file in enumerate(self.buf_lst):
            os.rename(f"{self.folder_path}/{file}", f"{self.folder_path}/{idx+1}_empty")
            self.buf_lst[idx] = f"{idx + 1}_empty"


    def run(self, sys_argv):
        cmd = sys_argv[1]
        lba = int(sys_argv[2])
        buffer_lst = self.buf_lst
        if cmd == 'R':
            for buffer_cmd in buffer_lst:
                cmd_lst = buffer_cmd.split('_')
                if cmd_lst[1] == 'W' and int(cmd_lst[2]) == lba:
                    self.ssd._output_txt.write(f"{lba:02d} {cmd_lst[3]}\n")
                    return
                if cmd_lst[1] == 'E':
                    start_lba = int(cmd_lst[2])
                    size = int(cmd_lst[3])
                    if start_lba <= lba < start_lba + size:
                        self.ssd._output_txt.write(f"{lba:02d} 0x00000000\n")
                        return
            self.ssd.run(sys_argv)

        elif cmd == 'W':
            self.ssd._output_txt.write("")
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

        elif cmd == 'E':
            # 기능 추가 필요
            pass
