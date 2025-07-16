import contextlib
from io import StringIO

import pytest
from pytest_mock import MockerFixture
from unittest.mock import call

import ssd
from shell import Shell, Logger


@pytest.fixture
def shell():
    return Shell()


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

def test_erase_success(shell, mocker):
    mock_erase_ssd = mocker.patch.object(ssd.SSD, 'erase_ssd')

    shell.erase(2,25)

    expected_calls = [call(2, 10), call(12, 10), call(22, 5)]

    assert mock_erase_ssd.call_args_list == expected_calls
    assert mock_erase_ssd.call_count==3


def test_erase_fail(shell):
    with pytest.raises(ValueError, match="Invalid LBA range or SIZE"):
        shell.erase(-1,25)


def test_erase_range_success(shell, mocker):
    mock_erase_ssd = mocker.patch.object(ssd.SSD, 'erase_ssd')

    shell.erase_range(3,20)

    expected_calls = [call(3, 10), call(13, 8)]

    assert mock_erase_ssd.call_args_list == expected_calls
    assert mock_erase_ssd.call_count==2


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

def test_option_main_file_not_found(shell,mocker):
    mock_print = mocker.patch("builtins.print")

    shell.option_main("non_existing_file.txt")

    mock_print.assert_called_with('ERROR')


def test_option_main_pass_with_mocked_print(shell,mocker, tmp_path):
    test_file = tmp_path / "commands.txt"
    test_file.write_text("1_testCommand\n")

    mock_command_dict = {('1_', 1): lambda: print("PASS")}
    mocker.patch.object(shell, "command_dictionary", return_value=mock_command_dict)
    mock_print = mocker.patch("builtins.print")

    shell.option_main(str(test_file))

    printed_args = [" ".join(str(arg) for arg in call.args) for call in mock_print.call_args_list]

    assert any("___   Run..." in line for line in printed_args)
    assert any("PASS" in line for line in printed_args)

def test_option_main_fail(shell,mocker, tmp_path):
    path = tmp_path / "test.txt"
    path.write_text("02_failcase\n")

    mock_print = mocker.patch("builtins.print")

    shell.option_main("non_existing_file.txt")

    mock_print.assert_called_with('ERROR')


@pytest.fixture
def logger():
    Logger._instance = None  # 싱글톤 초기화
    return Logger()

def test_init_removes_log_file_if_exists(mocker):
    mock_exists = mocker.patch("os.path.exists", return_value=True)
    mock_remove = mocker.patch("os.remove")
    Logger._instance = None
    logger = Logger()
    mock_exists.assert_called_once_with(Logger.LOG_FILE)
    mock_remove.assert_called_once_with(Logger.LOG_FILE)

def test_print_calls_rotate_and_writes(mocker, logger):
    mock_rotate = mocker.patch.object(logger, "rotate_log_if_needed")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())
    logger.print("HEADER", "message")
    mock_rotate.assert_called_once()
    mock_open.assert_called_once_with("latest.log", 'a', encoding='utf-8')
    handle = mock_open()
    written_text = handle.write.call_args[0][0]

    # 날짜, 시간 정보는 변화가 많으니 제외하고 확인
    assert "HEADER" in written_text
    assert "message" in written_text
    assert written_text.endswith("\n")

def test_rotate_log_if_needed_renames(mocker, logger):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.path.getsize", return_value=Logger.MAX_SIZE + 1)
    mocker.patch("glob.glob", return_value=["until_250708_17h_12m_52s.log"])
    mock_rename = mocker.patch("os.rename")
    mocker.patch("time.strftime", return_value="until_250710_09h_00m_00s")

    logger.rotate_log_if_needed()

    assert mock_rename.call_count == 2
    calls = mock_rename.call_args_list
    # 첫 호출: 기존 until 파일 .log -> .zip
    assert calls[0][0][0].endswith(".log")
    assert calls[0][0][1].endswith(".zip")
    # 두번째 호출: latest.log -> 새로운 until 파일명
    assert calls[1][0][0] == Logger.LOG_FILE
    assert calls[1][0][1].startswith("until_")
    assert calls[1][0][1].endswith(".log")


