"""Scheduler entry for the daily job."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..config import AnalysisConfig
from ..main import run_daily_analysis


DEFAULT_DB_PATH = Path("sector_rotation_results.sqlite")


def run(config: Optional[AnalysisConfig] = None, db_path: Optional[Path] = None) -> None:
    """Trigger the daily pipeline and persist results."""

    db_path = db_path or DEFAULT_DB_PATH
    run_daily_analysis(cfg=config, db_path=db_path)
