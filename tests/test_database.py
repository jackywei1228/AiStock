import json
import sqlite3
from datetime import date

import pytest

from ai_stock.sector_rotation.db.database import Database
from ai_stock.sector_rotation.db.writer import write_results
from ai_stock.sector_rotation.factors.leader_factor import LeaderCandidate
from ai_stock.sector_rotation.models.strong_board import BoardScore


def test_sqlite_backend_persists_results(tmp_path):
    db_path = tmp_path / "results.sqlite"
    database = Database(db_path)

    board_scores = [BoardScore(board="BK001", score=1.23, breakdown={"trend": 0.5})]
    leaders = {
        "BK001": [LeaderCandidate(symbol="AAA", return_pct=0.1, avg_turnover=2.0)]
    }

    write_results(database, date(2024, 1, 1), board_scores, leaders)

    with sqlite3.connect(db_path) as conn:
        board_row = conn.execute(
            "SELECT board_code, score, breakdown FROM board_scores"
        ).fetchone()
        leader_row = conn.execute(
            "SELECT board_code, symbol, return_pct, avg_turnover FROM leader_candidates"
        ).fetchone()

    assert board_row is not None
    assert board_row[0] == "BK001"
    assert board_row[1] == pytest.approx(1.23)
    assert json.loads(board_row[2]) == {"trend": 0.5}

    assert leader_row is not None
    assert leader_row[0] == "BK001"
    assert leader_row[1] == "AAA"
    assert leader_row[2] == pytest.approx(0.1)
    assert leader_row[3] == pytest.approx(2.0)
