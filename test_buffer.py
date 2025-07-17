import pytest
from pytest_mock import MockerFixture
from buffer import Buffer, BUFFER_FOLDER_PATH, WRITE, ERASE, EMPTY_VALUE

TEST_LBA = 3
TEST_WRITE_VALUE = 0x1234ABCD

@pytest.fixture
def buffer(mocker: MockerFixture):
    mocker.patch("os.makedirs")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.listdir", return_value=[])
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("buffer.SSDOutput", return_value=mocker.Mock(write=mocker.Mock()))
    return Buffer()

def test_create_when_folder_does_not_exist(mocker: MockerFixture):
    mocker.patch("os.path.exists", return_value=False)
    makedirs_mock = mocker.patch("os.makedirs")
    mocker.patch("os.listdir", return_value=[])
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("buffer.SSDOutput", return_value=mocker.Mock(write=mocker.Mock()))
    Buffer()
    makedirs_mock.assert_called_once_with(BUFFER_FOLDER_PATH)

def test_write_command_updates_memory(buffer: Buffer, mocker: MockerFixture):
    mocker.patch.object(buffer, "flush")
    sys_argv = [None, 'W', str(TEST_LBA), f"0x{TEST_WRITE_VALUE:08X}"]
    buffer.set_buffer(sys_argv)
    assert buffer.command_memory[TEST_LBA] == WRITE
    assert buffer.value_memory[TEST_LBA] == TEST_WRITE_VALUE

def test_flush_calls_remove_buffer_and_put_run_command(buffer: Buffer, mocker: MockerFixture):
    buffer.buf_lst = [
        "1_W_1_0x00000001",
        "2_E_2_3",
        "3_W_3_0x00000003",
        "4_E_4_1",
        "5_W_5_0x00000005"
    ]
    for i in [1, 3, 5]:
        buffer.command_memory[i] = WRITE

    mock_remove = mocker.patch.object(buffer, 'remove_buffer_and_put_run_command')
    mock_rename = mocker.patch.object(buffer, 'rename_buffer_to_start_1')
    mock_recreate = mocker.patch.object(buffer, 'remove_flushed_files_and_create_new_buffer')

    buffer.flush(5)

    assert mock_remove.call_count == 5
    mock_rename.assert_called_once()
    mock_recreate.assert_called_once()

def test_remove_buffer_and_put_run_command_write_full_buf(buffer: Buffer):
    buffer.command_memory[3] = WRITE
    buffer.buf_lst = [
        "1_W_3_0x00000011",
        "2_E_1_1",
        "3_W_2_0x00000022",
        "4_empty",
        "5_empty"
    ]
    buffer._run_command = []
    buffer.remove_buffer_and_put_run_command(0)
    assert buffer.command_memory[3] == 0  # 해당 LBA 초기화 확인
    assert buffer._run_command == [[None, 'W', 3, '0x00000011']]


def test_remove_buffer_and_put_run_command_erase_full_buf(buffer: Buffer):
    buffer.command_memory[5] = ERASE
    buffer.command_memory[6] = ERASE
    buffer.buf_lst = [
        "1_E_5_2",
        "2_W_1_0x00000011"
    ]
    buffer.remove_buffer_and_put_run_command(0)
    assert buffer.command_memory[5] == 0
    assert buffer.command_memory[6] == 0
    assert buffer._run_command == [[None, 'E', 5, 2]]



def test_multiple_writes_to_same_lba_overwrites_previous(buffer: Buffer, mocker: MockerFixture):
    lba = 3
    first_value = 0xAAAA1111
    second_value = 0xBBBB2222

    mocker.patch.object(buffer, "flush")  # flush 무력화

    buffer.set_buffer([None, 'W', str(lba), f"0x{first_value:08X}"])
    buffer.set_buffer([None, 'W', str(lba), f"0x{second_value:08X}"])

    assert buffer.command_memory[lba] == WRITE
    assert buffer.value_memory[lba] == second_value

    lba_entries = [entry for entry in buffer.buf_lst if f"_W_{lba}_" in entry]
    assert len(lba_entries) == 1
    expected_entry = f"{lba_entries[0].split('_')[0]}_W_{lba}_0x{second_value:08X}"
    assert lba_entries[0] == expected_entry

def test_multiple_erases_to_same_range_are_merged(buffer: Buffer, mocker: MockerFixture):
    mocker.patch.object(buffer, "flush")

    first_lba = 11
    first_size = 4
    second_lba = 14
    second_size = 3

    buffer.set_buffer([None, 'E', str(first_lba), str(first_size)])
    buffer.set_buffer([None, 'E', str(second_lba), str(second_size)])

    for lba in range(first_lba, second_lba + second_size):
        assert buffer.command_memory[lba] == ERASE
        assert buffer.value_memory[lba] == EMPTY_VALUE

    erase_entries = [entry for entry in buffer.buf_lst if entry.split('_')[1] == 'E']
    assert len(erase_entries) == 1
    assert f"_E_{first_lba}_6" in erase_entries[0]


def test_erase_commands_split_by_write_are_not_merged(buffer: Buffer, mocker: MockerFixture):
    mocker.patch.object(buffer, "flush")

    buffer.set_buffer([None, 'E', '10', '2'])  # ERASE 10,11
    buffer.set_buffer([None, 'W', '12', '0xABCD1234'])  # WRITE 12
    buffer.set_buffer([None, 'E', '13', '2'])  # ERASE 13,14

    for lba in [10, 11, 13, 14]:
        assert buffer.command_memory[lba] == ERASE
        assert buffer.value_memory[lba] == EMPTY_VALUE
    assert buffer.command_memory[12] == WRITE

    erase_entries = [entry for entry in buffer.buf_lst if entry.split('_')[1] == 'E']
    assert len(erase_entries) == 2
    assert any("_E_10_2" in entry for entry in erase_entries)
    assert any("_E_13_2" in entry for entry in erase_entries)
