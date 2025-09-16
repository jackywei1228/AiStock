"""Persistence helpers supporting both JSON and SQLite backends."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable


_JSON_SUFFIXES = {".json", ".jsonl", ".ndjson"}
_SQLITE_TABLE_COLUMNS: Dict[str, Iterable[str]] = {
    "strong_boards": (
        "run_date",
        "board_name",
        "score",
        "trend_score",
        "hype_score",
        "capital_score",
        "leader_score",
    ),
    "rps_candidates": (
        "run_date",
        "board_name",
        "rps_score",
        "relative_lag",
        "capital_spillover",
        "hype_spillover",
        "tech_ready",
    ),
    "leaders": (
        "run_date",
        "board_name",
        "stock_code",
        "stock_name",
        "is_leader",
        "strength",
    ),
}
_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


@dataclass
class Database:
    path: Path
    engine: str = field(default="auto")

    def __post_init__(self) -> None:
        self.path = Path(self.path)
        if self.engine == "auto":
            suffix = self.path.suffix.lower()
            self.engine = "json" if suffix in _JSON_SUFFIXES else "sqlite"
        if self.engine not in {"json", "sqlite"}:
            raise ValueError(f"Unsupported engine '{self.engine}'")
        if self.engine == "sqlite":
            self._initialise_sqlite()

    def append(self, table: str, record: Dict[str, Any]) -> None:
        if self.engine == "json":
            self._append_json(table, record)
        else:
            self._append_sqlite(table, record)

    # JSON backend ---------------------------------------------------------
    def _load_json(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _append_json(self, table: str, record: Dict[str, Any]) -> None:
        payload = self._load_json()
        bucket = payload.setdefault(table, [])
        bucket.append(record)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    # SQLite backend -------------------------------------------------------
    def _initialise_sqlite(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        schema_sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        with sqlite3.connect(self.path) as conn:
            conn.executescript(schema_sql)

    def _append_sqlite(self, table: str, record: Dict[str, Any]) -> None:
        try:
            columns = tuple(_SQLITE_TABLE_COLUMNS[table])
        except KeyError as exc:
            raise ValueError(f"Unknown table '{table}' for sqlite backend") from exc

        values = []
        for column in columns:
            value = record.get(column)
            if column == "breakdown" and value is not None and not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)
            if column == "is_leader" and value is not None:
                value = int(bool(value))
            values.append(value)

        placeholders = ", ".join(["?"] * len(columns))
        column_list = ", ".join(columns)
        sql = f"INSERT OR REPLACE INTO {table} ({column_list}) VALUES ({placeholders})"

        with sqlite3.connect(self.path) as conn:
            conn.execute(sql, values)
            conn.commit()
