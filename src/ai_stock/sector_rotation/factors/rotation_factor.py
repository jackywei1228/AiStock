"""Rotation factor built on top of the other factor outputs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .capital_factor import CapitalComponents
from .hype_factor import HypeComponents
from .leader_factor import LeaderComponents
from .trend_factor import TrendComponents


@dataclass(frozen=True)
class RotationComponents:
    catch_up: float
    capital_follow_through: float
    hype_transmission: float
    technical_setup: float
    leader_confirmation: float

    @property
    def score(self) -> float:
        return (
            self.catch_up * 40
            + self.capital_follow_through * 60
            + self.hype_transmission * 50
            + self.technical_setup * 30
            + self.leader_confirmation * 20
        )


def calculate_rotation_factor(
    trend: Dict[str, TrendComponents],
    capital: Dict[str, CapitalComponents],
    hype: Dict[str, HypeComponents],
    leaders: Dict[str, LeaderComponents] | None = None,
) -> Dict[str, RotationComponents]:
    """Combine factor components into a rotation readiness indicator."""

    results: Dict[str, RotationComponents] = {}
    for board, trend_component in trend.items():
        capital_component = capital.get(board)
        hype_component = hype.get(board)
        if capital_component is None or hype_component is None:
            continue

        catch_up = _catch_up_component(trend_component, capital_component)
        capital_follow = max(0.0, capital_component.continuity)
        hype_transmission = _hype_transmission_component(trend_component, hype_component)
        technical_setup = max(0.0, trend_component.ma_signal)

        leader_confirmation = 0.0
        if leaders and board in leaders:
            leader = leaders[board]
            leader_confirmation = (
                leader.limit_up_count * 0.5 + leader.leader_turnover_share
            )

        results[board] = RotationComponents(
            catch_up=catch_up,
            capital_follow_through=capital_follow,
            hype_transmission=hype_transmission,
            technical_setup=technical_setup,
            leader_confirmation=leader_confirmation,
        )
    return results


def _catch_up_component(trend: TrendComponents, capital: CapitalComponents) -> float:
    if trend.return_10d >= 0:
        return 0.0
    if capital.avg_net_inflow <= 0:
        return 0.0
    return min(abs(trend.return_10d), capital.avg_net_inflow / 1_000_000)


def _hype_transmission_component(trend: TrendComponents, hype: HypeComponents) -> float:
    momentum_gap = max(0.0, hype.hot_trend - trend.return_5d)
    hot_change = max(0.0, hype.hot_change)
    return momentum_gap + hot_change
