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
    return shell_ftn(testable_ssd)


def test_read_success(mocker):
    mock_read_ssd = mocker.patch('shell.shell_ftn.read')
    mock_read_ssd.side_effect = [1,2,3]

    shell= shell_ftn()
    assert shell.read(0) == 1
    assert shell.read(1) == 2
    assert shell.read(2) == 3

def test_read_fail(mocker):
    mock_read_ssd = mocker.patch('shell.shell_ftn.read')
    mock_read_ssd.side_effect = ValueError('ERROR')

    shell= shell_ftn()
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(100)
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(10.1)

def test_write( mocker):
    # mk = shell_ftn()
    mk = mocker.patch.object(SSD(),'write_ssd')
    mk.write(3, '0x00000000')
    mk.write(0, '0x00000000')
    mk.write(3, '0x03300000')
    mk.write(-1, '0x00000000')
    mk.write(100, '0x00000000')
    mk.write('3', '0x00000000')
    mk.write(3, '0x0000000011')
    mk.call_count == 7
    pass

def test_fullread(capsys):
    shell = shell_ftn()
    shell.fullread()
    captured = capsys.readouterr()

    assert captured.out.split('\n')[0]=="[Full Read]"


def test_fullwrite(capsys):
    test_shell=shell_ftn()
    # act
    test_shell.fullwrite(12341234)
    captured = capsys.readouterr()
    # mock_read_ssd = mocker.patch('shell.shell_ftn.fullwrite')
    # mock_read_ssd.side_effect = "[Full Write] Done"
    expected = "[Full Write] Done"

    assert captured.out=="[Full Write] Done\n"

def test_FullWriteAndReadCompare():
    test_shell = shell_ftn()
    # act
    assert test_shell.FullWriteAndReadCompare()==None

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
    mock_read_line.side_effect=[10,20]
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging('ssd_nand.txt')
    captured = capsys.readouterr()
    assert 'FAIL' in captured.out