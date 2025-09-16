"""Board popularity proxies and sentiment data."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Iterable, List

from .board_data import Board
from ..utils import akshare_helper


@dataclass(frozen=True)
class BoardHotMetric:
    board: str
    category: str
    date: date
    hot_score: float
    mentions: float


@dataclass(frozen=True)
class HotRankItem:
    rank: int
    symbol: str
    name: str
    last_price: float
    change_pct: float


@dataclass(frozen=True)
class NewsItem:
    symbol: str
    title: str
    published_at: str
    source: str
    url: str


def fetch_board_hot(boards: Iterable[Board], start: date, end: date) -> Dict[str, List[BoardHotMetric]]:
    result: Dict[str, List[BoardHotMetric]] = {}
    for board in boards:
        metrics = [
            BoardHotMetric(
                board=board.code,
                category=board.category,
                date=item["date"],
                hot_score=float(item.get("hot_score", 0.0)),
                mentions=float(item.get("mentions", 0.0)),
            )
            for item in akshare_helper.board_hot_metrics(
                board.code,
                start,
                end,
                board_name=board.name,
                category=board.category,
            )
        ]
        if metrics:
            result[board.code] = metrics
    return result


def fetch_hot_rank(limit: int = 20) -> List[HotRankItem]:
    items = []
    for payload in akshare_helper.stock_hot_rank(limit=limit):
        items.append(
            HotRankItem(
                rank=int(payload.get("rank", 0)),
                symbol=str(payload.get("symbol", "")),
                name=str(payload.get("name", "")),
                last_price=float(payload.get("last_price", 0.0)),
                change_pct=float(payload.get("change_pct", 0.0)),
            )
        )
    return items


def fetch_sentiment_news(symbols: Iterable[str], per_symbol: int = 5) -> Dict[str, List[NewsItem]]:
    news: Dict[str, List[NewsItem]] = {}
    for symbol in symbols:
        articles = [
            NewsItem(
                symbol=payload.get("symbol", symbol),
                title=str(payload.get("title", "")),
                published_at=str(payload.get("published_at", "")),
                source=str(payload.get("source", "")),
                url=str(payload.get("url", "")),
            )
            for payload in akshare_helper.stock_news(symbol, limit=per_symbol)
        ]
        if articles:
            news[symbol] = articles
    return news
