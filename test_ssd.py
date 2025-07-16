import random
from unittest.mock import call
import pytest

from ssd import SSD, SSDOutput, SSDNand
from pytest_mock import MockerFixture

TEST_LBA = 3
TEST_WRITE_VALUE = 0x1298CDEF
ERROR_MESSAGE = "ERROR"


@pytest.fixture
def ssd():
    return SSD()


def test_read(ssd):
    ssd_output = SSDOutput()
    ssd_nand = SSDNand()

    ssd.run([None, 'R', TEST_LBA])
    assert ssd_output.read() == ssd_nand.readline(TEST_LBA)


@pytest.mark.parametrize("lba", [0, 10, 20, 50, 90, 99])
def test_write(ssd, lba):
    ssd_nand = SSDNand()
    ssd_output = SSDOutput()
    ssd.run([None, 'W', lba, hex(TEST_WRITE_VALUE).upper()])

    assert f"{lba:02} 0x{TEST_WRITE_VALUE:08X}\n" == ssd_nand.readline(lba)
    assert ssd_output.read() == ""


@pytest.mark.parametrize("lba", [-1, -10])
def test_ssd_read_error_minus_index(ssd, lba):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'R', lba])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba", [100, 1000, 10000])
def test_ssd_read_error_index_above_99(ssd, lba):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'R', lba])
    assert ssd._output_txt.read() == ERROR_MESSAGE


def test_ssd_read_error_not_digit(ssd):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'R', 'abc'])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(-1, 0x00000000), (-10, 0x00000000)])
def test_ssd_write_error_minus_index(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, hex(value).upper()])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(100, 0x00000000), (1000, 0x00000000), (10000, 0x00000000)])
def test_ssd_write_error_index_above_99(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, hex(value).upper()])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [("abc", 0x00000000), ("ax", 0xABCD0000)])
def test_ssd_write_error_not_digit(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, hex(value).upper()])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(10, -1), (10, -10)])
def test_ssd_write_error_minus_value(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, hex(value).upper()])
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("lba, value", [(10, 0x100000000), (10, 0x300000000)])
def test_ssd_write_error_value_above_32bits(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, hex(value).upper()])
    assert ssd._output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("output", ["ERROR", "10 0x00000000", "20 0x00000000"])
def test_output_read(output):
    ssd_output = SSDOutput()
    with open("ssd_output.txt", 'w', encoding='utf-8') as file:
        file.write(output)

    assert output == ssd_output.read()


@pytest.mark.parametrize("output", ["ERROR", "10 0x00000000", "20 0x00000000"])
def test_output_write(output):
    ssd_output = SSDOutput()
    with open("ssd_output.txt", 'w', encoding='utf-8') as file:
        file.write("")

    ssd_output.write(output)

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == output


def test_nand_read():
    ssd_nand = SSDNand()
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        output = file.readlines()

    assert output == ssd_nand.read()


@pytest.mark.parametrize("lba", [0, 10, 20, 50, 90, 99])
def test_nand_readline(lba):
    ssd_nand = SSDNand()
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        output = file.readlines()

    assert output[lba] == ssd_nand.readline(lba)


def test_nand_write():
    ssd_nand = SSDNand()

    ssd_nand_txt = []
    for i in range(0, 100):
        rand_32bit = random.randint(0, 0xFFFFFFFF)
        newline = f"{i:02d} 0x{rand_32bit:08X}\n"
        ssd_nand_txt.append(newline)

    ssd_nand.write(ssd_nand_txt)

    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        assert file.readlines() == ssd_nand_txt

@pytest.mark.skip()
def test_ssd_read_output(ssd, mocker: MockerFixture):
    mk = mocker.Mock(spec=SSDOutput)
    ssd._output_txt = mk
    ssd.run([None, 'R', 3])
    assert ssd._output_txt.write.call_count == 1

    lines = ssd._nand_txt.read()
    target_line = lines[3]
    ssd._output_txt.write.assert_called_with(target_line)


@pytest.mark.skip()
def test_ssd_write_output(ssd, mocker: MockerFixture):
    mk = mocker.Mock(spec=SSDOutput)
    ssd._output_txt = mk

    ssd.run([None, 'W', 3, "0x12341234"])
    assert ssd._output_txt.write.call_count == 1
    ssd._output_txt.write.assert_called_with("")


@pytest.mark.parametrize("output", [["ERROR"], ["10 0x00000000"], ["20 0x00000000"]])
def test_singleton_ssd_nand(output):
    ssd_nand = SSDNand()
    ssd_nand.write(output)
    ssd_new_output = SSDNand()
    assert ssd_nand.read() == ssd_new_output.read()


@pytest.mark.parametrize("output", ["ERROR", "10 0x00000000", "20 0x00000000"])
def test_singleton_ssd_output(output):
    ssd_output = SSDOutput()
    ssd_output.write(output)
    ssd_new_output = SSDOutput()
    assert ssd_output.read() == ssd_new_output.read()


def test_singleton_ssd():
    ssd_nand = SSDNand()
    ssd_nand.write(["10 0x00000000"])
    ssd_output = SSDOutput()
    ssd_output.write("20 0xABCD0000")
    ssd = SSD()
    assert ssd_output.read() == ssd.output_txt.read()
    assert ssd_nand.read() == ssd.nand_txt.read()


@pytest.mark.skip()
@pytest.mark.parametrize("input", [[None, 'R', 0], [None, 'R', 10], [None, 'R', 99]])
def test_ssd_run_read(ssd, mocker: MockerFixture, input):
    mock_read = mocker.patch('ssd.SSD._command')
    ssd.run(input)
    ssd._command.assert_called_once()
    ssd._command.assert_has_calls([call(input[2])])


@pytest.mark.skip()
@pytest.mark.parametrize("input",
                         [[None, 'W', 0, '0x00000000'], [None, 'W', 10, '0x12345678'], [None, 'W', 99, '0xABCDEF90']])
def test_ssd_run_write(ssd, mocker: MockerFixture, input):
    mock_write = mocker.patch('ssd.SSD._write_ssd')
    ssd.run(input)
    ssd._write_ssd.assert_called_once()
    ssd._write_ssd.assert_has_calls([call(input[2], int(input[3], 16))])


@pytest.mark.skip()
@pytest.mark.parametrize("input", [[None, 'E', 1, 2], [None, 'E', 5, 5], [None, 'E', 10, 10]])
def test_ssd_run_erase(ssd, mocker: MockerFixture, input):
    mock_erase = mocker.patch('ssd.SSD._erase_ssd')
    ssd.run(input)
    ssd._erase_ssd.assert_called_once()
    ssd._erase_ssd.assert_has_calls([call(input[2], input[3])])


@pytest.mark.parametrize("input",
                         [[None, 'A'], [None, 'W', 10], [None, 'W', 10, '1', 1], [None, 'R'],
                          [None, 'R', 99, '0xABCDEF90'],
                          [None, 'E', 10], [None, 'E', 10, 1, 1]])
def test_ssd_run_wrong_command(ssd, input):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run(input)


def test_erase_success(ssd):
    ssd_nand = SSDNand()
    for i in range(100):
        ssd.run([None, 'W', i, hex(TEST_WRITE_VALUE).upper()])

    ssd.run([None, 'E', 0, 10])
    for i in range(0, 10):
        assert ssd_nand.readline(i) == f"{i:02d} 0x00000000\n"

    ssd.run([None, 'E', 11, 5])
    for i in range(11, 16):
        assert ssd_nand.readline(i) == f"{i:02d} 0x00000000\n"


def test_erase_size_error(ssd):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, 11])

    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, 0])


def test_erase_wrong_index_error(ssd):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, 100])

    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', -1, 10])
