import sys
from ssd import SSD

class shell_ftn:
    def read(self,idx:int):
        if idx<0 or idx>99:
            raise ValueError("ERROR")
        if type(idx)!=int:
            raise ValueError("ERROR")
        result = SSD().read_ssd(idx)
        print(f'[Read] LBA {idx}: {result}')
        return result


    def write(self,num, value):
        if num<0:
            raise AssertionError()
        if num > 99:
            raise AssertionError()
        if not isinstance(value, str):
            raise TypeError("입력은 문자열이어야 합니다. 예: '0x00000000'")

        if not value.startswith("0x"):
            raise ValueError("입력은 '0x'로 시작해야 합니다.")

        hex_part = value[2:]

        if len(hex_part) != 8:
            raise ValueError("0x 뒤에 정확히 8자리여야 합니다.")

        # 각 문자들이 16진수 범위인지 검사
        valid_chars = "0123456789abcdefABCDEF"
        if not all(c in valid_chars for c in hex_part):
            raise ValueError("16진수 숫자만 허용됩니다 (0-9, A-F).")

        if SSD().write_ssd(num, value):
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
            ssd_output = open("ssd_output.txt", "w")

            print("[Full Read]")
            for i in range(100):
                str = ssd_nand.readline()
                if str:
                    words = str.split()
                    print(f"LBA {words[0]} : {words[1]}\n")

            ssd_nand.close()
            ssd_output.close()
        except Exception as e:
            raise e

    def FullWriteAndReadCompare(self):
        print("1_FullWriteAndReadCompare")
        # 1_FullWriteAndReadCompare
        #
        # 1_ 라고만 입력해도 실행 가능
        # 0 ~ 4번 LBA까지 다섯개의 동일한 랜덤 값으로 write 명령어 수행
        # 0 ~ 4번 LBA까지 실제 저장된 값과 맞는지 확인
        # 5 ~ 9번 LBA까지 다섯개의 동일하지만 0 ~ 4번과 다른 랜덤값으로 write 명령어 수행
        # 5 ~ 9번 LBA까지 실제 저장된 값과 맞는지 확인
        # 위와 같은 규칙으로 전체 영역에 대해 반복

    def PartialLBAWrite(self):
        print("2_PartialLBAWrite")

    def WriteReadAging(self):
        print("3_WriteReadAging")

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

