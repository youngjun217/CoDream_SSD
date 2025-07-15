import random

import pytest
from ssd import SSD, SSDOutput, SSDNand
from pytest_mock import MockerFixture


def generate_ssd_nand_txt():
    ssd_nand_txt = []
    for i in range(0, 100):
        newline = f"{i:02d} 0x00000000\n"
        ssd_nand_txt.append(newline)

    with open("ssd_nand.txt", 'w', encoding='utf-8') as file:
        file.writelines(ssd_nand_txt)


def test_read():
    ssd = SSD()
    index = 3
    ssd.read_ssd(index)
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    assert lines[index] == ssd_output_txt


@pytest.mark.parametrize("index", [0, 10, 20, 50, 90, 99])
def test_write(index):
    generate_ssd_nand_txt()
    ssd = SSD()
    value = 0x1298CDEF
    ssd.write_ssd(lba=index, value=value)
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        ssd_nand_txt = file.read()
    lines = ssd_nand_txt.splitlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    written_value = lines[index].split(" ")[-1]
    assert f"0x{value:08X}" == written_value
    assert ssd_output_txt == ""


@pytest.mark.parametrize("index", [-1, -10])
def test_ssd_read_error_minus_index(index):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(index)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index", [100, 1000, 10000])
def test_ssd_read_error_index_above_99(index):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(index)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


def test_ssd_read_error_not_digit():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd("abc")
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index, value", [(-1, 0x00000000), (-10, 0x00000000)])
def test_ssd_write_error_minus_index(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(index, value)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index, value", [(100, 0x00000000), (1000, 0x00000000), (10000, 0x00000000)])
def test_ssd_write_error_index_above_99(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(index, value)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index, value", [("abc", 0x00000000), (3, "0xABCD0000")])
def test_ssd_write_error_not_digit(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(index, value)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index, value", [(10, -1), (10, -10)])
def test_ssd_write_error_minus_value(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(index, value)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


@pytest.mark.parametrize("index, value", [(10, 0x100000000), (10, 0x300000000)])
def test_ssd_write_error_value_above_32bits(index, value):
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(index, value)
    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        assert file.read() == "ERROR"


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
    generate_ssd_nand_txt()
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        output = file.readlines()

    assert output == ssd_nand.read()


@pytest.mark.parametrize("index", [0, 10, 20, 50, 90, 99])
def test_nand_readline(index):
    ssd_nand = SSDNand()
    generate_ssd_nand_txt()
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        output = file.readlines()

    assert output[index] == ssd_nand.readline(index)


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