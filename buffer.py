import os

from ssd import SSD


class Buffer:

    def __init__(self):
        self.folder_path = './buffer'

    def read(self):
        files = os.listdir(self.folder_path)
        files = sorted(files, key=lambda x: int(x.split('_')[0]))
        return files

    def write(self, command, lba, value):
        if command == 'R':
            return

        files = self.read()
        empty_idx = -1
        for idx, file_name in enumerate(files):
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

    def execute(self, files):
        ssd = SSD()
        for file_name in files:
            _, command, lba, value = file_name.split("_")
            if command == "W":
                ssd.write_ssd(lba, value)
            if command == "E":
                ssd.erase_ssd(lba, value)

    def flush(self):
        files = self.read()
        self.execute(files)
        for idx, file in enumerate(files):
            os.rename(f"{self.folder_path}/{file}", f"{self.folder_path}/{idx+1}_empty")