"""Stock level data used when picking leaders."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from .board_data import Board
from ..utils import akshare_helper


@dataclass(frozen=True)
class StockBar:
    symbol: str
    date: date
    close: float
    turnover_rate: float


@dataclass(frozen=True)
class BoardComponentQuote:
    board: str
    category: str
    symbol: str
    name: str
    last_price: float
    pct_change: float
    turnover: float
    turnover_rate: float
    turnover_share: float


@dataclass(frozen=True)
class LeaderSnapshot:
    board: str
    category: str
    symbol: str
    name: str
    pct_change: float
    turnover_share: float
    limit_up_streak: int


def fetch_stock_data(stocks: Iterable[str], start: date, end: date) -> Dict[str, List[StockBar]]:
    result: Dict[str, List[StockBar]] = {}
    for symbol in stocks:
        history = [
            StockBar(
                symbol=symbol,
                date=item["date"],
                close=item["close"],
                turnover_rate=item["turnover_rate"],
            )
            for item in akshare_helper.stock_history(symbol, start, end)
        ]
        if history:
            result[symbol] = history
    return result


def fetch_board_component_quotes(board: Board, limit: int = 50) -> List[BoardComponentQuote]:
    snapshot = akshare_helper.board_member_snapshot(board.code, category=board.category, limit=limit)
    total_turnover = sum(item.get("turnover", 0.0) for item in snapshot) or 1.0
    quotes: List[BoardComponentQuote] = []
    for item in snapshot:
        turnover = float(item.get("turnover", 0.0))
        quotes.append(
            BoardComponentQuote(
                board=board.code,
                category=board.category,
                symbol=str(item.get("symbol", "")),
                name=str(item.get("name", "")),
                last_price=float(item.get("price", 0.0)),
                pct_change=float(item.get("pct_change", 0.0)),
                turnover=turnover,
                turnover_rate=float(item.get("turnover_rate", 0.0)),
                turnover_share=turnover / total_turnover,
            )
        )
    return quotes


def identify_leader_snapshots(board: Board, top_n: int = 3) -> List[LeaderSnapshot]:
    quotes = fetch_board_component_quotes(board)
    quotes.sort(key=lambda item: item.pct_change, reverse=True)
    leaders: List[LeaderSnapshot] = []
    for quote in quotes[:top_n]:
        leaders.append(
            LeaderSnapshot(
                board=board.code,
                category=board.category,
                symbol=quote.symbol,
                name=quote.name,
                pct_change=quote.pct_change,
                turnover_share=quote.turnover_share,
                limit_up_streak=0,  # Placeholder; requires dedicated连板数据接口.
            )
        )
    return leaders
