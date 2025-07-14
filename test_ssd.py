import pytest

from ssd import SSD


def test_ssd():
    assert False

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