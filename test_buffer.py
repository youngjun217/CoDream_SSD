import os.path

from pytest_mock import MockerFixture

from buffer import Buffer, BUFFER_FOLDER_PATH


def test_buffer_mock_create(mocker: MockerFixture):
    mock_create = mocker.patch('buffer.Buffer.create')
    buffer = Buffer()

    buffer.create.assert_called_once()

def test_buffer_create():
    buffer = Buffer()
    file_list = os.listdir(BUFFER_FOLDER_PATH)

    assert os.path.exists(BUFFER_FOLDER_PATH)
    assert buffer.buf_lst[1:] == file_list


