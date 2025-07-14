import pytest
import ssd
def write(num:int, value:int)->None:
    if num<0:
        raise AssertionError()
    if num > 99:
        raise AssertionError()
    if not isinstance(value, int):
        raise TypeError("입력은 정수여야 합니다. 예: 0x10000000 같은 형식으로 입력하세요.")

    # 범위 제한 (선택)
    if not (0 <= value <= 0xFFFFFFFF):
        raise ValueError("입력값은 0x00000000 ~ 0xFFFFFFFF 범위여야 합니다.")

    if ssd.write(num, value):
        print('[Write] Done')
    pass

def test_write(mocker):
    mk = mocker.patch('ssd.write')
    write(3,0x00000000)
    write(0,0x00000000)
    write(3,0x03300000)
    with pytest.raises(AssertionError):
        write(-1,0x00000000)
        write(100,0x00000000)
        write('3',0x00000000)
        write(3,0x0000000011)
    mk.call_count==7
    pass

# read
# write
# exit : 프로그램 종료
# help : 프로그램 사용법
# 제작자 명시 (팀장/팀원)
# 각 명령어마다 사용법 기입
# fullwrite : 전체 인덱스 (LBA) write
# fullread : 전체 인덱스 (LBA) read
# Test Script 실행 명령 : Test Script 부분에서 상세 설명
# 없는 명령어 : INVALID COMMAND 출력

####추가
# 1_FullWriteAndReadCompare
#
# 1_ 라고만 입력해도 실행 가능
# 0 ~ 4번 LBA까지 다섯개의 동일한 랜덤 값으로 write 명령어 수행
# 0 ~ 4번 LBA까지 실제 저장된 값과 맞는지 확인
# 5 ~ 9번 LBA까지 다섯개의 동일하지만 0 ~ 4번과 다른 랜덤값으로 write 명령어 수행
# 5 ~ 9번 LBA까지 실제 저장된 값과 맞는지 확인
# 위와 같은 규칙으로 전체 영역에 대해 반복
# 2_PartialLBAWrite
#
# 2_ 라고만 입력해도 실행 가능
# 30회 반복
# 4번 LBA에 랜덤값을 적는다.
# 0번 LBA에 같은 값을 적는다.
# 3번 LBA에 같은 값을 적는다.
# 1번 LBA에 같은 값을 적는다.
# 2번 LBA에 같은 값을 적는다.
# LBA 0 ~ 4번 모두 같은지 확인
# 3_WriteReadAging
#
# 3_ 라고만 입력해도 실행 가능
# 200회 반복
# 0번 LBA에 랜덤 값을 적는다.
# 99번 LBA에 같은 값을 적는다.
# LBA 0번과 99번이 같은지 확인

#shell 실행 시 명령어 받는 부분
