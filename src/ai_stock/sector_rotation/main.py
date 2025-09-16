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
from .utils import logger


def _collect_board_members(boards: Iterable[board_data.Board]) -> Dict[str, List[str]]:
    return {board.code: board_data.list_board_members(board) for board in boards}


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
    price_history = board_price.fetch_board_prices(boards, cfg.start_date, cfg.end_date)
    money_flow = board_money.fetch_money_flow(boards, cfg.start_date, cfg.end_date)
    hot_metrics = board_hot.fetch_board_hot(boards, cfg.start_date, cfg.end_date)

    board_members = _collect_board_members(boards)
    board_component_quotes = {
        board.code: stock_data.fetch_board_component_quotes(board)
        for board in boards
    }

    all_stock_symbols = {
        symbol for symbols in board_members.values() for symbol in symbols
    }
    for quotes in board_component_quotes.values():
        for quote in quotes:
            all_stock_symbols.add(quote.symbol)

    stock_history = stock_data.fetch_stock_data(all_stock_symbols, cfg.start_date, cfg.end_date)

    trend_scores = trend_factor.calculate_trend_factor(price_history)
    hype_scores = hype_factor.calculate_hype_factor(hot_metrics)
    capital_scores = capital_factor.calculate_capital_factor(money_flow)

    leader_candidates, leader_components = leader_factor.calculate_leader_factor(
        board_component_quotes,
        stock_history,
        top_n=cfg.leaders_per_board,
    )

    rotation_scores = rotation_factor.calculate_rotation_factor(
        trend_scores,
        capital_scores,
        hype_scores,
        leader_components,
    )

    board_rankings = strong_board.rank_boards(
        trend_scores,
        hype_scores,
        capital_scores,
        leader_components,
        cfg.factor_weights,
    )

    predictions = rps_predict.predict_next_session(rotation_scores, cfg.rotation_weights)
    rotation_candidates = rps_predict.predict_rotation_candidates(
        board_rankings,
        rotation_scores,
        cfg.rotation_weights,
        top_n=min(5, len(rotation_scores)),
    )

    top_selection = board_selection.select_primary_boards(
        board_rankings, top_n=min(3, len(board_rankings)), min_score=0.0
    )
    candidate_boards = board_selection.select_candidate_boards(
        rotation_candidates,
        exclude=[score.board for score in top_selection],
        top_n=min(2, len(rotation_candidates)),
        min_predicted=0.0,
    )

    leader_picks = stock_selection.select_leaders(top_selection, leader_candidates, cfg.leaders_per_board)

    regime = position_control.assess_market_regime(top_selection, predictions)
    allocations = position_control.allocate_portfolio(cfg.initial_cash, top_selection, regime)

    report_text = daily_report.build_daily_report(
        cfg.end_date,
        top_selection,
        leader_picks,
        allocations,
        predictions,
        rotation_candidates,
        candidate_boards,
        regime,
    )
    heatmap = visualization.rotation_heatmap(top_selection)
    factor_table = visualization.factor_table(
        trend_scores,
        hype_scores,
        capital_scores,
        leader_components,
        [score.board for score in board_rankings],
    )
    rotation_path = visualization.rotation_pathway(rotation_candidates, predictions)

    if db_path is not None:
        db = Database(db_path)
        write_results(db, cfg.end_date, top_selection, rotation_candidates, leader_picks)

    log.info("Report generated with %d boards", len(top_selection))

    return {
        "config": asdict(cfg),
        "selected_boards": [asdict(score) for score in top_selection],
        "allocations": allocations,
        "leaders": {board: [asdict(candidate) for candidate in picks] for board, picks in leader_picks.items()},
        "predictions": predictions,
        "rotation_candidates": [candidate.__dict__ for candidate in rotation_candidates],
        "candidate_boards": [candidate.__dict__ for candidate in candidate_boards],
        "regime": regime,
        "report": report_text,
        "heatmap": heatmap,
        "factor_table": factor_table,
        "rotation_path": rotation_path,
    }
