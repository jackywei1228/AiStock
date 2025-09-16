"""Scheduler helpers for the sector rotation workflow.

The helpers in this module keep scheduling lightweight for development
by relying on the standard library only.  They can be used directly in a
long-running Python process or swapped into ``cron`` / enterprise
orchestrators (Airflow, Prefect, etc.) without code changes.
"""
from __future__ import annotations

import argparse
import logging
import time as time_module
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Optional

from ..config import AnalysisConfig
from ..main import run_daily_analysis


DEFAULT_DB_PATH = Path("sector_rotation_results.sqlite")
WINDOW_START = time(15, 30)
WINDOW_END = time(16, 0)


def run(config: Optional[AnalysisConfig] = None, db_path: Optional[Path] = None) -> None:
    """Trigger the daily pipeline and persist results once."""

    db_path = db_path or DEFAULT_DB_PATH
    run_daily_analysis(cfg=config, db_path=db_path)


def run_daily_window(
    config: Optional[AnalysisConfig] = None,
    db_path: Optional[Path] = None,
    start: time = WINDOW_START,
    end: time = WINDOW_END,
    idle_ceiling: int = 300,
) -> None:
    """Run the analysis once per day inside the given intraday window."""

    log = logging.getLogger(__name__)
    log.info(
        "Daily scheduler active. Window %s-%s",
        start.strftime("%H:%M"),
        end.strftime("%H:%M"),
    )

    while True:
        now = datetime.now()
        current = now.time()

        if start <= current <= end:
            log.info("Window reached (%s). Launching analysis run.", now.isoformat(timespec="seconds"))
            run(config=config, db_path=db_path)
            sleep_seconds = _seconds_until_next_window(start)
            log.info("Run finished. Sleeping %.0f seconds until next window.", sleep_seconds)
            time_module.sleep(sleep_seconds)
            continue

        sleep_seconds = _seconds_until_start(start)
        sleep_value = min(float(idle_ceiling), sleep_seconds)
        log.debug(
            "Outside window (%s). Sleeping %.0f seconds before re-check.",
            now.isoformat(timespec="seconds"),
            sleep_value,
        )
        time_module.sleep(sleep_value)


def _seconds_until_start(start: time) -> float:
    now = datetime.now()
    candidate = datetime.combine(now.date(), start)
    if now.time() >= start:
        candidate += timedelta(days=1)
    return max(60.0, (candidate - now).total_seconds())


def _seconds_until_next_window(start: time) -> float:
    now = datetime.now()
    tomorrow = datetime.combine(now.date(), start) + timedelta(days=1)
    return max(300.0, (tomorrow - now).total_seconds())


def _parse_time(value: str) -> time:
    try:
        hour, minute = value.split(":")
        return time(int(hour), int(minute))
    except ValueError as exc:  # pragma: no cover - defensive parsing
        raise argparse.ArgumentTypeError(f"Invalid time format '{value}', expected HH:MM") from exc


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Sector rotation daily scheduler")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to SQLite database")
    parser.add_argument("--once", action="store_true", help="Run immediately and exit")
    parser.add_argument("--start", type=_parse_time, default=WINDOW_START, help="Window start time (HH:MM)")
    parser.add_argument("--end", type=_parse_time, default=WINDOW_END, help="Window end time (HH:MM)")
    parser.add_argument(
        "--idle-ceiling",
        type=int,
        default=300,
        help="Maximum seconds to sleep between window checks",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    if args.once:
        run(db_path=args.db)
    else:
        run_daily_window(
            db_path=args.db,
            start=args.start,
            end=args.end,
            idle_ceiling=args.idle_ceiling,
        )


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
