import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from shell import shell_ftn

def test_read_success(mocker):
    mock_read_ssd = mocker.patch('shell.shell_ftn.read')
    mock_read_ssd.side_effect = [1,2,3]

    shell= shell_ftn()
    assert shell.read(0) == 1
    assert shell.read(1) == 2
    assert shell.read(2) == 3


def test_read_fail(mocker):
    mock_read_ssd = mocker.patch('shell.shell_ftn.read')
    mock_read_ssd.side_effect = ValueError('ERROR')

    shell= shell_ftn()
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(100)
    with pytest.raises(ValueError, match='ERROR'):
        shell.read(10.1)
#


def test_fullwrite(capsys):
    test_shell=shell_ftn()
    # act
    test_shell.fullwrite(12341234)
    captured = capsys.readouterr()
    # mock_read_ssd = mocker.patch('shell.shell_ftn.fullwrite')
    # mock_read_ssd.side_effect = "[Full Write] Done"
    expected = "[Full Write] Done"

    assert captured.out=="[Full Write] Done\n"