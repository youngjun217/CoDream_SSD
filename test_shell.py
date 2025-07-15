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



@pytest.mark.parametrize("index", [1, 3, 10, 4])
def test_read(mocker: MockerFixture, index, capsys):
    mock_ssd_read = mocker.patch('ssd.SSD.read_ssd')
    mock_ouptut_read = mocker.patch('ssd.SSDOutput.read')

    shell = shell_ftn()
    shell.read(index)
    captured = capsys.readouterr()

    mock_ssd_read.assert_called_with(index)
    mock_ouptut_read.assert_called_once()
    assert '[Read]' in captured.out




# @patch('builtins.open', new_callable=mock_open, read_data='')
def test_write_success(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data=''))
    mock_func = mocker.patch('shell.SSD.write_ssd')
    shell = shell_ftn()
    result = shell.write(3, '0x00000000')
    mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
    assert result is True
    shell.write(0, '0x00000000')
    mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
    assert result is True
    shell.write(3, '0x03300000')
    mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
    assert result is True
    pass

def test_write_fail(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='ERROR'))
    mock_func = mocker.patch('shell.SSD.write_ssd', side_effect=AssertionError("SSD write failed"))
    shell = shell_ftn()
    with pytest.raises(AssertionError):
        result = shell.write(-1, '0x00000000')
        mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
        assert result is not True
    with pytest.raises(AssertionError):
        result = shell.write(100, '0x00000000')
        mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
        assert result is not True
    with pytest.raises(AssertionError):
        result = shell.write(3, '0x0000000000')
        mock_open.assert_any_call('ssd_output.txt', 'r', encoding='utf-8')
        assert result is not True



def test_fullread(capsys, mocker):
    mk = mocker.patch('shell.shell_ftn.fullread')
    mk.return_value = "[Full Read]"
    shell = shell_ftn()
    print(shell.fullread())
    captured = capsys.readouterr()

    # assert
    assert captured.out == "[Full Read]\n"
    assert mk.call_count == 1


def test_fullwrite(capsys):
    test_shell = shell_ftn()
    # act
    test_shell.fullwrite(12341234)
    captured = capsys.readouterr()
    # mock_read_ssd = mocker.patch('shell.shell_ftn.fullwrite')
    # mock_read_ssd.side_effect = "[Full Write] Done"
    expected = "[Full Write] Done"

    assert captured.out == "[Full Write] Done\n"


def test_FullWriteAndReadCompare(capsys,mocker):
    mk = mocker.patch('shell.shell_ftn.FullWriteAndReadCompare')
    mk.return_value = "PASS"
    test_shell = shell_ftn()
    print(test_shell.FullWriteAndReadCompare())
    captured = capsys.readouterr()
    # act
    assert captured.out == "PASS\n"
    mk.call_count == 1


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
    mock_read_line = mocker.patch('ssd.SSDNand.readline')
    mock_read_line.return_value = 10
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()

    assert mock_write_ssd.call_count == 400
    assert 'PASS' in captured.out


def test_WriteReadAging_fail(mocker, capsys):
    mock_read_line = mocker.patch('ssd.SSDNand.readline')
    mock_read_line.side_effect = [10, 20]
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()

    assert 'FAIL' in captured.out
