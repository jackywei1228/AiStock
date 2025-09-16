"""Board and stock money flow statistics sourced from AKShare."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from .board_data import Board
from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardMoneyFlow:
    board: str
    category: str
    date: date
    net_inflow: float
    main_inflow: float


@dataclass(frozen=True)
class StockMoneyFlow:
    symbol: str
    date: date
    main_inflow: float
    large_inflow: float
    medium_inflow: float
    small_inflow: float


def fetch_money_flow(boards: Iterable[Board], start: date, end: date) -> Dict[str, List[BoardMoneyFlow]]:
    result: Dict[str, List[BoardMoneyFlow]] = {}
    for board in boards:
        flows = [
            BoardMoneyFlow(
                board=board.code,
                category=board.category,
                date=item["date"],
                net_inflow=item["net_inflow"],
                main_inflow=item["main_inflow"],
            )
            for item in akshare_helper.board_money_flow(
                board.code,
                start,
                end,
                board_name=board.name,
                category=board.category,
            )
        ]
        if flows:
            result[board.code] = flows
    return result


def fetch_stock_money_flow(symbols: Iterable[str], start: date, end: date) -> Dict[str, List[StockMoneyFlow]]:
    result: Dict[str, List[StockMoneyFlow]] = {}
    for symbol in symbols:
        flows = [
            StockMoneyFlow(
                symbol=symbol,
                date=item["date"],
                main_inflow=item["main_inflow"],
                large_inflow=item["large_inflow"],
                medium_inflow=item["medium_inflow"],
                small_inflow=item["small_inflow"],
            )
            for item in akshare_helper.stock_money_flow(symbol, start, end)
        ]
        if flows:
            result[symbol] = flows
    return result
