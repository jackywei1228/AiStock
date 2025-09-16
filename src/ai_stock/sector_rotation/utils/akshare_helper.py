"""AKShare data access helpers with graceful fallbacks.

The helper sits between the domain logic and the "akshare" package to
provide deterministic fallbacks when network access is unavailable.
"""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Dict, Iterable, Iterator, List, Optional, Sequence

try:  # pragma: no cover - exercised in integration scenarios.
    import akshare as ak
except ImportError:  # pragma: no cover - unit tests rely on the fallback path.
    ak = None  # type: ignore


LOGGER = logging.getLogger(__name__)
AK_AVAILABLE = ak is not None


@dataclass(frozen=True)
class BoardInfo:
    code: str
    name: str
    category: str = "industry"


@dataclass(frozen=True)
class SyntheticBoard:
    code: str
    name: str
    category: str
    members: List[str]


_SYNTHETIC_BOARDS: Dict[str, Dict[str, SyntheticBoard]] = {
    "industry": {
        "BK001": SyntheticBoard("BK001", "半导体", "industry", ["600703", "600584", "688396"]),
        "BK002": SyntheticBoard("BK002", "新能源", "industry", ["300750", "002594", "002812"]),
        "BK003": SyntheticBoard("BK003", "消费电子", "industry", ["000100", "002475", "603986"]),
        "BK004": SyntheticBoard("BK004", "医药", "industry", ["600276", "600196", "002007"]),
        "BK005": SyntheticBoard("BK005", "券商", "industry", ["600030", "600837", "601901"]),
        "BK006": SyntheticBoard("BK006", "新能源汽车", "industry", ["002594", "601238", "300750"]),
    },
    "concept": {
        "BK101": SyntheticBoard("BK101", "数据要素", "concept", ["002154", "300170", "688288"]),
        "BK102": SyntheticBoard("BK102", "算力", "concept", ["300496", "000977", "603019"]),
        "BK103": SyntheticBoard("BK103", "人形机器人", "concept", ["002031", "300126", "000625"]),
    },
}

_DEFAULT_MAX_MEMBERS = 50
_DEFAULT_CALENDAR_SPAN = 365


# ---------------------------------------------------------------------------
# Board metadata helpers


def list_boards(
    limit: Optional[int] = None,
    categories: Optional[Sequence[str]] = None,
) -> List[BoardInfo]:
    cats = tuple(categories) if categories is not None else ("industry",)
    boards: List[BoardInfo] = []
    for category in cats:
        boards.extend(_load_board_infos(category))
    boards.sort(key=lambda info: (info.category, info.code))
    if limit is not None:
        boards = boards[:limit]
    return boards


def list_industry_boards(limit: Optional[int] = None) -> List[BoardInfo]:
    return list_boards(limit=limit, categories=("industry",))


def list_concept_boards(limit: Optional[int] = None) -> List[BoardInfo]:
    return list_boards(limit=limit, categories=("concept",))


def get_board_info(code: str) -> BoardInfo:
    mapping = _board_info_index()
    try:
        return mapping[code]
    except KeyError as exc:
        raise KeyError(f"Unknown board code '{code}'") from exc


def board_members(code: str, category: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
    info = get_board_info(code)
    if category and category != info.category:
        info = BoardInfo(code=info.code, name=info.name, category=category)
    limit = limit or _DEFAULT_MAX_MEMBERS
    if AK_AVAILABLE:
        try:
            if info.category == "concept":
                df = ak.stock_board_concept_cons_em(symbol=info.name)
            else:
                df = ak.stock_board_industry_cons_em(symbol=info.name)
        except Exception as exc:  # pragma: no cover - network dependent.
            LOGGER.warning("Falling back to synthetic members for %s: %s", code, exc)
        else:
            members = [
                str(item).strip()
                for item in df.get("代码", [])
                if str(item).strip()
            ]
            if members:
                return members[:limit]
    synthetic = _SYNTHETIC_BOARDS.get(info.category, {}).get(code)
    if synthetic is None:
        raise KeyError(f"No member data for board '{code}'")
    return synthetic.members[:limit]


def board_member_snapshot(code: str, category: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, float]]:
    info = get_board_info(code)
    if category and category != info.category:
        info = BoardInfo(code=info.code, name=info.name, category=category)
    limit = limit or _DEFAULT_MAX_MEMBERS
    if AK_AVAILABLE:
        try:
            if info.category == "concept":
                df = ak.stock_board_concept_cons_em(symbol=info.name)
            else:
                df = ak.stock_board_industry_cons_em(symbol=info.name)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to fetch live component snapshot for %s: %s", code, exc)
        else:
            records: List[Dict[str, float]] = []
            for _, row in df.head(limit).iterrows():
                symbol = str(row.get("代码") or "").strip()
                name = str(row.get("名称") or "").strip()
                if not symbol or not name:
                    continue
                records.append(
                    {
                        "symbol": symbol,
                        "name": name,
                        "price": _to_float(row.get("最新价")),
                        "pct_change": _to_float(row.get("涨跌幅")),
                        "turnover": _to_float(row.get("成交额")),
                        "turnover_rate": _to_float(row.get("换手率")),
                    }
                )
            if records:
                return records
    return _synthetic_component_snapshot(info, limit)


@lru_cache(maxsize=4)
def _load_board_infos(category: str) -> List[BoardInfo]:
    if category not in _SYNTHETIC_BOARDS:
        raise ValueError(f"Unsupported board category: {category}")
    if AK_AVAILABLE:
        try:
            if category == "concept":
                df = ak.stock_board_concept_name_em()
            else:
                df = ak.stock_board_industry_name_em()
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to fetch %s board list, using fallback: %s", category, exc)
        else:
            if "排名" in df.columns:
                df = df.sort_values(by="排名")
            boards: List[BoardInfo] = []
            for _, row in df.iterrows():
                code = str(row.get("板块代码") or row.get("代码") or "").strip()
                name = str(row.get("板块名称") or row.get("名称") or "").strip()
                if not code or not name:
                    continue
                boards.append(BoardInfo(code=code, name=name, category=category))
            if boards:
                return boards
    return [
        BoardInfo(code=board.code, name=board.name, category=board.category)
        for board in _SYNTHETIC_BOARDS[category].values()
    ]


@lru_cache(maxsize=1)
def _board_info_index() -> Dict[str, BoardInfo]:
    mapping: Dict[str, BoardInfo] = {}
    for category in _SYNTHETIC_BOARDS.keys():
        for info in _load_board_infos(category):
            mapping[info.code] = info
    return mapping


# ---------------------------------------------------------------------------
# Trading calendar helpers


def iter_trading_days(start: date, end: date) -> Iterator[date]:
    if start > end:
        return
    calendar = _load_trading_calendar()
    if not calendar:
        yield from _iter_simple_days(start, end)
        return
    if start < calendar[0] or end > calendar[-1]:
        yield from _iter_simple_days(start, end)
        return
    for trading_day in calendar:
        if trading_day < start:
            continue
        if trading_day > end:
            break
        yield trading_day


@lru_cache(maxsize=1)
def _load_trading_calendar() -> List[date]:
    if AK_AVAILABLE:
        try:
            df = ak.tool_trade_date_hist_sina()
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Unable to fetch trading calendar, using naive dates: %s", exc)
        else:
            days: List[date] = []
            for value in df.get("trade_date", []):
                parsed = _parse_date(value)
                if parsed is not None:
                    days.append(parsed)
            if days:
                days.sort()
                return days
    today = date.today()
    start = today - timedelta(days=_DEFAULT_CALENDAR_SPAN)
    return [start + timedelta(days=offset) for offset in range(_DEFAULT_CALENDAR_SPAN * 2)]


# ---------------------------------------------------------------------------
# Board level history helpers


def board_price_history(
    code: str,
    start: date,
    end: date,
    board_name: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, float]]:
    info = get_board_info(code)
    if category and category != info.category:
        info = BoardInfo(code=info.code, name=info.name, category=category)
    name = board_name or info.name
    start_key = start.strftime("%Y%m%d")
    end_key = end.strftime("%Y%m%d")
    return _board_price_cache(info.category, code, name, start_key, end_key, start, end)


def board_money_flow(
    code: str,
    start: date,
    end: date,
    board_name: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, float]]:
    info = get_board_info(code)
    if category and category != info.category:
        info = BoardInfo(code=info.code, name=info.name, category=category)
    name = board_name or info.name
    return _board_money_cache(info.category, code, name, start, end)


def board_hot_metrics(
    code: str,
    start: date,
    end: date,
    board_name: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Dict[str, float]]:
    info = get_board_info(code)
    if category and category != info.category:
        info = BoardInfo(code=info.code, name=info.name, category=category)
    history = board_price_history(info.code, start, end, board_name=board_name or info.name, category=info.category)
    metrics = []
    for item in history:
        metrics.append(
            {
                "date": item["date"],
                "hot_score": item.get("turnover_rate", 0.0),
                "mentions": item.get("volume", 0.0),
            }
        )
    return metrics


@lru_cache(maxsize=128)
def _board_price_cache(
    category: str,
    code: str,
    name: str,
    start_key: str,
    end_key: str,
    start: date,
    end: date,
) -> List[Dict[str, float]]:
    if AK_AVAILABLE:
        try:
            if category == "concept":
                df = ak.stock_board_concept_hist_em(
                    symbol=name,
                    start_date=start_key,
                    end_date=end_key,
                    period="daily",
                    adjust="",
                )
            else:
                df = ak.stock_board_industry_hist_em(
                    symbol=name,
                    start_date=start_key,
                    end_date=end_key,
                    period="日k",
                    adjust="",
                )
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Fallback to synthetic price history for %s: %s", code, exc)
        else:
            records: List[Dict[str, float]] = []
            for _, row in df.iterrows():
                trading_day = _parse_date(row.get("日期"))
                if trading_day is None or trading_day < start or trading_day > end:
                    continue
                records.append(
                    {
                        "date": trading_day,
                        "close": _to_float(row.get("收盘")),
                        "change_pct": _to_float(row.get("涨跌幅")),
                        "change_amount": _to_float(row.get("涨跌额")),
                        "volume": _to_float(row.get("成交量")),
                        "turnover": _to_float(row.get("成交额")),
                        "turnover_rate": _to_float(row.get("换手率")),
                    }
                )
            if records:
                records.sort(key=lambda item: item["date"])
                return records
    return _synthetic_board_history(code, start, end)


@lru_cache(maxsize=128)
def _board_money_cache(
    category: str,
    code: str,
    name: str,
    start: date,
    end: date,
) -> List[Dict[str, float]]:
    if AK_AVAILABLE:
        try:
            if category == "concept":
                df = ak.stock_concept_fund_flow_hist(symbol=name)
            else:
                df = ak.stock_sector_fund_flow_hist(symbol=name)
        except Exception as exc:  # pragma: no cover
            LOGGER.warning("Fallback to synthetic money flow for %s: %s", code, exc)
        else:
            records: List[Dict[str, float]] = []
            for _, row in df.iterrows():
                trading_day = _parse_date(row.get("日期"))
                if trading_day is None or trading_day < start or trading_day > end:
                    continue
                main = _to_float(row.get("主力净流入-净额"))
                medium = _to_float(row.get("中单净流入-净额"))
                small = _to_float(row.get("小单净流入-净额"))
                records.append(
                    {
                        "date": trading_day,
                        "net_inflow": main + medium + small,
                        "main_inflow": main,
                    }
                )
            if records:
                records.sort(key=lambda item: item["date"])
                return records
    return _synthetic_board_money_flow(code, start, end)


# ---------------------------------------------------------------------------
# Stock level helpers


def stock_history(symbol: str, start: date, end: date) -> List[Dict[str, float]]:
    start_key = start.strftime("%Y%m%d")
    end_key = end.strftime("%Y%m%d")
    return _stock_history_cache(symbol, start_key, end_key, start, end)


def stock_money_flow(symbol: str, start: date, end: date) -> List[Dict[str, float]]:
    market = _detect_market(symbol)
    if AK_AVAILABLE and market is not None:
        try:
            df = ak.stock_individual_fund_flow(stock=symbol[:6], market=market)
        except Exception as exc:  # pragma: no cover
            LOGGER.debug("Stock %s money flow unavailable, using synthetic data: %s", symbol, exc)
        else:
            records: List[Dict[str, float]] = []
            for _, row in df.iterrows():
                trading_day = _parse_date(row.get("日期"))
                if trading_day is None or trading_day < start or trading_day > end:
                    continue
                records.append(
                    {
                        "date": trading_day,
                        "main_inflow": _to_float(row.get("主力净流入-净额")),
                        "large_inflow": _to_float(row.get("超大单净流入-净额")),
                        "medium_inflow": _to_float(row.get("中单净流入-净额")),
                        "small_inflow": _to_float(row.get("小单净流入-净额")),
                    }
                )
            if records:
                records.sort(key=lambda item: item["date"])
                return records
    return _synthetic_stock_money_flow(symbol, start, end)


def stock_hot_rank(limit: int = 20) -> List[Dict[str, object]]:
    if AK_AVAILABLE:
        try:
            df = ak.stock_hot_rank_em()
        except Exception as exc:  # pragma: no cover
            LOGGER.debug("Hot rank unavailable, using synthetic data: %s", exc)
        else:
            records: List[Dict[str, object]] = []
            for _, row in df.head(limit).iterrows():
                records.append(
                    {
                        "rank": int(_to_float(row.get("当前排名"))),
                        "symbol": str(row.get("代码") or "").strip(),
                        "name": str(row.get("股票名称") or "").strip(),
                        "last_price": _to_float(row.get("最新价")),
                        "change_pct": _to_float(row.get("涨跌幅")),
                    }
                )
            if records:
                return records
    return _synthetic_hot_rank(limit)


def stock_news(symbol: str, limit: int = 10) -> List[Dict[str, object]]:
    if AK_AVAILABLE:
        try:
            df = ak.stock_news_em(symbol=symbol)
        except Exception as exc:  # pragma: no cover
            LOGGER.debug("News fetch failed for %s: %s", symbol, exc)
        else:
            records: List[Dict[str, object]] = []
            for _, row in df.head(limit).iterrows():
                published = row.get("发布时间")
                timestamp = str(published).strip() if published is not None else ""
                records.append(
                    {
                        "symbol": symbol,
                        "title": str(row.get("新闻标题") or "").strip(),
                        "published_at": timestamp,
                        "source": str(row.get("文章来源") or "").strip(),
                        "url": str(row.get("新闻链接") or "").strip(),
                    }
                )
            if records:
                return records
    return []


@lru_cache(maxsize=256)
def _stock_history_cache(
    symbol: str,
    start_key: str,
    end_key: str,
    start: date,
    end: date,
) -> List[Dict[str, float]]:
    if AK_AVAILABLE:
        market = _detect_market(symbol)
        if market is not None:
            try:
                df = ak.stock_zh_a_hist(symbol=symbol[:6], start_date=start_key, end_date=end_key, adjust="")
            except Exception as exc:  # pragma: no cover
                LOGGER.debug("Unable to fetch history for %s: %s", symbol, exc)
            else:
                records: List[Dict[str, float]] = []
                for _, row in df.iterrows():
                    trading_day = _parse_date(row.get("日期"))
                    if trading_day is None or trading_day < start or trading_day > end:
                        continue
                    records.append(
                        {
                            "date": trading_day,
                            "close": _to_float(row.get("收盘")),
                            "turnover_rate": _to_float(row.get("换手率")),
                        }
                    )
                if records:
                    records.sort(key=lambda item: item["date"])
                    return records
    return _synthetic_stock_history(symbol, start, end)


# ---------------------------------------------------------------------------
# Fallback generators


def seed_for(key: str) -> int:
    return abs(hash(key)) % (2**32)


def random_walk(base: float, step: float, days: int, seed: int) -> List[float]:
    rng = random.Random(seed)
    price = base
    series = []
    for _ in range(days):
        change = rng.uniform(-step, step)
        price = max(1.0, price * (1 + change))
        series.append(round(price, 2))
    return series


def _synthetic_board_history(code: str, start: date, end: date) -> List[Dict[str, float]]:
    days = list(_iter_simple_days(start, end))
    seed = seed_for(f"price-{code}")
    closes = random_walk(base=100.0, step=0.05, days=len(days), seed=seed)
    rng = random.Random(seed)
    records: List[Dict[str, float]] = []
    prev_close = closes[0]
    for idx, trading_day in enumerate(days):
        close = closes[idx]
        change_amount = close - prev_close if idx else 0.0
        change_pct = (change_amount / prev_close * 100) if idx and prev_close else 0.0
        volume = round(1_000_000 * (1 + rng.uniform(-0.3, 0.3)), 2)
        turnover = round(close * volume / 10_000, 2)
        turnover_rate = round(max(0.5, rng.uniform(0.5, 8.0)), 2)
        records.append(
            {
                "date": trading_day,
                "close": close,
                "change_pct": change_pct,
                "change_amount": change_amount,
                "volume": volume,
                "turnover": turnover,
                "turnover_rate": turnover_rate,
            }
        )
        prev_close = close
    return records


def _synthetic_board_money_flow(code: str, start: date, end: date) -> List[Dict[str, float]]:
    days = list(_iter_simple_days(start, end))
    seed = seed_for(f"money-{code}")
    rng = random.Random(seed)
    records: List[Dict[str, float]] = []
    for trading_day in days:
        main = rng.uniform(-5_000_000, 5_000_000)
        medium = rng.uniform(-1_000_000, 1_000_000)
        small = rng.uniform(-500_000, 500_000)
        records.append(
            {
                "date": trading_day,
                "net_inflow": round(main + medium + small, 2),
                "main_inflow": round(main, 2),
            }
        )
    return records


def _synthetic_component_snapshot(info: BoardInfo, limit: int) -> List[Dict[str, float]]:
    seed = seed_for(f"snapshot-{info.code}")
    rng = random.Random(seed)
    members = board_members(info.code, category=info.category, limit=limit)
    records: List[Dict[str, float]] = []
    for symbol in members:
        price = round(rng.uniform(5, 120), 2)
        pct_change = round(rng.uniform(-5, 10), 2)
        turnover = round(rng.uniform(10_000_000, 200_000_000), 2)
        records.append(
            {
                "symbol": symbol,
                "name": symbol,
                "price": price,
                "pct_change": pct_change,
                "turnover": turnover,
                "turnover_rate": round(rng.uniform(0.5, 12.0), 2),
            }
        )
    return records


def _synthetic_stock_history(symbol: str, start: date, end: date) -> List[Dict[str, float]]:
    days = list(_iter_simple_days(start, end))
    seed = seed_for(f"stock-{symbol}")
    closes = random_walk(base=50.0, step=0.08, days=len(days), seed=seed)
    rng = random.Random(seed)
    records: List[Dict[str, float]] = []
    for idx, trading_day in enumerate(days):
        records.append(
            {
                "date": trading_day,
                "close": closes[idx],
                "turnover_rate": round(rng.uniform(0.5, 10.0), 3),
            }
        )
    return records


def _synthetic_stock_money_flow(symbol: str, start: date, end: date) -> List[Dict[str, float]]:
    days = list(_iter_simple_days(start, end))
    seed = seed_for(f"stock-money-{symbol}")
    rng = random.Random(seed)
    records: List[Dict[str, float]] = []
    for trading_day in days:
        main = rng.uniform(-2_000_000, 2_000_000)
        records.append(
            {
                "date": trading_day,
                "main_inflow": round(main, 2),
                "large_inflow": round(main * rng.uniform(0.4, 0.8), 2),
                "medium_inflow": round(rng.uniform(-500_000, 500_000), 2),
                "small_inflow": round(rng.uniform(-200_000, 200_000), 2),
            }
        )
    return records


def _synthetic_hot_rank(limit: int) -> List[Dict[str, object]]:
    seed = seed_for("hot-rank")
    rng = random.Random(seed)
    boards = list(_SYNTHETIC_BOARDS["industry"].values())
    members = [symbol for board in boards for symbol in board.members]
    records: List[Dict[str, object]] = []
    for rank, symbol in enumerate(members[:limit], start=1):
        records.append(
            {
                "rank": rank,
                "symbol": symbol,
                "name": symbol,
                "last_price": round(rng.uniform(5, 60), 2),
                "change_pct": round(rng.uniform(-5, 8), 2),
            }
        )
    return records


# ---------------------------------------------------------------------------
# Shared utilities


def _iter_simple_days(start: date, end: date) -> Iterator[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _detect_market(symbol: str) -> Optional[str]:
    digits = "".join(ch for ch in symbol if ch.isdigit())
    if len(digits) != 6:
        return None
    if digits.startswith(("4", "8", "9")):
        return "bj"
    if digits.startswith("6") or digits.startswith("9"):
        return "sh"
    return "sz"


def _to_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text or text in {"-", "--"}:
        return 0.0
    text = text.replace(",", "")
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return 0.0


def _parse_date(value: object) -> Optional[date]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
