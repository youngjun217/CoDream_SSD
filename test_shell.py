import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from shell import shell_ftn

def test_read(mocker):
    mock_read_ssd = mocker.patch('shell.read_ssd')
    mock_read_ssd.side_effect = [1,2,3]

    shell= shell_ftn()
    assert shell.read(0) == 1
    assert shell.read(1) == 2
    assert shell.read(2) == 3