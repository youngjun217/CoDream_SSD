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

