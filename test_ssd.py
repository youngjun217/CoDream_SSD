import pytest

from ssd import SSD


def test_ssd():
    assert False

def test_read():
    ssd = SSD()
    index = 3
    ssd.read(lba=index)
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        ssd_nand_txt = file.read()
    lines = ssd_nand_txt.splitlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    assert lines[index] == ssd_output_txt

def test_write():
    ssd = SSD()
    index = 3
    value = 0x1298CDEF
    ssd.write(lba=index, value=value)
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        ssd_nand_txt = file.read()
    lines = ssd_nand_txt.splitlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    written_value = lines[index].split(" ")[-1]
    assert value == int(written_value)
    assert ssd_output_txt == ""


def test_ssd_read_error_minus_index():
    ssd = SSD()
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.read(-1)
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.read(-10)

def test_ssd_read_error_index_above_99():
    ssd = SSD()
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.read(100)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read(1000)
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.read(10000)

def test_ssd_read_error_not_digit():
    ssd = SSD()
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.read("abc")


def test_ssd_write_error_minus_index():
    ssd = SSD()
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.write(-1)
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.write(-10)

def test_ssd_write_error_index_above_99():
    ssd = SSD()
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.write(100)
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.write(1000)
    with pytest.raises(ValueError, match = "ERROR"):
        ssd.write(10000)

def test_ssd_write_error_not_digit():
    ssd = SSD()
    with pytest.raises("ValueError", match = "ERROR"):
        ssd.write("abc")