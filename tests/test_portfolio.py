import pytest

from ai_stock import Portfolio


def test_sell_adjusts_cost_basis_using_average_cost():
    portfolio = Portfolio(cash=1000)
    portfolio.buy("AAPL", price=10, shares=50)

    realised = portfolio.sell("AAPL", price=12, shares=20)

    assert realised == pytest.approx(40)
    assert portfolio.realised_pnl == pytest.approx(40)
    assert portfolio.cash == pytest.approx(740)

    position = portfolio.position("AAPL")
    assert position is not None
    assert position.shares == pytest.approx(30)
    assert position.cost_basis == pytest.approx(300)
    assert position.average_cost == pytest.approx(10)


def test_full_exit_clears_position_and_accumulates_realised_pnl():
    portfolio = Portfolio(cash=0)
    portfolio.buy("MSFT", price=20, shares=10)

    realised_first = portfolio.sell("MSFT", price=25, shares=4)
    assert realised_first == pytest.approx(20)

    realised_second = portfolio.sell("MSFT", price=30, shares=6)
    assert realised_second == pytest.approx(60)

    assert portfolio.realised_pnl == pytest.approx(80)
    assert portfolio.position("MSFT") is None


def test_unrealised_pnl_and_snapshot_reports_consistent_values():
    portfolio = Portfolio(cash=1000)
    portfolio.buy("GOOG", price=100, shares=2)
    portfolio.buy("GOOG", price=120, shares=1)

    prices = {"GOOG": 150}

    market_value = portfolio.market_value(prices)
    unrealised = portfolio.unrealised_pnl(prices)
    snapshot = portfolio.snapshot(prices)

    assert market_value == pytest.approx(1130)
    assert unrealised == pytest.approx((150 - (320 / 3)) * 3)
    assert snapshot["cash"] == pytest.approx(680)
    assert snapshot["market_value"] == pytest.approx(market_value)
    assert snapshot["unrealised_pnl"] == pytest.approx(unrealised)
    assert snapshot["realised_pnl"] == pytest.approx(0)
