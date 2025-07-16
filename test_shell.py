import pytest
from pytest_mock import MockerFixture
from unittest.mock import call

import ssd
from shell import shell_ftn


@pytest.fixture
def shell():
    return shell_ftn()


@pytest.mark.parametrize("index", ['1 10', '2 20'])
def test_read(shell, mocker: MockerFixture, index):
    mock_read_ssd = mocker.patch.object(shell.ssd, 'read_ssd')
    mock_read_output = mocker.patch.object(shell.ssd_output, 'read', return_value=index)
    mock_print = mocker.patch('builtins.print')

    shell.read(index)

    mock_read_ssd.assert_called_with(index)
    mock_read_output.assert_called_once()
    mock_print.assert_called_once()


def test_write_success(shell, mocker):
    mocker.patch.object(ssd.SSD, 'write_ssd')
    mocker.patch.object(ssd.SSDOutput, 'read', return_value='')
    mock_print = mocker.patch('builtins.print')

    result = shell.write(3, '0x00000000')

    mock_print.assert_called_once()
    assert result is True


def test_write_fail(shell, mocker):
    mocker.patch.object(ssd.SSD, 'write_ssd')
    mocker.patch.object(ssd.SSDOutput, 'read', return_value='ERROR')
    mock_print = mocker.patch('builtins.print')
    result = shell.write(10, '0xABCDEF12')

    mock_print.assert_not_called()
    assert result is False


def test_erase(shell, mocker):

    shell.erase(3, 23)


def test_help_output(shell, mocker):
    mock_print = mocker.patch('builtins.print')

    shell.help()
    printed_args = mock_print.call_args[0][0]

    mock_print.assert_called_once()
    assert '[Help]\n' in printed_args


def test_fullread_success(shell, mocker):
    mock_read_ssd = mocker.patch.object(shell.ssd, 'read_ssd')
    mock_read_output = mocker.patch.object(shell.ssd_output, 'read')
    mock_print = mocker.patch('builtins.print')

    shell.fullread()

    assert mock_read_ssd.call_count == 100
    assert mock_read_output.call_count == 100
    mock_print.assert_any_call("[Full Read]")


@pytest.mark.parametrize('values', ['ERROR', '1 10'])
def test_fullread_with_errors(shell, mocker, values):
    mocker.patch.object(shell.ssd, 'read_ssd')
    mock_read_output = mocker.patch.object(shell.ssd_output, 'read', return_value=values)
    mocker.patch('builtins.print')

    shell.fullread()

    assert mock_read_output.call_count == 100


def test_fullread_raises_exception(shell, mocker):
    mocker.patch.object(shell.ssd, 'read_ssd', side_effect=ValueError("ERROR"))
    mocker.patch('builtins.print')

    with pytest.raises(ValueError, match="ERROR"):
        shell.fullread()


def test_fullwrite(shell, mocker):
    mock_write = mocker.patch.object(shell.ssd, 'write_ssd')
    mock_print = mocker.patch('builtins.print')
    shell.fullwrite(12341234)

    # expected = "[Full Write] Done\n"
    assert mock_write.call_count == 100
    mock_print.assert_called_once_with("[Full Write] Done")


def test_FullWriteAndReadCompare_pass(shell, mocker):
    mocker.patch('random.randint', return_value=0x1A2B3C4D)
    mock_print = mocker.patch('builtins.print')

    shell.FullWriteAndReadCompare()

    mock_print.assert_called_with('PASS')


@pytest.mark.parametrize('values', ['00 0x12345688', '02 0x00000000'])
def test_FullWriteAndReadCompare_fail(shell, mocker, values):
    mocker.patch('random.randint', return_value=0x12345678)
    mocker.patch.object(shell.ssd, 'write_ssd')
    mocker.patch.object(ssd.SSDNand, 'readline', return_value=values)
    mock_print = mocker.patch('builtins.print')

    shell.FullWriteAndReadCompare()

    mock_print.assert_called_with('FAIL')


def test_PartialLBAWrite_pass(shell, mocker):
    mocker.patch('random.randint', return_value=12345678)
    mock_write_ssd = mocker.patch.object(shell.ssd, 'write_ssd')
    mock_print = mocker.patch('builtins.print')
    shell.PartialLBAWrite()
    assert mock_write_ssd.call_count == 150
    mock_print.assert_called_with('PASS')

def test_PartialLBAWrite_fail(shell, mocker):
    mocker.patch('random.randint', return_value=12345678)
    mocker.patch.object(shell.ssd, 'write_ssd')
    mocker.patch.object(shell.ssd_nand, 'readline', side_effect=['00 0x12345678', '02 0x00000000'])
    mock_print = mocker.patch('builtins.print')
    result = shell.PartialLBAWrite()

    mock_print.assert_called_with('FAIL')
    assert result is None


def test_WriteReadAging_pass(shell, mocker: MockerFixture):
    mock_read_line = mocker.patch.object(shell.ssd_nand, 'readline')
    mock_write_ssd = mocker.patch.object(shell.ssd, 'write_ssd')
    mock_print = mocker.patch('builtins.print')

    shell.WriteReadAging()

    assert mock_read_line.call_count == 400
    assert mock_write_ssd.call_count == 400
    mock_print.assert_called_with('PASS')


def test_WriteReadAging_fail(shell, mocker):
    mock_read_line = mocker.patch.object(shell.ssd_nand, 'readline', side_effect=['1 10', '2 20'])
    mock_print = mocker.patch('builtins.print')

    shell.WriteReadAging()

    mock_print.assert_called_with('FAIL')


def test_main_function_invaild_case(shell):
    with pytest.raises(ValueError, match="INVALID COMMAND"):
        shell.main_function(['unknown', 'arg'])


def test_main_function_pass(shell, mocker):
    mock_read = mocker.patch.object(shell, 'read')

    shell.main_function(['read', '10'])

    mock_read.assert_called_once_with(10)


def test_main(shell, mocker):
    mocker.patch('builtins.input', side_effect=['read 10', 'exit'])
    mock_main_func = mocker.patch.object(shell, 'main_function')

    shell.main()

    mock_main_func.assert_called_once_with(['read', '10'])
