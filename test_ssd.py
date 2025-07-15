import random
import pytest
from ssd import SSD, SSDOutput, SSDNand
from pytest_mock import MockerFixture

TEST_LBA = 3
TEST_WRITE_VALUE = 0x1298CDEF
ERROR_MESSAGE = "ERROR"

def test_read():
    ssd = SSD()
    ssd_output = SSDOutput()
    ssd_nand = SSDNand()

    ssd.read_ssd(TEST_LBA)
    assert ssd_output.read() == ssd_nand.readline(TEST_LBA)


@pytest.mark.parametrize("lba", [0, 10, 20, 50, 90, 99])
def test_write(lba):
    ssd_nand = SSDNand()
    ssd_output = SSDOutput()

    ssd = SSD()
    ssd.write_ssd(lba=lba, value=TEST_WRITE_VALUE)

    assert f"{lba:02} 0x{TEST_WRITE_VALUE:08X}" == ssd_nand.read(TEST_LBA)
    assert ssd_output.read() == ""


@pytest.mark.parametrize("lba", [-1, -10])
def test_ssd_read_error_minus_index(lba):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(lba)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("index", [100, 1000, 10000])
def test_ssd_read_error_index_above_99(index):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.read_ssd(index)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


def test_ssd_read_error_not_digit():
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.read_ssd("abc")
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("index, value", [(-1, 0x00000000), (-10, 0x00000000)])
def test_ssd_write_error_minus_index(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.write_ssd(index, value)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(100, 0x00000000), (1000, 0x00000000), (10000, 0x00000000)])
def test_ssd_write_error_index_above_99(lba, value):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.write_ssd(lba, value)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [("abc", 0x00000000), (3, "0xABCD0000")])
def test_ssd_write_error_not_digit(lba, value):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.write_ssd(lba, value)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("index, value", [(10, -1), (10, -10)])
def test_ssd_write_error_minus_value(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.write_ssd(index, value)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


@pytest.mark.parametrize("lba, value", [(10, 0x100000000), (10, 0x300000000)])
def test_ssd_write_error_value_above_32bits(lba, value):
    ssd = SSD()
    with pytest.raises(ValueError, match=ERROR_MESSAGE):
        ssd.write_ssd(lba, value)
    ssd_output = SSDOutput()
    assert ssd_output.read() == ERROR_MESSAGE


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


def test_ssd_read_output(mocker: MockerFixture):
    mk = mocker.Mock(spec=SSDOutput)
    ssd = SSD()
    ssd._output_txt = mk
    ssd.read_ssd(3)
    assert ssd._output_txt.write.call_count == 1

    lines = ssd._nand_txt.read()
    target_line = lines[3]
    ssd._output_txt.write.assert_called_with(target_line)


def test_ssd_write_output(mocker: MockerFixture):
    mk = mocker.Mock(spec=SSDOutput)
    ssd = SSD()
    ssd._output_txt = mk

    ssd.write_ssd(3, 0x12312312)
    assert ssd._output_txt.write.call_count == 1
    ssd._output_txt.write.assert_called_with("")

@pytest.mark.parametrize("output", [["ERROR"], ["10 0x00000000"], ["20 0x00000000"]])
def test_singletone_ssd_nand(output):
    ssd_output = SSDNand()
    ssd_output.write(output)
    ssd_new_output = SSDNand()
    assert ssd_output.read() == ssd_new_output.read()

@pytest.mark.parametrize("output", ["ERROR", "10 0x00000000", "20 0x00000000"])
def test_singletone_ssd_output(output):
    ssd_output = SSDOutput()
    ssd_output.write(output)
    ssd_new_output = SSDOutput()
    assert ssd_output.read() == ssd_new_output.read()

