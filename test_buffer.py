import pytest
import os.path
from pytest_mock import MockerFixture
from buffer import Buffer, BUFFER_FOLDER_PATH, WRITE, ERASE, EMPTY_VALUE, ERASE_VALUE

TEST_LBA = 3
TEST_WRITE_VALUE = 0x1234ABCD

@pytest.fixture
def buffer(mocker: MockerFixture):
    mocker.patch("os.makedirs")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.listdir", return_value=[])
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("buffer.SSDOutput", return_value=mocker.Mock(write=mocker.Mock()))
    buffer = Buffer()
    buffer._buf_lst = ['1_empty', '2_empty', '3_empty', '4_empty', '5_empty']
    buffer._buffer_cnt = 0
    return buffer

def test_create_when_folder_does_not_exist(mocker: MockerFixture):
    mocker.patch("os.path.exists", return_value=False)
    makedirs_mock = mocker.patch("os.makedirs")
    mocker.patch("os.listdir", return_value=[])
    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("buffer.SSDOutput", return_value=mocker.Mock(write=mocker.Mock()))
    Buffer()
    makedirs_mock.assert_called_once_with(BUFFER_FOLDER_PATH)

def test_write_command_updates_memory(buffer: Buffer):
    sys_argv = [None, 'W', str(TEST_LBA), f"0x{TEST_WRITE_VALUE:08X}"]
    buffer._set_buffer_with_write(WRITE, int(sys_argv[2]), int(sys_argv[3],16))
    assert buffer._buffer_cmd_memory[TEST_LBA][0] == WRITE
    assert buffer._buffer_cmd_memory[TEST_LBA][1] == TEST_WRITE_VALUE

def test_flush_calls_remove_buffer_and_put_run_command(buffer: Buffer, mocker: MockerFixture):
    buffer._buf_lst = [
        "1_W_1_0x00000001",
        "2_E_2_3",
        "3_W_3_0x00000003",
        "4_E_4_1",
        "5_W_5_0x00000005"
    ]
    buffer._buffer_cnt = 5

    mock_remove = mocker.patch.object(buffer, '_remove_buffer_and_put_run_command')

    buffer._flush(5)

    assert mock_remove.call_count == 5
    assert buffer._buf_lst == ['1_empty', '2_empty', '3_empty', '4_empty', '5_empty']
    assert buffer._buffer_cnt == 0

def test_remove_buffer_and_put_run_command_write_full_buf(buffer: Buffer):
    buffer._buffer_cmd_memory[3][0] = WRITE
    buffer._buffer_cmd_memory[3][1] = 0x00000011
    buffer._buf_lst = [
        "1_W_3_0x00000011",
        "2_E_1_1",
        "3_W_2_0x00000022",
        "4_empty",
        "5_empty"
    ]
    buffer._buffer_cnt = 3
    buffer._run_command = []
    buffer._remove_buffer_and_put_run_command(0)
    assert buffer._buffer_cmd_memory[3][0] == 0  # 해당 LBA 초기화 확인
    assert buffer._buffer_cmd_memory[3][1] == 0  # 해당 LBA 초기화 확인
    assert buffer._run_command == [[None, 'W', 3, '0x00000011']]


def test_remove_buffer_and_put_run_command_erase_full_buf(buffer: Buffer):
    buffer._buffer_cmd_memory[5][0] = ERASE
    buffer._buffer_cmd_memory[5][1] = ERASE_VALUE
    buffer._buffer_cmd_memory[6][0] = ERASE
    buffer._buffer_cmd_memory[6][1] = ERASE_VALUE
    buffer._buf_lst = [
        "1_E_5_2",
        "2_W_1_0x00000011"
    ]
    buffer._remove_buffer_and_put_run_command(0)
    assert buffer._buffer_cmd_memory[5][0] == 0
    assert buffer._buffer_cmd_memory[6][0] == 0
    assert buffer._run_command == [[None, 'E', 5, '2']]



def test_multiple_writes_to_same_lba_overwrites_previous(buffer: Buffer):
    lba = 3
    first_value = 0xAAAA1111
    second_value = 0xBBBB2222

    buffer._check_buffer_write([None, 'W', str(lba), f"0x{first_value:08X}"])
    buffer._check_buffer_write([None, 'W', str(lba), f"0x{second_value:08X}"])

    assert buffer._buffer_cmd_memory[lba][0] == WRITE
    assert buffer._buffer_cmd_memory[lba][1] == second_value

    lba_entries = [entry for entry in buffer._buf_lst if f"_W_{lba}_" in entry]
    assert len(lba_entries) == 1
    expected_entry = f"{lba_entries[0].split('_')[0]}_W_{lba}_0x{second_value:08X}"
    assert lba_entries[0] == expected_entry

def test_multiple_erases_to_same_range_are_merged(buffer: Buffer):

    first_lba = 11
    first_size = 4
    second_lba = 14
    second_size = 3

    buffer._check_buffer_erase([None, 'E', str(first_lba), str(first_size)])
    buffer._check_buffer_erase([None, 'E', str(second_lba), str(second_size)])

    for lba in range(first_lba, second_lba + second_size):
        assert buffer._buffer_cmd_memory[lba][0] == ERASE
        assert buffer._buffer_cmd_memory[lba][1] == ERASE_VALUE

    erase_entries = [entry for entry in buffer._buf_lst if entry.split('_')[1] == 'E']
    assert len(erase_entries) == 1
    assert f"_E_{first_lba}_6" in erase_entries[0]


def test_erase_commands_split_by_write_are_not_merged(buffer: Buffer, mocker: MockerFixture):

    buffer._check_buffer_erase([None, 'E', '10', '2'])  # ERASE 10,11
    buffer._check_buffer_write([None, 'W', '12', '0xABCD1234'])  # WRITE 12
    buffer._check_buffer_erase([None, 'E', '13', '2'])  # ERASE 13,14

    for lba in [10, 11, 13, 14]:
        assert buffer._buffer_cmd_memory[lba][0] == ERASE
        assert buffer._buffer_cmd_memory[lba][1] == ERASE_VALUE
    assert buffer._buffer_cmd_memory[12][0] == WRITE
    assert buffer._buffer_cmd_memory[12][1] == 0xABCD1234

    erase_entries = [entry for entry in buffer._buf_lst if entry.split('_')[1] == 'E']
    assert len(erase_entries) == 2
    assert any("_E_10_2" in entry for entry in erase_entries)
    assert any("_E_13_2" in entry for entry in erase_entries)

def test_buffer_create():
    buffer = Buffer()
    file_list = os.listdir(BUFFER_FOLDER_PATH)

    assert os.path.exists(BUFFER_FOLDER_PATH)
    assert buffer._buf_lst == file_list

def test_buffer_get_buf():
    buffer = Buffer()
    assert ('W', 1, '0x00000001') == buffer._get_buf_information("2_W_1_0x00000001")
