import random
from unittest.mock import call, patch
import pytest

from buffer import Buffer
from ssd import SSD, SSDOutput, SSDNand
from pytest_mock import MockerFixture

from ssd_texts import MAX_NAND_SIZE

TEST_LBA = 3
TEST_WRITE_VALUE = 0x1298CDEF
ERROR_MESSAGE = "ERROR"


def dec_to_hex(value):
    return f"0x{value:08X}"


@pytest.fixture
def ssd():
    return SSD(True)


def test_read(ssd):
    ssd_output = SSDOutput()
    ssd_nand = SSDNand()

    ssd.run([None, 'R', TEST_LBA])
    assert ssd_output.read() == ssd_nand.read()[TEST_LBA]


@pytest.mark.parametrize("lba", [0, 10, 20, 50, 90, 99])
def test_write(ssd, lba):
    ssd_nand = SSDNand()
    ssd_output = SSDOutput()
    ssd.run([None, 'W', lba, dec_to_hex(TEST_WRITE_VALUE)])

    assert f"{lba:02} 0x{TEST_WRITE_VALUE:08X}\n" == ssd_nand.read()[lba]
    assert ssd_output.read() == ""


@pytest.mark.parametrize("lba", [-1, -10])
def test_ssd_read_error_minus_index(ssd, lba):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'R', lba])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba", [100, 1000, 10000])
def test_ssd_read_error_index_above_99(ssd, lba):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'R', lba])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


def test_ssd_read_error_not_digit(ssd):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'R', 'abc'])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(-1, 0x00000000), (-10, 0x00000000)])
def test_ssd_write_error_minus_index(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, dec_to_hex(value)])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(100, 0x00000000), (1000, 0x00000000), (10000, 0x00000000)])
def test_ssd_write_error_index_above_99(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, dec_to_hex(value)])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [("abc", 0x00000000), ("ax", 0xABCD0000)])
def test_ssd_write_error_not_digit(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, dec_to_hex(value)])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(10, -1), (10, -10)])
def test_ssd_write_error_minus_value(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, dec_to_hex(value)])
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("lba, value", [(10, 0x100000000), (10, 0x300000000)])
def test_ssd_write_error_value_above_32bits(ssd, lba, value):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'W', lba, dec_to_hex(value)])
    output_txt = SSDOutput()
    assert output_txt.read() == ERROR_MESSAGE


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

    assert output[lba] == ssd_nand.read()[lba]


def test_nand_write():
    ssd_nand = SSDNand()

    ssd_nand_txt = []
    for i in range(0, MAX_NAND_SIZE):
        rand_32bit = random.randint(0, 0xFFFFFFFF)
        newline = f"{i:02d} 0x{rand_32bit:08X}\n"
        ssd_nand_txt.append(newline)

    ssd_nand.write(ssd_nand_txt)

    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        assert file.readlines() == ssd_nand_txt


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


@pytest.mark.parametrize("input",
                         [[None, 'A'], [None, 'W', 10], [None, 'W', 10, '1', 1], [None, 'R'],
                          [None, 'R', 99, '0xABCDEF90'],
                          [None, 'E', 10], [None, 'E', 10, 1, 1], [None, 'F', 10, 1, 1], [None, 'F', 10]])
def test_ssd_run_wrong_command(ssd, input):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run(input)


def test_erase_success(ssd):
    ssd_nand = SSDNand()
    for i in range(MAX_NAND_SIZE):
        ssd.run([None, 'W', i, dec_to_hex(TEST_WRITE_VALUE)])

    ssd.run([None, 'E', 0, 10])
    for i in range(0, 10):
        assert ssd_nand.read()[i] == f"{i:02d} 0x00000000\n"

    ssd.run([None, 'E', 11, 5])
    for i in range(11, 16):
        assert ssd_nand.read()[i] == f"{i:02d} 0x00000000\n"

def test_erace_out_of_range(ssd):
    ssd_nand = SSDNand()
    for i in range(MAX_NAND_SIZE):
        ssd.run([None, 'W', i, dec_to_hex(TEST_WRITE_VALUE)])

    ssd.run([None, 'E', 99, 2])
    for i in range(99, MAX_NAND_SIZE):
        assert ssd_nand.read()[i] == f"{i:02d} 0x00000000\n"
    assert len(ssd_nand.read()) == MAX_NAND_SIZE

def test_erase_size_error(ssd):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, 11])

    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, 0])


def test_erase_wrong_index_error(ssd):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', 0, MAX_NAND_SIZE])

    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, 'E', -1, 10])


@pytest.mark.parametrize("lba, size", [("abc", 2), (1, "ab")])
def test_erase_wrong_index_error_not_digit(ssd, lba, size):
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.run([None, 'E', lba, size])


@pytest.mark.parametrize("cmd", ['A', '1', '@'])
def test_wrong_command_error(ssd, cmd):
    with pytest.raises(ValueError, match="ERROR"):
        ssd.run([None, cmd, 0, 100])

@patch('buffer.Buffer.run')
def test_flush_success(mock_buffer_run):
    ssd = SSD()
    ssd_nand = SSDNand()
    mock_buffer_run.return_value = [[None, 'W', 1, '0x1234ABCD']]

    ssd.run([None, 'F'])

    assert ssd_nand.read()[1] == "01 0x1234ABCD\n"


@patch('buffer.Buffer.run')
def test_no_command(mock_buffer_run):
    ssd = SSD()
    ssd_nand = SSDNand()
    ssd_output = SSDOutput()
    mock_buffer_run.return_value = []

    assert ssd.run([None, 'F']) == None