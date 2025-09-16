"""Capital flow factors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..data.board_money import BoardMoneyFlow, StockMoneyFlow
from ..utils.indicators import moving_average


@dataclass(frozen=True)
class CapitalComponents:
    avg_net_inflow: float
    main_ratio: float
    continuity: float

    @property
    def score(self) -> float:
        return (
            self.avg_net_inflow / 1_000_000
            + self.main_ratio * 20
            + self.continuity * 5
        )


def calculate_capital_factor(money_flow: Dict[str, List[BoardMoneyFlow]]) -> Dict[str, CapitalComponents]:
    results: Dict[str, CapitalComponents] = {}
    for board, flows in money_flow.items():
        if not flows:
            continue
        avg_net = moving_average(flow.net_inflow for flow in flows)
        avg_main = moving_average(flow.main_inflow for flow in flows)
        main_ratio = 0.0 if avg_net == 0 else avg_main / avg_net
        continuity = _positive_run_ratio([flow.net_inflow for flow in flows])
        results[board] = CapitalComponents(
            avg_net_inflow=avg_net,
            main_ratio=main_ratio,
            continuity=continuity,
        )
    return results


def calculate_stock_capital_factor(stock_flows: Dict[str, List[StockMoneyFlow]]) -> Dict[str, float]:
    ratios: Dict[str, float] = {}
    for symbol, flows in stock_flows.items():
        if not flows:
            continue
        avg_main = moving_average(flow.main_inflow for flow in flows)
        avg_total = moving_average(
            flow.main_inflow + flow.medium_inflow + flow.small_inflow for flow in flows
        )
        ratios[symbol] = 0.0 if avg_total == 0 else avg_main / avg_total
    return ratios


def _positive_run_ratio(values: List[float]) -> float:
    if not values:
        return 0.0
    streak = 0
    max_streak = 0
    for value in values:
        if value > 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak / len(values)
