"""Stock level data used when picking leaders."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from .board_data import Board
from ..utils import akshare_helper


@dataclass(frozen=True)
class StockBar:
    symbol: str
    date: date
    close: float
    turnover_rate: float
    turnover: float
    pct_change: float


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
                turnover=item.get("turnover", 0.0),
                pct_change=item.get("pct_change", 0.0),
            )
            for item in akshare_helper.stock_history(symbol, start, end)
        ]
        if history:
            result[symbol] = history
    return result


def fetch_board_component_quotes(
    board: Board,
    limit: int = 50,
    history: Optional[Mapping[str, List[StockBar]]] = None,
    target_date: Optional[date] = None,
    members: Optional[Sequence[str]] = None,
) -> List[BoardComponentQuote]:
    snapshot = akshare_helper.board_member_snapshot(board.code, category=board.category, limit=limit)
    if members is not None:
        snapshot = [item for item in snapshot if item.get("symbol") in set(members)]

    raw_items: List[Dict[str, float]] = []
    for item in snapshot:
        symbol = str(item.get("symbol", "")).strip()
        name = str(item.get("name", "")).strip()
        if not symbol:
            continue

        price = float(item.get("price", 0.0) or 0.0)
        pct_change = float(item.get("pct_change", 0.0) or 0.0)
        turnover = float(item.get("turnover", 0.0) or 0.0)
        turnover_rate = float(item.get("turnover_rate", 0.0) or 0.0)

        if history is not None and target_date is not None:
            bar = _select_bar(history.get(symbol, []), target_date)
            if bar is not None:
                price = bar.close
                pct_change = bar.pct_change
                turnover = bar.turnover
                turnover_rate = bar.turnover_rate
            else:
                akshare_helper.LOGGER.debug(
                    "No historical quote for %s on %s; using snapshot values", symbol, target_date
                )

        raw_items.append(
            {
                "symbol": symbol,
                "name": name,
                "price": price,
                "pct_change": pct_change,
                "turnover": turnover,
                "turnover_rate": turnover_rate,
            }
        )

    total_turnover = sum(max(0.0, item["turnover"]) for item in raw_items) or 1.0
    quotes: List[BoardComponentQuote] = []
    for item in raw_items:
        quotes.append(
            BoardComponentQuote(
                board=board.code,
                category=board.category,
                symbol=item["symbol"],
                name=item["name"],
                last_price=item["price"],
                pct_change=item["pct_change"],
                turnover=item["turnover"],
                turnover_rate=item["turnover_rate"],
                turnover_share=item["turnover"] / total_turnover if total_turnover else 0.0,
            )
        )
    return quotes


def _select_bar(bars: Sequence[StockBar], target: date) -> Optional[StockBar]:
    chosen: Optional[StockBar] = None
    for bar in bars:
        if bar.date > target:
            continue
        if chosen is None or bar.date > chosen.date:
            chosen = bar
    return chosen


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
