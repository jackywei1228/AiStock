"""Board price history sourced from AKShare with fallbacks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from .board_data import Board
from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardPriceBar:
    board: str
    category: str
    date: date
    close: float
    change_pct: float
    change_amount: float
    volume: float
    turnover: float
    turnover_rate: float
    ma5: float
    ma10: float


def fetch_board_prices(boards: Iterable[Board], start: date, end: date) -> Dict[str, List[BoardPriceBar]]:
    """Return market data for each requested board."""

    result: Dict[str, List[BoardPriceBar]] = {}
    for board in boards:
        history = akshare_helper.board_price_history(
            board.code,
            start,
            end,
            board_name=board.name,
            category=board.category,
        )
        closes = [item["close"] for item in history]
        bars: List[BoardPriceBar] = []
        for idx, item in enumerate(history):
            ma5 = _moving_average(closes, idx, 5)
            ma10 = _moving_average(closes, idx, 10)
            bars.append(
                BoardPriceBar(
                    board=board.code,
                    category=board.category,
                    date=item["date"],
                    close=item["close"],
                    change_pct=item.get("change_pct", 0.0),
                    change_amount=item.get("change_amount", 0.0),
                    volume=item.get("volume", 0.0),
                    turnover=item.get("turnover", 0.0),
                    turnover_rate=item.get("turnover_rate", 0.0),
                    ma5=ma5,
                    ma10=ma10,
                )
            )
        if bars:
            result[board.code] = bars
    return result


def _moving_average(values: List[float], idx: int, window: int) -> float:
    start_idx = max(0, idx - window + 1)
    subset = values[start_idx : idx + 1]
    if not subset:
        return 0.0
    return sum(subset) / len(subset)
