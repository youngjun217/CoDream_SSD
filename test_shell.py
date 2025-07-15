import pytest
from pytest_mock import MockerFixture
from unittest.mock import call

import ssd
from shell import shell_ftn
from ssd import SSD, SSDOutput


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


def test_write_fail(mocker):
    shell = shell_ftn()
    mocker.patch.object(ssd.SSD, 'write_ssd')
    mocker.patch.object(ssd.SSDOutput, 'read', return_value='ERROR')

    mock_print = mocker.patch('builtins.print')

    result = shell.write(10, '0xABCDEF12')

    mock_print.assert_not_called()
    assert result is False

def test_help_output(mocker):
    shell = shell_ftn()
    mock_print = mocker.patch('builtins.print')

    shell.help()
    mock_print.assert_called_once()
    printed_args = mock_print.call_args[0][0]

    assert '[Help]\n' in printed_args


def test_fullread_success(mocker):
    shell = shell_ftn()
    mock_read_ssd = mocker.patch.object(shell.ssd, 'read_ssd')
    mock_read_output = mocker.patch.object(shell.ssd_output, 'read')
    mock_print = mocker.patch('builtins.print')
    mock_read_output.return_value = "00000001 data_value"

    shell.fullread()

    assert mock_read_ssd.call_count == 100
    assert mock_read_output.call_count == 100

    mock_print.assert_any_call("[Full Read]")
    mock_print.assert_any_call("LBA 00000001 : data_value")

def test_fullread_with_errors(mocker):
    shell = shell_ftn()

    mocker.patch.object(shell.ssd, 'read_ssd')
    mocker.patch('builtins.print')
    mock_read_output = mocker.patch.object(shell.ssd_output, 'read')

    def side_effect():
        side_effect.counter += 1
        return "ERROR" if side_effect.counter <= 50 else "00000001 data_value"
    side_effect.counter = 0
    mock_read_output.side_effect = side_effect

    shell.fullread()

    assert mock_read_output.call_count == 100

def test_fullread_raises_exception(mocker):
    shell = shell_ftn()

    mocker.patch.object(shell.ssd, 'read_ssd', side_effect=ValueError("ERROR"))
    mocker.patch('builtins.print')

    with pytest.raises(ValueError, match="ERROR"):
        shell.fullread()

def test_fullwrite(capsys):
    test_shell = shell_ftn()

    test_shell.fullwrite(12341234)
    captured = capsys.readouterr()
    expected = "[Full Write] Done\n"

    assert captured.out == expected


def test_FullWriteAndReadCompare_pass(mocker):
    shell = shell_ftn()

    mocker.patch('random.randint', return_value=0x1A2B3C4D)
    # mocker.patch.object(shell.ssd, 'write_ssd')
    # mock_readline = mocker.patch.object(shell.ssd_nand,'readline',return_value="01 0x1A2B3C4D")

    mock_print = mocker.patch('builtins.print')
    shell.FullWriteAndReadCompare()

    mock_print.assert_called_with('PASS')

def test_FullWriteAndReadCompare_fail(mocker):
    shell   = shell_ftn()

    mocker.patch('random.randint', return_value=0x12345678)
    mocker.patch.object(shell.ssd, 'write_ssd')
    mock_reads = ["00 0x12345678","02 0x00000000"]
    mocker.patch.object(ssd.SSDNand, 'readline', side_effect=mock_reads)
    mock_print = mocker.patch('builtins.print')

    shell.FullWriteAndReadCompare()

    mock_print.assert_called_with('FAIL')

def test_PartialLBAWrite_pass(mocker):
    shell = shell_ftn()
    mocker.patch('random.randint', return_value=12345678)
    mock_write_ssd = mocker.patch.object(shell.ssd, 'write_ssd')
    mock_print = mocker.patch('builtins.print')
    result = shell.PartialLBAWrite()
    assert mock_write_ssd.call_count == 150
    mock_print.assert_called_with('PASS')


def test_PartialLBAWrite_fail(mocker):
    shell = shell_ftn()
    mocker.patch('random.randint', return_value=12345678)
    mocker.patch.object(shell.ssd, 'write_ssd')
    mock_reads = ["00 0x12345678", "02 0x00000000"]
    mocker.patch.object(ssd.SSDNand, 'readline', side_effect=mock_reads)
    mock_print = mocker.patch('builtins.print')
    result = shell.PartialLBAWrite()

    mock_print.assert_called_with('FAIL')
    assert result is None


def test_WriteReadAging_pass(mocker:MockerFixture, capsys):
    mock_read_line = mocker.patch('ssd.SSDNand.readline')
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()

    assert mock_write_ssd.call_count == 400
    assert 'PASS' in captured.out


def test_WriteReadAging_fail(mocker, capsys):
    mock_read_line = mocker.patch('ssd.SSDNand.readline')
    mock_read_line.side_effect = ['1 10', '2 20']
    mock_write_ssd = mocker.patch('ssd.SSD.write_ssd')

    shell = shell_ftn()
    shell.WriteReadAging()
    captured = capsys.readouterr()

    assert 'FAIL' in captured.out

def test_main_function_invaild_case(mocker):
    shell = shell_ftn()

    with pytest.raises(ValueError, match="INVALID COMMAND"):
        shell.main_function(['unknown', 'arg'])

def test_main_function_pass(mocker):
    shell = shell_ftn()

    # 내부 함수들을 모두 mock 처리
    mock_read = mocker.patch.object(shell, 'read')
    shell.main_function(['read', '10'])
    mock_read.assert_called_once_with(10)

def test_main(mocker):
    shell = shell_ftn()

    mocker.patch('builtins.input', side_effect=['read 10', 'exit'])
    mock_main_func = mocker.patch.object(shell, 'main_function')
    shell.main()

    mock_main_func.assert_called_once_with(['read', '10'])

