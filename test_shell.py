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

# def test_read_fail(mocker):
#     mock_read_ssd = mocker.patch('shell.read_ssd')
#     mock_read_ssd.side_effect = [1,2,3,ValueError]
#
#     shell= shell_ftn()
#     with pytest.raises(ValueError, match='ERROR'):
#         shell.read(100)
#     with pytest.raises(ValueError, match='ERROR'):
#         shell.read(10.1)
#
#     # act
#     test_shell.fullwrite(12341234)
#     captured = capsys.readouterr()
#     mock_read_ssd = mocker.patch('shell.shell_ftn.fullwrite')
#     mock_read_ssd.side_effect = "[Full Write] Done"
#     expected = "[Full Write] Done"
#
#     assert captured=="[Full Write] Done"

# def test_fullwrite():
#
#
#
# def test_select_stock_brocker_fail():
#     # arrange
#     auto_trading_system = AutoTradingSystem()
#
#     # act and assert
#     with pytest.raises(ValueError, match="unknown API\n"):
#         auto_trading_system.select_stock_brocker("marae")


# def test_select_stock_brocker_fail():
#     # arrange
#     auto_trading_system = AutoTradingSystem()
#
#     # act and assert
#     with pytest.raises(ValueError, match="unknown API\n"):
#         auto_trading_system.select_stock_brocker("marae")
#
#
# def test_error_when_test_stock_brocker_not_selected():
#     # arrange
#     auto_trading_system = AutoTradingSystem()
#
#     # act and assert
#     with pytest.raises(Exception, match="Stock Brocker is not selected!"):
#         auto_trading_system.is_set_stock_brocker()
#
#
# def test_login(mocker: MockerFixture):
#     # arrange
#     stock_brocker_device: StockBrockerDeviceDriver = mocker.Mock()
#     auto_trading_system = AutoTradingSystem()
#     auto_trading_system.set_stock_brocker(stock_brocker_device)
#
#     # act
#     auto_trading_system.login("idtest1", "12345678")
#     auto_trading_system.login("idtest2", "4567890")
#     auto_trading_system.login("idtest3", "12345678")
#
#     stock_brocker_device.login.assert_has_calls(
#         [call("idtest1", "12345678"), call("idtest2", "4567890"), call("idtest3", "12345678")])
#     stock_brocker_device.login.call_count == 3