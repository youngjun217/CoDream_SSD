import os.path

from pytest_mock import MockerFixture

import buffer
from buffer import Buffer, BUFFER_FOLDER_PATH


def test_buffer_mock_create(mocker: MockerFixture):
    mock_create = mocker.patch('buffer.Buffer.create')
    buffer = Buffer()

    buffer.create.assert_called_once()

def test_buffer_create():
    buffer = Buffer()
    file_list = os.listdir(BUFFER_FOLDER_PATH)

    assert os.path.exists(BUFFER_FOLDER_PATH)
    assert buffer._buf_lst == file_list

def test_buffer_get_buf():
    buffer = Buffer()
    assert ('W', 1, '0x00000001') == buffer._get_buf_information("2_W_1_0x00000001")

