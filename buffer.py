import os

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
        for idx, file in enumerate(files):
            if "empty" in file:
                empty_idx = idx+1
                break

        old_name = f"{self.folder_path}/{empty_idx}_empty"
        new_name = f"{self.folder_path}/{empty_idx}_{command}_{lba}_{value}"
        if empty_idx != -1:
            os.rename(old_name, new_name)

    def execute(self):
        pass

    def flush(self):
        self.execute()
        files = self.read()
        for idx, file in enumerate(files):
            os.rename(f"{self.folder_path}/{file}", f"{self.folder_path}/{idx+1}_empty")

