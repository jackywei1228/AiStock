-- Illustrative schema mirroring the JSON persistence helper.
CREATE TABLE IF NOT EXISTS board_scores (
    run_date TEXT NOT NULL,
    board_code TEXT NOT NULL,
    score REAL NOT NULL,
    breakdown TEXT,
    PRIMARY KEY (run_date, board_code)
);

CREATE TABLE IF NOT EXISTS leader_candidates (
    run_date TEXT NOT NULL,
    board_code TEXT NOT NULL,
    symbol TEXT NOT NULL,
    return_pct REAL NOT NULL,
    avg_turnover REAL NOT NULL,
    PRIMARY KEY (run_date, board_code, symbol)
);
