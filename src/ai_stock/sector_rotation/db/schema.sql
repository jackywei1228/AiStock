-- Strong board scores with factor breakdown
CREATE TABLE IF NOT EXISTS strong_boards (
    run_date TEXT NOT NULL,
    board_name TEXT NOT NULL,
    score REAL NOT NULL,
    trend_score REAL NOT NULL,
    hype_score REAL NOT NULL,
    capital_score REAL NOT NULL,
    leader_score REAL NOT NULL,
    PRIMARY KEY (run_date, board_name)
);

-- Rotation candidates with breakout components
CREATE TABLE IF NOT EXISTS rps_candidates (
    run_date TEXT NOT NULL,
    board_name TEXT NOT NULL,
    rps_score REAL NOT NULL,
    relative_lag REAL NOT NULL,
    capital_spillover REAL NOT NULL,
    hype_spillover REAL NOT NULL,
    tech_ready REAL NOT NULL,
    PRIMARY KEY (run_date, board_name)
);

-- Leader stocks selected for each board
CREATE TABLE IF NOT EXISTS leaders (
    run_date TEXT NOT NULL,
    board_name TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    stock_name TEXT NOT NULL,
    is_leader INTEGER NOT NULL,
    strength REAL NOT NULL,
    PRIMARY KEY (run_date, board_name, stock_code)
);
