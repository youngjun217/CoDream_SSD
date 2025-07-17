import os

# from ssd import SSD


class Buffer:

    def __init__(self):
        self.folder_path = './buffer'
        self.buf_lst = []
        self.create()

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
            _, command, lba, value = file_name.split("_")
            if command == "W":
                ssd.write_ssd(lba, value)
            if command == "E":
                ssd.erase_ssd(lba, value)

    def flush(self):
        for idx, file in enumerate(self.buf_lst):
            os.rename(f"{self.folder_path}/{file}", f"{self.folder_path}/{idx+1}_empty")
