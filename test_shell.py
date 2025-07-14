import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from shell import shell_ftn

def test_read_success(mocker):
    mock_read_ssd = mocker.patch('shell.read_ssd')
    mock_read_ssd.side_effect = [1,2,3,ValueError]

    shell= shell_ftn()
    assert shell.read(0) == 1
    assert shell.read(1) == 2
    assert shell.read(2) == 3

def test_read_fail(mocker):
    mock_read_ssd = mocker.patch('shell.read_ssd')
    mock_read_ssd.side_effect = [1,2,3,ValueError]

    shell= shell_ftn()
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(100)
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(10.1)
