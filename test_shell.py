import pytest
from pytest_mock import MockerFixture
from unittest.mock import call

from shell import Shell, Logger


class Test_shell():
    @pytest.fixture
    def setup_shell(self, mocker):
        self.shell=Shell()
        self.read_ssd = mocker.patch.object(self.shell.ssd, 'read_ssd')
        self.write_ssd = mocker.patch.object(self.shell.ssd, 'write_ssd')
        self.erase_ssd = mocker.patch.object(self.shell.ssd, 'erase_ssd')
        self.read_output = mocker.patch.object(self.shell.ssd_output, 'read')
        self.nand_readline = mocker.patch.object(self.shell.ssd_nand, 'readline')
        self.mock_print = mocker.patch('builtins.print')
        self.rand_num = mocker.patch('random.randint', return_value=12345678)


    @pytest.mark.parametrize("index, output", [(1, '1 10'), (2, '2 20')])
    def test_read(self, setup_shell, index, output):
        self.read_output.return_value=output
        #Act
        self.shell.read(index)
        #Assert
        self.read_ssd.assert_called_with(index)
        self.read_output.assert_called_once()


    def test_write_success(self, setup_shell):
        self.read_output.return_value=''
        #Act
        result = self.shell.write(3, '0x00000000')
        #Assert
        self.mock_print.assert_called_once()
        assert result is True


    def test_write_fail(self, setup_shell):
        self.read_output.return_value='ERROR'
        #Act
        result = self.shell.write(10, '0xABCDEF12')
        #Assert
        self.mock_print.assert_not_called()
        assert result is False


    def test_erase_success(self, setup_shell):
        expected_calls = [call(2, 10), call(12, 10), call(22, 5)]
        #Act
        self.shell.erase(2,25)
        #Assert
        assert self.erase_ssd.call_args_list == expected_calls
        assert self.erase_ssd.call_count==3


    def test_erase_fail(self, setup_shell):
        #Act & Assert
        with pytest.raises(ValueError):
            self.shell.erase_range(-1,25)


    def test_erase_range_success(self, setup_shell):
        expected_calls = [call(3, 10), call(13, 8)]
        #Act
        self.shell.erase_range(3,20)
        #Assert
        assert self.erase_ssd.call_args_list == expected_calls
        assert self.erase_ssd.call_count==2


    def test_help_output(self, setup_shell):
        #Act
        self.shell.help()
        #Assert
        printed_args = self.mock_print.call_args[0][0]
        self.mock_print.assert_called_once()
        assert '[Help]\n' in printed_args


    def test_fullread_success(self, setup_shell):
        #Act
        self.shell.fullread()
        #Assert
        assert self.read_ssd.call_count == 100
        assert self.read_output.call_count == 100
        self.mock_print.assert_any_call("[Full Read]")


    @pytest.mark.parametrize('values', ['ERROR', '1 10'])
    def test_fullread_with_errors(self, setup_shell, values):
        self.read_output.return_value=values
        #Act
        self.shell.fullread()
        #Assert
        assert self.read_output.call_count == 100


    def test_fullread_raises_exception(self, setup_shell):
        self.read_output.side_effect=ValueError("ERROR")
        #Act & #Assert
        with pytest.raises(ValueError, match="ERROR"):
            self.shell.fullread()


    def test_fullwrite(self, setup_shell):
        #Act
        self.shell.fullwrite(12341234)
        #Assert
        assert self.write_ssd.call_count == 100
        self.mock_print.assert_called_once_with("[Full Write] Done")


    def test_FullWriteAndReadCompare_pass(self, mocker):
        mocker.patch('random.randint', return_value=12345678)
        mock_print = mocker.patch('builtins.print')
        #Act
        Shell().FullWriteAndReadCompare()
        #Assert
        mock_print.assert_called_with('PASS')


    @pytest.mark.parametrize('values', ['00 0x12345688', '02 0x00000000'])
    def test_FullWriteAndReadCompare_fail(self, setup_shell, values):
        self.nand_readline.return_value=values
        #Act
        self.shell.FullWriteAndReadCompare()
        #Assert
        self.mock_print.assert_called_with('FAIL')


    def test_PartialLBAWrite_pass(self, setup_shell):
        #Act
        self.shell.PartialLBAWrite()
        #Assert
        assert self.write_ssd.call_count == 150
        self.mock_print.assert_called_with('PASS')

    def test_PartialLBAWrite_fail(self, setup_shell):
        self.nand_readline.side_effect=['00 0x12345678', '02 0x00000000']
        #Act
        result = self.shell.PartialLBAWrite()
        #Assert
        self.mock_print.assert_called_with('FAIL')
        assert result is None


    def test_WriteReadAging_pass(self, setup_shell):
        #Act
        self.shell.WriteReadAging()
        #Assert
        assert self.nand_readline.call_count == 400
        assert self.write_ssd.call_count == 400
        self.mock_print.assert_called_with('PASS')


    def test_WriteReadAging_fail(self, setup_shell):
        self.nand_readline.side_effect=['1 10', '2 20']
        #Act
        self.shell.WriteReadAging()
        #Assert
        self.mock_print.assert_called_with('FAIL')


    def test_EraseAndWriteAging_pass(self, setup_shell):
        #Act
        self.shell.EraseAndWriteAging()
        #Assert
        assert self.erase_ssd.call_count == 1471
        assert self.write_ssd.call_count == 2940
        self.mock_print.assert_called_with('PASS')


    def test_EraseAndWriteAging_fail(self, setup_shell,mocker):
        mocker.patch.object(self.shell, '_send_command')
        mocker.patch.object(self.shell, '_aging', side_effect=lambda idx: (_ for _ in ()).throw(
            Exception()) if idx == 4 else None)
        #Act & Assert
        with pytest.raises(Exception):
            self.shell.EraseAndWriteAging()

    def test_main_function_invaild_case(self, setup_shell):
        # Act & Assert
        with pytest.raises(ValueError, match="INVALID COMMAND"):
            self.shell.main_function(['unknown', 'arg'])


    def test_main_function_pass(self, setup_shell):
        #Act
        self.shell.main_function(['read', '10'])
        #Assert
        self.read_ssd.assert_called_once_with(10)


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

    @pytest.fixture
    def setup_logger(self, mocker):
         # 싱글톤 초기화
        Logger._instance = None
        self._logger = Logger()
        self.mock_open = mocker.patch("builtins.open", mocker.mock_open())


    def test_init_removes_log_file_if_exists(self,setup_logger,mocker):
        mock_exists = mocker.patch("os.path.exists", return_value=True)
        mock_remove = mocker.patch("os.remove")
        #Assert
        mock_exists.assert_called_once_with(self._logger.LOG_FILE)
        mock_remove.assert_called_once_with(self._logger.LOG_FILE)

    def test_print_calls_rotate_and_writes(self,setup_logger, mocker, logger):
        mock_rotate = mocker.patch.object(logger, "rotate_log_if_needed")
        self._logger.print("HEADER", "message")
        mock_rotate.assert_called_once()
        self.mock_open.assert_called_once_with("latest.log", 'a', encoding='utf-8')
        written_text = self.mock_open.write.call_args[0][0]

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

    def test_erase_logger_fail(shell,mocker):
        mock_logger = mocker.Mock()
        shell.logger = mock_logger

        # read 메서드가 있어야 __qualname__을 참조할 수 있음
        shell.read = lambda *args, **kwargs: None

        # 실패 조건: LBA < 0
        with pytest.raises(Exception):
            shell.erase(-1, 10)

        # logger.print가 "FAIL"로 호출됐는지 확인
        mock_logger.print.assert_called_once()
        args, _ = mock_logger.print.call_args
        assert args[1] == "FAIL"

