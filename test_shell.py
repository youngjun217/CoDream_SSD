import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from shell import shell_ftn
from ssd import SSD


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


def test_read_success(mocker):
    mock_read_ssd = mocker.patch('shell.shell_ftn.read')
    mock_read_ssd.side_effect = [1, 2, 3]


def test_read(mocker):
    shell = shell_ftn()
    index = 0
    fake_data = "10"
    m = mocker.mock_open(read_data=fake_data)

    # open("ssd_nand.txt") 를 호출할 때 가짜 파일이 열리게 함
    mocker.patch("builtins.open", m)
    shell.read(index)

    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        ssd_nand_txt = file.read()
    lines = ssd_nand_txt.splitlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    assert lines[index] == ssd_output_txt


@pytest.mark.parametrize("lst", [100, 10.3, '20'])
def test_read_fail(lst):
    index = lst
    shell = shell_ftn()

    with pytest.raises(ValueError, match="ERROR"):
        shell.read(index)


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


def test_WriteReadAging_pass(mocker, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.return_value = 10
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging('ssd_nand.txt')
    captured = capsys.readouterr()
    assert 'PASS' in captured.out


def test_WriteReadAging_fail(mocker, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.side_effect = [10, 20]
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging('ssd_nand.txt')
    captured = capsys.readouterr()
    assert 'FAIL' in captured.out
