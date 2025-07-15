import sys
from ssd import SSD
import random

class shell_ftn():
    def __init__(self):
        self.ssd = SSD()

    def read(self,idx:int):
        if idx<0 or idx>99:
            raise ValueError("ERROR")
        if type(idx)!=int:
            raise ValueError("ERROR")
        result = self.ssd.read_ssd(idx)
        print(f'[Read] LBA {idx}: {result}')
        return result


    def write(self, num:int, value:int)->None:
        if num<0:
            raise AssertionError()
        if num > 99:
            raise AssertionError()
        if not isinstance(value, str):
            raise TypeError("입력은 문자열이어야 합니다. 예: '0x00000000'")

        if not value.startswith("0x"):
            raise ValueError("입력은 '0x'로 시작해야 합니다.")

        hex_part = value[2:]

        
        # 각 문자들이 16진수 범위인지 검사
        valid_chars = "0123456789abcdefABCDEF"
        if not all(c in valid_chars for c in hex_part):
            raise ValueError("16진수 숫자만 허용됩니다 (0-9, A-F).")

        if self.ssd.write_ssd(num, value):
            print('[Write] Done')
        pass

    # help : 프로그램 사용법
    def help(self):
        print('help')
        # 제작자 명시 (팀장/팀원)
        # 각 명령어마다 사용법 기입

    def fullwrite(self, value):
        if len(str(value)) > 8:
            raise ValueError("ERROR")
        for x in range(100):
            SSD().write_ssd(x,value)
        print("[Full Write] Done")

    def fullread(self):
        try:
            ssd_nand = open("ssd_nand.txt", "r")

            print("[Full Read]")

            for idx in range(100):
                self.ssd.read_ssd(idx)
                ssd_output = open("ssd_output.txt", "r")
                str = ssd_output.readline()
                print(f"LBA {str.split()[0]} : {str.split()[1]}")

            ssd_nand.close()
            ssd_output.close()
        except Exception as e:
            raise e

    def FullWriteAndReadCompare(self):
        for start_idx in range(0, 100, 5):
            rand_num = random.randint(0x00000000, 0xFFFFFFFF)
            rand_num_list = [rand_num] * 5
            for x in range(5):
                SSD().write_ssd(start_idx+x,rand_num_list[x])
                if SSD().read_ssd(start_idx+x) == rand_num_list[x]:
                    pass


    def PartialLBAWrite(self):
        for i in range(30):
            r1 = random.randint(0, 0xFFFFFFFF)
            r1 = hex(r1)
            self.write(4,r1)
            self.write(0,r1)
            self.write(3,r1)
            self.write(1,r1)
            self.write(2,r1)

            a = self.read(0)
            if a!= self.read(1):
                print("FAIL")
                return False
            if a!= self.read(2):
                print("FAIL")
                return False
            if a!= self.read(3):
                print("FAIL")
                return False
            if a!= self.read(4):
                print("FAIL")
                return False
        print("PASS")
        return True


    def _read_line(self, filepath, line_number):
        with open(filepath, 'r', encoding='utf-8') as f:
            for current_line, line in enumerate(f, start=1):
                if current_line == line_number:
                    parts = line.strip().split()
                    return int(parts[1])
        return None

    def WriteReadAging(self, filepath):
        value = random.randint(0, 0xFFFFFFFF)
        ssd = SSD()
        for i in range(200):
            ssd.write_ssd(0, value)
            ssd.write_ssd(99, value)
            if self._read_line(filepath, 1) != self._read_line(filepath, 100):
                print('FAIL')
                return
        print('PASS')

    def testScript(self,test_intro):
        if test_intro == '1_':
            self.FullWriteAndReadCompare()
        elif test_intro == '2_':
            self.PartialLBAWrite()
        elif test_intro == '3_':
            self.WriteReadAging()

    def main_function(self,args):
        if args[0].lower() == "read" and len(args)==2:
            self.read(int(args[1])) #idx
        elif args[0].lower() == "write"and len(args)==3:
            self.write(int(args[1]), args[2]) #idx, value
        elif args[0].lower() == "fullwrite"and len(args)==2:
            self.fullwrite(args[1]) #value
        elif args[0].lower() == "fullread"and len(args)==1:
            self.fullread()
        elif args[0][0:2] in ['1_','2_','3_']and len(args)==1:
            test_intro = args[0][0:2]
            self.testScript(test_intro)
        else:
            raise ValueError("INVALID COMMAND")


    def main(self):
        while True:
            command = input("Shell>")
            args = command.split()
            if args==[]: raise ValueError("INVALID COMMAND")
            if args[0].lower() == "exit":
                # print("Exiting the program...")
                break
            self.main_function(args)

if __name__ == "__main__":
    shell_ftn().main()

