import pytest
from ssd import SSD

def generate_ssd_nand_txt():
    ssd_nand_txt = []
    for i in range(0,100):
        newline = f"{i:02d} 0x00000000\n"
        ssd_nand_txt.append(newline)

    with open("ssd_nand.txt", 'w', encoding='utf-8') as file:
        file.writelines(ssd_nand_txt)


def test_read():
    ssd = SSD()
    index = 3
    ssd.read_ssd(index)
    with open("ssd_nand.txt", 'r', encoding='utf-8') as file:
        ssd_nand_txt = file.read()
    lines = ssd_nand_txt.splitlines()

    with open("ssd_output.txt", 'r', encoding='utf-8') as file:
        ssd_output_txt = file.read()

    assert lines[index] == ssd_output_txt


@pytest.mark.parametrize("lst", [0, 10, 20, 50, 90, 99])
def test_write(lst):
    generate_ssd_nand_txt()
    ssd = SSD()
    index = lst
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


def test_ssd_read_error_minus_index():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(-1)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(-10)


def test_ssd_read_error_index_above_99():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(100)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(1000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd(10000)


def test_ssd_read_error_not_digit():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.read_ssd("abc")


def test_ssd_write_error_minus_index():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(-1, 0x00000000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(-10, 0x00000000)


def test_ssd_write_error_index_above_99():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(100, 0x00000000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(1000, 0x00000000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(10000, 0x00000000)


def test_ssd_write_error_not_digit():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd("abc", 0x00000000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(3, "0xABCD0000")


def test_ssd_write_error_minus_value():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(10, -1)


def test_ssd_write_error_value_above_32bits():
    ssd = SSD()
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(10, 0x100000000)
    with pytest.raises(ValueError, match="ERROR"):
        ssd.write_ssd(10, 0x300000000)
