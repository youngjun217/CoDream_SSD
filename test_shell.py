import pytest
from pytest_mock import MockerFixture
from unittest.mock import call

import ssd
from shell import shell_ftn
from ssd import SSD, SSDOutput


class TestableSSD(SSD):
    def __init__(self):
        self._write_ssd_call_count = 0
        self._read_ssd_call_count = 0

    def read_ssd(self, index):
        self._read_ssd_call_count += 1

    def write_ssd(self, lba, value):
        self._write_ssd_call_count += 1

    @property
    def read_ssd_call_count(self):
        return self._read_ssd_call_count

    @property
    def write_ssd_call_count(self):
        return self._write_ssd_call_count


@pytest.fixture
def shell_with_ssd_mock():
    testable_ssd = TestableSSD()
    shell = shell_ftn()
    shell.ssd = testable_ssd
    return shell



@pytest.mark.parametrize("index", [1, 3, 10, 4, -1, '20', 10.3, 100])
def test_read(mocker: MockerFixture, index):
    mock_read = mocker.patch('ssd.SSD.read_ssd')

    shell = shell_ftn()
    shell.read(index)

    mock_read.assert_called_with(index)



def test_write(mocker):
    # mk = shell_ftn()
    mk = mocker.patch.object(SSD(), 'write_ssd')
    mk.write(3, '0x00000000')
    mk.write(0, '0x00000000')
    mk.write(3, '0x03300000')
    mk.write(-1, '0x00000000')
    mk.write(100, '0x00000000')
    mk.write('3', '0x00000000')
    mk.write(3, '0x0000000011')
    mk.call_count == 7
    pass


def test_fullread(capsys, mocker):
    mk = mocker.patch('shell.shell_ftn.fullread')
    mk.return_value = "[Full Read]"
    shell = shell_ftn()
    print(shell.fullread())
    captured = capsys.readouterr()

    # assert
    assert captured.out == "[Full Read]\n"
    mk.call_count == 1


def test_fullwrite(capsys):
    test_shell = shell_ftn()
    # act
    test_shell.fullwrite(12341234)
    captured = capsys.readouterr()
    # mock_read_ssd = mocker.patch('shell.shell_ftn.fullwrite')
    # mock_read_ssd.side_effect = "[Full Write] Done"
    expected = "[Full Write] Done"

    assert captured.out == "[Full Write] Done\n"


def test_FullWriteAndReadCompare():
    test_shell = shell_ftn()
    # act
    assert test_shell.FullWriteAndReadCompare() == None


def test_PartialLBAWrite():
    shell = shell_ftn()
    assert shell.PartialLBAWrite()


def test_WriteReadAging_pass(mocker:MockerFixture, capsys):
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()

    # PASS 출력 검사
    assert 'PASS' in captured.out
    # 총 400번 호출되었는지
    assert mock_write_ssd.call_count == 400



def test_WriteReadAging_pass(mocker:MockerFixture, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.return_value = 10
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()
    #최종 반환값이 PASS인지 검증
    assert 'PASS' in captured.out
    assert mock_write_ssd.call_count == 400


def test_WriteReadAging_fail(mocker, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.side_effect = [10, 20]
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()
    assert 'FAIL' in captured.out
