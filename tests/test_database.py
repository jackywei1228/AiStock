import sqlite3
from datetime import date

import pytest

from ai_stock.sector_rotation.db.database import Database
from ai_stock.sector_rotation.db.writer import write_results
from ai_stock.sector_rotation.factors.leader_factor import LeaderCandidate
from ai_stock.sector_rotation.models.rps_predict import RpsCandidate
from ai_stock.sector_rotation.models.strong_board import BoardScore


def test_sqlite_backend_persists_results(tmp_path):
    db_path = tmp_path / "results.sqlite"
    database = Database(db_path)

    board_scores = [
        BoardScore(
            board="BK001",
            score=1.23,
            breakdown={"trend": 0.5, "hype": 0.4, "capital": 0.3, "leader": 0.2},
        )
    ]
    rotation_candidates = [
        RpsCandidate(
            board="BK002",
            predicted=2.34,
            breakdown={
                "relative_lag": 0.7,
                "capital_spillover": 0.6,
                "hype_spillover": 0.5,
                "technical_readiness": 0.4,
            },
        )
    ]
    leaders = {
        "BK001": [
            LeaderCandidate(
                symbol="AAA",
                name="Alpha",
                return_pct=0.1,
                pct_change=9.9,
                turnover_share=0.12,
                is_limit_up=True,
            )
        ]
    }

    write_results(database, date(2024, 1, 1), board_scores, rotation_candidates, leaders)

    with sqlite3.connect(db_path) as conn:
        board_row = conn.execute(
            "SELECT board_name, score, trend_score, hype_score, capital_score, leader_score FROM strong_boards"
        ).fetchone()
        leader_row = conn.execute(
            "SELECT board_name, stock_code, stock_name, is_leader, strength FROM leaders"
        ).fetchone()
        rps_row = conn.execute(
            "SELECT board_name, rps_score, relative_lag, capital_spillover, hype_spillover, tech_ready FROM rps_candidates"
        ).fetchone()

    assert board_row is not None
    assert board_row[0] == "BK001"
    assert board_row[1] == pytest.approx(1.23)
    assert board_row[2] == pytest.approx(0.5)
    assert board_row[3] == pytest.approx(0.4)
    assert board_row[4] == pytest.approx(0.3)
    assert board_row[5] == pytest.approx(0.2)

    assert leader_row is not None
    assert leader_row[0] == "BK001"
    assert leader_row[1] == "AAA"
    assert leader_row[2] == "Alpha"
    assert leader_row[3] == 1
    expected_strength = leaders["BK001"][0].score
    assert leader_row[4] == pytest.approx(expected_strength)

    assert rps_row is not None
    assert rps_row[0] == "BK002"
    assert rps_row[1] == pytest.approx(2.34)
    assert rps_row[2] == pytest.approx(0.7)
    assert rps_row[3] == pytest.approx(0.6)
    assert rps_row[4] == pytest.approx(0.5)
    assert rps_row[5] == pytest.approx(0.4)
