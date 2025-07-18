from datetime import datetime

import pytest
from unittest.mock import call, MagicMock, patch
import unittest
from unittest import mock
from shell import *


class Test_shell:
    @pytest.fixture
    def setup_shell(self, mocker):
        self.shell = Shell()
        self.get_response = mocker.patch.object(self.shell, 'get_response')
        self.get_response_value = mocker.patch.object(self.shell, 'get_response_value')
        self.mock_print = mocker.patch('builtins.print')
        self.rand_num = mocker.patch('random.randint', return_value=12345678)
        self.shell.send_command = mocker.Mock()

    @pytest.fixture
    def setup_ssdinterface(self, mocker):
        self.shell = Shell()
        self.shell.ssd_interface = mocker.Mock()

    @pytest.mark.parametrize('command', ['E', 'W', 'R', 'F'])
    def test_send_command(self, setup_ssdinterface, command):
        self.shell.ssd_interface.run.return_value = 'OK'
        result = self.shell.send_command(command, 10, 10)

        self.shell.ssd_interface.run.assert_called_once()
        assert result == 'OK'

    def test_response(self, setup_ssdinterface):
        self.shell.ssd_interface.get_response.return_value = 'RESPONSE'
        assert self.shell.get_response() == 'RESPONSE'
        self.shell.ssd_interface.get_response.assert_called_once()

    @pytest.mark.parametrize('values,result', [('01 0xDEADBEEF', '0xDEADBEEF'), ('ERROR', 'ERROR')])
    def test_getresponsevalue(self, setup_ssdinterface, values, result):
        self.shell.ssd_interface.get_response.return_value = values
        assert self.shell.get_response_value() == result

    def test_read(self, setup_shell):
        # Act
        ShellReadCommand(self.shell, 1).execute()
        # Assert
        assert self.shell.send_command.call_count == 1
        self.get_response_value.assert_called_once()

    def test_write_success(self, setup_shell):
        self.get_response_value.return_value = ''
        # Act
        result = ShellWriteCommand(self.shell, lba=5, value=0xDEADBEEF).execute()
        # Assert
        assert result is True
        self.shell.send_command.assert_called_once_with('W', 5, 0xDEADBEEF)

    def test_write_fail(self, setup_shell):
        self.get_response_value.return_value = 'ERROR'
        # Act
        result = ShellWriteCommand(self.shell, lba=5, value=0xCAFEBABE).execute()
        # Assert
        self.mock_print.assert_not_called()
        assert result is False

    def test_erase_success(self, setup_shell):
        expected_calls = [call('E', 2, 10), call('E', 12, 10), call('E', 22, 5)]
        # Act
        ShellEraseCommand(self.shell, st_lba=2, erase_size=25).execute()
        # Assert
        assert self.shell.send_command.call_args_list == expected_calls
        assert self.shell.send_command.call_count == 3

    def test_erase_fail(self, setup_shell):
        # Act & Assert
        with pytest.raises(Exception):
            ShellEraseCommand(self.shell, st_lba=-1, erase_size=25).execute()

    def test_erase_range_success(self, setup_shell):
        # Act
        ShellEraseRangeCommand(self.shell, st_lba=3, en_lba=20).execute()
        # Assert
        assert self.shell.send_command.call_args_list == [call('E', 3, 10), call('E', 13, 8)]
        assert self.shell.send_command.call_count == 2

    def test_erase_range_fail(self, setup_shell):
        # Act & Assert
        with pytest.raises(ValueError):
            ShellEraseRangeCommand(self.shell, st_lba=-1, en_lba=25).execute()

    def test_help_output(self, setup_shell):
        # Act
        ShellHelpCommand(self.shell).execute()
        # Assert
        assert '[Help]\n' in self.mock_print.call_args[0][0]


    def test_fullread_success(self, setup_shell):
        # Act
        ShellFullReadCommand(self.shell).execute()
        # Assert
        assert self.shell.send_command.call_count == 100
        self.mock_print.assert_any_call("[Full Read]")

    @pytest.mark.parametrize('values', ['ERROR'])
    def test_fullread_errors(self, setup_shell, values):
        self.get_response_value.return_value = values
        # Act
        ShellFullReadCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_any_call("ERROR")

    def test_fullread_raises_exception(self, setup_shell):
        self.get_response_value.side_effect = ValueError("ERROR")
        # Act & #Assert
        with pytest.raises(ValueError, match="ERROR"):
            ShellFullReadCommand(self.shell).execute()

    def test_fullwrite(self, setup_shell):
        # Act
        ShellFullWriteCommand(self.shell, value=12341234).execute()
        # Assert
        assert self.shell.send_command.call_count == 100
        self.mock_print.assert_called_once_with("[Full Write] Done")

    def test_FullWriteAndReadCompare_pass(self, setup_shell):
        self.rand_num.side_effect = ([0xAABBCCDD] * 100)
        self.get_response_value.return_value = '0xAABBCCDD'
        # Act
        ShellFullWriteAndReadCompareCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_any_call('PASS')

    @pytest.mark.parametrize('values', ['00 0x12345688', '02 0x00000000'])
    def test_FullWriteAndReadCompare_fail(self, setup_shell, values):
        self.get_response_value.return_value = values
        # Act
        ShellFullWriteAndReadCompareCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_called_with('FAIL')

    def test_PartialLBAWrite_pass(self, setup_shell):
        # Act
        ShellPartialLBAWriteCommand(self.shell).execute()
        # Assert
        assert self.shell.send_command.call_count == 300
        self.mock_print.assert_called_with('PASS')

    def test_PartialLBAWrite_fail(self, setup_shell):
        self.get_response_value.side_effect = ['00 0x12345678', '02 0x00000000']
        # Act
        result = ShellPartialLBAWriteCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_called_with('FAIL')
        assert result is None

    def test_WriteReadAging_pass(self, setup_shell):
        # Act
        ShellWriteReadAgingCommand(self.shell).execute()
        # Assert
        assert self.get_response_value.call_count == 400
        self.mock_print.assert_called_with('PASS')

    def test_WriteReadAging_fail(self, setup_shell):
        self.get_response_value.side_effect = ['1 10', '2 20']
        # Act
        ShellWriteReadAgingCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_called_with('FAIL')

    def test_EraseAndWriteAging_pass(self, setup_shell, mocker):
        mocker.patch.object(ShellEraseRangeCommand, 'execute', return_value=None)
        # Act
        ShellEraseAndWriteAgingCommand(self.shell).execute()
        # Assert
        self.mock_print.assert_called_with('PASS')

    def test_EraseAndWriteAging_fail(self, setup_shell, mocker):
        mocker.patch.object(ShellEraseRangeCommand, 'execute', side_effect=RuntimeError())
        # Act & Assert
        with pytest.raises(Exception):
            ShellEraseAndWriteAgingCommand(self.shell).execute()


    def test_Flush(self, setup_shell):
        # Act
        ShellFlushCommand(self.shell).execute()
        # Assert
        assert self.shell.send_command.call_count == 1

    def test_main_function_invaild_case(self, setup_shell):
        # Act & Assert
        with pytest.raises(ValueError, match="INVALID COMMAND"):
            self.shell.main_function(['unknown', 'arg'])

    def test_main_function_pass(self, setup_shell):
        # Act
        self.shell.main_function(['read', '10'])
        # Assert
        self.shell.send_command.assert_called_once_with('R', 10)

    def test_main(self, setup_shell, mocker):
        mocker.patch('builtins.input', side_effect=['read 10', 'exit'])
        mock_main_func = mocker.patch.object(self.shell, 'main_function')
        # Act
        self.shell.main()
        # Assert
        mock_main_func.assert_called_once_with(['read', '10'])

    def test_option_main_file_not_found(self, setup_shell):
        # Act
        self.shell.option_main("non_existing_file.txt")
        # Assert
        self.mock_print.assert_called_with('ERROR')

    def test_option_main_pass(self, setup_shell, mocker, tmp_path):
        test_file = tmp_path / "commands.txt"
        test_file.write_text("1_testCommand\n")
        mock_command_dict = {('1_', 1): lambda: print("PASS")}
        mocker.patch.object(self.shell, "command_dictionary", return_value=mock_command_dict)
        # Act
        self.shell.option_main(str(test_file))
        # Assert
        printed_args = [" ".join(str(arg) for arg in call.args) for call in self.mock_print.call_args_list]
        assert any("___   Run..." in line for line in printed_args)
        assert any("PASS" in line for line in printed_args)

    def test_option_main_fail(self, setup_shell, mocker, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("02_failcase\n")
        # Act
        self.shell.option_main("non_existing_file.txt")
        # Assert
        self.mock_print.assert_called_with('ERROR')

    @patch('ssd.SSD.run')
    def test_SSDConcreteInterface_run(self, mock_ssd_run):
        shell = Shell()
        shell.send_command('R', 1)
        assert mock_ssd_run.call_count == 1

    @patch('ssd_texts.SSDOutput.read')
    def test_SSDConcreteInterface_get_response(self, mock_ssd_output_read):
        shell = Shell()
        shell.get_response()
        assert mock_ssd_output_read.call_count == 1


class Test_logger():

    @pytest.fixture
    def setup_logger(self):
        self.logger = Logger()

    def test_init_logger(self, setup_logger):
        assert self.logger._initialized is True

    def test_print_calls_rotate_and_writes(self, setup_logger,mocker):
        mock_rotate = mocker.patch.object(self.logger, "rotate_log_if_needed")
        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        fake_now = datetime.datetime(2025, 7, 16, 15, 0)
        mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fake_now))
        self.logger.print("HEADER", "message")

        mock_rotate.assert_called_once()
        mock_open.assert_called_once_with("latest.log", 'a', encoding='utf-8')

        handle = mock_open()
        written_text = handle.write.call_args[0][0]
        assert "HEADER" in written_text
        assert "message" in written_text

    def test_rotate_log_if_needed_renames(self, setup_logger, mocker):
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.path.getsize", return_value=Logger.MAX_SIZE + 1)
        mocker.patch("glob.glob", return_value=["until_250708_17h_12m_52s.log"])
        mock_rename = mocker.patch("os.rename")
        mocker.patch("time.strftime", return_value="until_250710_09h_00m_00s")

        self.logger.rotate_log_if_needed()

        assert mock_rename.call_count == 2

        calls = mock_rename.call_args_list
        assert calls[0][0][0].endswith(".log")
        assert calls[0][0][1].endswith(".zip")
        assert calls[1][0][0] == Logger.LOG_FILE
        assert calls[1][0][1].startswith("until_")
        assert calls[1][0][1].endswith(".log")

