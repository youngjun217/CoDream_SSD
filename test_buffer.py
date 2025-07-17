import os
import pytest
from buffer import Buffer, WRITE, ERASE, EMPTY_VALUE


@pytest.fixture
def buffer_instance(tmp_path):
    buf = Buffer()
    buf.folder_path = tmp_path
    buf.buf_lst = []
    buf.create()
    return buf


def test_write_and_updates_buf_lst(buffer_instance, mocker):
    mocker.patch.object(buffer_instance, "flush")
    old_path = os.path.join(buffer_instance.folder_path, "1_empty")
    assert os.path.isfile(old_path)

    buffer_instance.write("W", 10, "0x1234")
    new_name = "1_W_10_0x1234"
    new_path = os.path.join(buffer_instance.folder_path, new_name)
    assert os.path.isfile(new_path)
    assert buffer_instance.buf_lst[0] == new_name


def test_write_flush_called_when_no_empty(buffer_instance, mocker):
    buffer_instance.buf_lst = [f"{i}_W_{i}_0" for i in range(1, 6)]

    for i in range(1, 6):
        open(os.path.join(buffer_instance.folder_path, f"{i}_W_{i}_0"), 'w').close()

    flush_mock = mocker.patch.object(buffer_instance, "flush", autospec=True)
    buffer_instance.write("W", 1, "0x12345678")
    flush_mock.assert_called_once()



def test_flush_removes_files_and_recreates(buffer_instance, mocker):
    mocker.patch.object(buffer_instance.ssd, "run", return_value=None)

    for i in range(1, 6):
        open(os.path.join(buffer_instance.folder_path, f"{i}_W_{i}_0"), 'w').close()

    buffer_instance.flush()

    files = sorted(os.listdir(buffer_instance.folder_path))
    expected_files = [f"{i}_empty" for i in range(1, 6)]
    assert files == expected_files
    assert buffer_instance.buf_lst == expected_files


def test_flush_removes_files_and_recreates(buffer_instance):
    for i in range(1, 6):
        open(os.path.join(buffer_instance.folder_path, f"{i}_W_{i}_0"), 'w').close()
    buffer_instance.flush()
    files = os.listdir(buffer_instance.folder_path)
    assert sorted(files) == [f"{i}_empty" for i in range(1, 6)]
    assert buffer_instance.buf_lst == [f"{i}_empty" for i in range(1, 6)]


def test_set_buffer_write_and_erase(buffer_instance):
    buffer_instance.set_buffer([None, "W", "10", "0x12345678"])
    assert buffer_instance.command_memory[10] == WRITE
    assert buffer_instance.value_memory[10] == 0x12345678
    assert any("_W_10" in s for s in buffer_instance.buf_lst)

    buffer_instance.set_buffer([None, "E", "3", "5"])
    for i in range(3, 8):
        assert buffer_instance.command_memory[i] == ERASE
        assert buffer_instance.value_memory[i] == EMPTY_VALUE
    assert any("_E_3_5" in s for s in buffer_instance.buf_lst)


def test_run_writes_correctly(buffer_instance, mocker):
    write_mock = mocker.MagicMock()
    buffer_instance.ssd._output_txt.write = write_mock

    buffer_instance.value_memory[10] = 0x12345678
    buffer_instance.run([None, "R", "10"])
    write_mock.assert_called_once_with("10 0x12345678\n")

    write_mock.reset_mock()
    buffer_instance.run([None, "W", "10"])
    write_mock.assert_called_once_with("")


def test_run_invalid_index_raises(buffer_instance):
    with pytest.raises(IndexError):
        buffer_instance.run([None, "R", "-1"])
    with pytest.raises(IndexError):
        buffer_instance.run([None, "W", "200"])


def test_run_writes_correctly(buffer_instance, mocker):
    write_mock_r = mocker.patch.object(buffer_instance.ssd._output_txt, "write")
    buffer_instance.value_memory[10] = 0x12345678
    buffer_instance.run([None, "R", "10"])
    write_mock_r.assert_called_once_with("10 0x12345678\n")


def test_set_buffer_erase_chunks(buffer_instance):
    buffer_instance.set_buffer([None, "E", "0", "15"])
    erase_cmds = [s for s in buffer_instance.buf_lst if "_E_" in s]
    assert any("10" in e for e in erase_cmds)
    assert len(buffer_instance.buf_lst) == 5
