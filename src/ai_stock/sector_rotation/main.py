"""Entry point for the sector rotation workflow."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from . import config as config_module
from .config import AnalysisConfig
from .data import board_data, board_hot, board_money, board_price, stock_data
from .db.database import Database
from .db.writer import write_results
from .factors import capital_factor, hype_factor, leader_factor, rotation_factor, trend_factor
from .models import rps_predict, strong_board
from .reports import daily_report, visualization
from .strategy import board_selection, position_control, stock_selection
from .utils import akshare_helper, logger


def _collect_board_members(codes: Iterable[str]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for code in codes:
        members = board_data.Board(code=code, name=akshare_helper.get_board(code).name)
        mapping[code] = board_data.list_board_members(members)
    return mapping


def run_daily_analysis(
    cfg: Optional[AnalysisConfig] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, object]:
    """Execute the full analysis tree and optionally persist the outcome."""

    cfg = cfg or AnalysisConfig.daily_defaults()
    log = logger.get_logger(__name__)
    log.info(
        "Running sector rotation analysis for %s to %s",
        cfg.start_date.isoformat(),
        cfg.end_date.isoformat(),
    )

    boards = board_data.list_boards(limit=cfg.board_count)
    board_codes = [board.code for board in boards]

    price_history = board_price.fetch_board_prices(board_codes, cfg.start_date, cfg.end_date)
    money_flow = board_money.fetch_money_flow(board_codes, cfg.start_date, cfg.end_date)
    hot_metrics = board_hot.fetch_board_hot(board_codes, cfg.start_date, cfg.end_date)

    board_members = _collect_board_members(board_codes)
    all_stock_symbols = {symbol for symbols in board_members.values() for symbol in symbols}
    stock_history = stock_data.fetch_stock_data(all_stock_symbols, cfg.start_date, cfg.end_date)

    trend_scores = trend_factor.calculate_trend_factor(price_history)
    hype_scores = hype_factor.calculate_hype_factor(hot_metrics)
    capital_scores = capital_factor.calculate_capital_factor(money_flow)
    rotation_scores = rotation_factor.calculate_rotation_factor(trend_scores, capital_scores, hype_scores)

    board_rankings = strong_board.rank_boards(
        trend_scores, hype_scores, capital_scores, rotation_scores, cfg.factor_weights
    )

    top_selection = board_selection.select_top_boards(board_rankings, top_n=min(3, len(board_rankings)))
    leaders = leader_factor.identify_leaders(board_members, stock_history)
    leader_picks = stock_selection.select_leaders(top_selection, leaders, cfg.leaders_per_board)

    allocations = position_control.allocate_equally(cfg.initial_cash, top_selection)
    predictions = rps_predict.predict_next_session(rotation_scores)

    report_text = daily_report.build_daily_report(
        cfg.end_date, top_selection, leader_picks, allocations, predictions
    )
    heatmap = visualization.rotation_heatmap(top_selection)

    if db_path is not None:
        db = Database(db_path)
        write_results(db, cfg.end_date, top_selection, leader_picks)

    log.info("Report generated with %d boards", len(top_selection))

    return {
        "config": asdict(cfg),
        "selected_boards": [asdict(score) for score in top_selection],
        "allocations": allocations,
        "leaders": {board: [asdict(candidate) for candidate in picks] for board, picks in leader_picks.items()},
        "predictions": predictions,
        "report": report_text,
        "heatmap": heatmap,
    }
