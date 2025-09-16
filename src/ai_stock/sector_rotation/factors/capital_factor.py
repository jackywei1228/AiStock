"""Capital flow factors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..data.board_money import BoardMoneyFlow
from ..utils.indicators import moving_average


@dataclass(frozen=True)
class CapitalComponents:
    net_inflow: float
    main_inflow: float

    @property
    def score(self) -> float:
        blended = self.net_inflow * 0.6 + self.main_inflow * 0.4
        return blended / 1_000_000


def calculate_capital_factor(money_flow: Dict[str, List[BoardMoneyFlow]]) -> Dict[str, CapitalComponents]:
    results: Dict[str, CapitalComponents] = {}
    for board, flows in money_flow.items():
        avg_net = moving_average(flow.net_inflow for flow in flows)
        avg_main = moving_average(flow.main_inflow for flow in flows)
        results[board] = CapitalComponents(net_inflow=avg_net, main_inflow=avg_main)
    return results
