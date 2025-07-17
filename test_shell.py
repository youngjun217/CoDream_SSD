from datetime import datetime

import pytest
from unittest.mock import call
import unittest
from unittest import  mock
from shell import *


class Test_shell:
    @pytest.fixture(autouse=True)
    def setup_shell(self,mocker):
        self.shell=Shell()
        self.read_output = mocker.patch.object(self.shell.ssd_output, 'read')
        self.nand_readline = mocker.patch.object(self.shell.ssd_nand, 'readline')
        self.mock_print = mocker.patch('builtins.print')
        self.rand_num = mocker.patch('random.randint', return_value=12345678)
        self.shell._send_command = mocker.Mock()


    def test_read(self):
        #Act
        cmd = ReadCommand(self.shell, 1)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_args_list == [(('R', 1),)]
        self.read_output.assert_called_once()


    def test_write_success(self, setup_shell):
        self.read_output.return_value=''
        #Act
        cmd = WriteCommand(self.shell, idx=5, value=0xDEADBEEF)
        result = cmd.execute()
        #Assert
        assert result is True
        self.shell._send_command.assert_called_once_with('W', 5, 0xDEADBEEF)


    def test_write_fail(self, setup_shell):
        self.read_output.return_value='ERROR'
        #Act
        cmd = WriteCommand(self.shell, idx=5, value=0xCAFEBABE)
        result = cmd.execute()
        #Assert
        self.mock_print.assert_not_called()
        assert result is False


    def test_erase_success(self, setup_shell):
        expected_calls = [call('E',2, 10), call('E',12, 10), call('E',22, 5)]
        #Act
        cmd = EraseCommand(self.shell, lba=2, size=25)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_args_list == expected_calls
        assert self.shell._send_command.call_count==3


    def test_erase_fail(self, setup_shell):
        #Act
        cmd = EraseCommand(self.shell, lba=-1, size=25)
        #Assert
        with pytest.raises(Exception):
            cmd.execute()


    def test_erase_range_success(self, setup_shell):
        expected_calls = [call('E',3, 10), call('E',13, 8)]
        #Act
        cmd = EraseRangeCommand(self.shell, st_lba=3, en_lba=20)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_args_list == expected_calls
        assert self.shell._send_command.call_count==2


    def test_help_output(self, setup_shell):
        #Act
        self.shell.help()
        #Assert
        printed_args = self.mock_print.call_args[0][0]
        self.mock_print.assert_called_once()
        assert '[Help]\n' in printed_args


    def test_fullread_success(self, setup_shell):
        #Act
        cmd = FullReadCommand(self.shell)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_count == 100
        self.mock_print.assert_any_call("[Full Read]")


    @pytest.mark.parametrize('values', ['ERROR', '1 10'])
    def test_fullread_with_errors(self, setup_shell, values):
        self.read_output.return_value=values
        #Act
        cmd = FullReadCommand(self.shell)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_count == 100


    def test_fullread_raises_exception(self, setup_shell):
        self.read_output.side_effect=ValueError("ERROR")
        #Act & #Assert
        cmd = FullReadCommand(self.shell)
        with pytest.raises(ValueError, match="ERROR"):
            cmd.execute()


    def test_fullwrite(self, setup_shell):
        #Act
        cmd = FullWriteCommand(self.shell,value=12341234)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_count == 100
        self.mock_print.assert_called_once_with("[Full Write] Done")


    def test_FullWriteAndReadCompare_pass(self, setup_shell,mocker):
        mocker.patch('random.randint', side_effect=([0xAABBCCDD] * 100))
        self.nand_readline.side_effect = lambda idx: f"{idx} 0xAABBCCDD"
        #Act
        cmd = FullWriteAndReadCompareCommand(self.shell)
        cmd.execute()
        #Assert
        self.mock_print.assert_any_call('PASS')


    @pytest.mark.parametrize('values', ['00 0x12345688', '02 0x00000000'])
    def test_FullWriteAndReadCompare_fail(self, setup_shell, values):
        self.nand_readline.return_value=values
        #Act
        cmd = FullWriteAndReadCompareCommand(self.shell)
        cmd.execute()
        #Assert
        self.mock_print.assert_called_with('FAIL')


    def test_PartialLBAWrite_pass(self, setup_shell):
        #Act
        cmd = PartialLBAWriteCommand(self.shell)
        cmd.execute()
        #Assert
        assert self.shell._send_command.call_count == 150
        self.mock_print.assert_called_with('PASS')

    def test_PartialLBAWrite_fail(self, setup_shell):
        self.nand_readline.side_effect=['00 0x12345678', '02 0x00000000']
        #Act
        cmd = PartialLBAWriteCommand(self.shell)
        result = cmd.execute()
        #Assert
        self.mock_print.assert_called_with('FAIL')
        assert result is None


    def test_WriteReadAging_pass(self, setup_shell):
        #Act
        cmd = WriteReadAgingCommand(self.shell)
        cmd.execute()

        #Assert
        assert self.nand_readline.call_count == 400
        assert self.shell._send_command.call_count == 400
        self.mock_print.assert_called_with('PASS')


    def test_WriteReadAging_fail(self, setup_shell):
        self.nand_readline.side_effect=['1 10', '2 20']
        #Act
        cmd = WriteReadAgingCommand(self.shell)
        cmd.execute()
        #Assert
        self.mock_print.assert_called_with('FAIL')


    def test_EraseAndWriteAging_pass(self, setup_shell, mocker):
        mocker.patch.object(EraseRangeCommand, 'execute', return_value=None)
        #Act
        cmd = EraseAndWriteAgingCommand(self.shell)
        cmd.execute()
        #Assert
        self.mock_print.assert_called_with('PASS')


    def test_EraseAndWriteAging_fail(self, setup_shell,mocker):
        mocker.patch.object(EraseRangeCommand, 'execute', side_effect=RuntimeError())
        # Act & Assert
        cmd = EraseAndWriteAgingCommand(self.shell)
        with pytest.raises(Exception):
            cmd.execute()


    def test_main_function_invaild_case(self, setup_shell):
        # Act & Assert
        with pytest.raises(ValueError, match="INVALID COMMAND"):
            self.shell.main_function(['unknown', 'arg'])


    def test_main_function_pass(self, setup_shell):
        #Act
        self.shell.main_function(['read', '10'])
        #Assert
        self.shell._send_command.assert_called_once_with('R', 10)


    def test_main(self, setup_shell,mocker):
        mocker.patch('builtins.input', side_effect=['read 10', 'exit'])
        mock_main_func = mocker.patch.object(self.shell, 'main_function')
        #Act
        self.shell.main()
        #Assert
        mock_main_func.assert_called_once_with(['read', '10'])

    def test_option_main_file_not_found(self, setup_shell):
        #Act
        self.shell.option_main("non_existing_file.txt")
        #Assert
        self.mock_print.assert_called_with('ERROR')


    def test_option_main_pass(self,setup_shell,mocker, tmp_path):
        test_file = tmp_path / "commands.txt"
        test_file.write_text("1_testCommand\n")
        mock_command_dict = {('1_', 1): lambda: print("PASS")}
        mocker.patch.object(self.shell, "command_dictionary", return_value=mock_command_dict)
        #Act
        self.shell.option_main(str(test_file))
        #Assert
        printed_args = [" ".join(str(arg) for arg in call.args) for call in self.mock_print.call_args_list]
        assert any("___   Run..." in line for line in printed_args)
        assert any("PASS" in line for line in printed_args)

    def test_option_main_fail(self,setup_shell,mocker, tmp_path):
        path = tmp_path / "test.txt"
        path.write_text("02_failcase\n")
        #Act
        self.shell.option_main("non_existing_file.txt")
        #Assert
        self.mock_print.assert_called_with('ERROR')


class Test_logger():

    # @pytest.fixture
    # def setup_logger(self, mocker):
    #      # 싱글톤 초기화
    #     Logger._instance = None
    #     self._logger = Logger()
    #     self.mock_open = mocker.patch("builtins.open", mocker.mock_open())

    def test_singleton(self):
        logger1 = Logger()
        logger2 = Logger()
        assert logger1 is logger2

    def test_logger_init_removes_log_file(self, mocker):
        mock_exists = mocker.patch("os.path.exists", return_value=True)
        mock_remove = mocker.patch("os.remove")

        logger = Logger()
        assert logger._initialized is True
        mock_exists.assert_called_once_with(Logger.LOG_FILE)
        mock_remove.assert_called_once_with(Logger.LOG_FILE)

    def test_print_calls_rotate_and_writes(self,mocker):
        logger = Logger()
        mock_rotate = mocker.patch.object(logger, "rotate_log_if_needed")
        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        fake_now = datetime.datetime(2025, 7, 16, 15, 0)
        mocker.patch("datetime.datetime", mocker.Mock(now=lambda: fake_now))
        logger.print("HEADER", "message")

        mock_rotate.assert_called_once()
        mock_open.assert_called_once_with("latest.log", 'a', encoding='utf-8')

        handle = mock_open()
        written_text = handle.write.call_args[0][0]

        assert "HEADER" in written_text
        assert "message" in written_text


    def test_rotate_log_if_needed_renames(self,mocker):
        logger = Logger()
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.path.getsize", return_value=Logger.MAX_SIZE + 1)
        mocker.patch("glob.glob", return_value=["until_250708_17h_12m_52s.log"])
        mock_rename = mocker.patch("os.rename")
        mocker.patch("time.strftime", return_value="until_250710_09h_00m_00s")

        logger.rotate_log_if_needed()

        assert mock_rename.call_count == 2

        calls = mock_rename.call_args_list
        assert calls[0][0][0].endswith(".log")
        assert calls[0][0][1].endswith(".zip")
        assert calls[1][0][0] == Logger.LOG_FILE
        assert calls[1][0][1].startswith("until_")
        assert calls[1][0][1].endswith(".log")

    def test_erase_logger_fail(self,mocker):
        shell=Shell()
        mock_logger = mocker.Mock()
        shell.logger = mock_logger
        cmd=EraseCommand(shell, lba=-1, size=20)


        # 실패 조건: LBA < 0
        with pytest.raises(Exception):
            cmd.execute()

        # logger.print가 "FAIL"로 호출됐는지 확인
        mock_logger.print.assert_called_once()


