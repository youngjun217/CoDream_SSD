import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from shell import shell_ftn

def test_read_success(mocker):
    mock_read_ssd = mocker.patch('ssd.read_ssd')
    mock_read_ssd.side_effect = [1,2,3,ValueError]

    shell= shell_ftn()
    assert shell.read(0) == 1
    assert shell.read(1) == 2
    assert shell.read(2) == 3

def test_read_fail(mocker):
    mock_read_ssd = mocker.patch('ssd.read_ssd')
    mock_read_ssd.side_effect = [1,2,3,ValueError]

    shell= shell_ftn()
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(100)
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(10.1)

def test_write( mocker):
    shell = shell_ftn()
    mk = mocker.patch('ssd.write')
    shell.write(3, '0x00000000')
    shell.write(0, '0x00000000')
    shell.write(3, '0x03300000')
    with pytest.raises(AssertionError):
        shell.write(-1, '0x00000000')
        shell.write(100, '0x00000000')
        shell.write('3', '0x00000000')
        shell.write(3, '0x0000000011')
    mk.call_count == 7
    pass


def test_WriteReadAging_pass(mocker, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.return_value = 10

    shell = shell_ftn()
    shell.WriteReadAging('ssd_nand.txt')
    captured = capsys.readouterr()
    assert 'PASS' in captured.out

def test_WriteReadAging_fail(mocker, capsys):
    mock_read_line = mocker.patch('shell.shell_ftn._read_line')
    mock_read_line.side_effect=[10,20]

    shell = shell_ftn()
    shell.WriteReadAging('ssd_nand.txt')
    captured = capsys.readouterr()
    assert 'FAIL' in captured.out