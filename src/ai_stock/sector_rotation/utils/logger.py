"""Very small logging helper used across the pipeline."""
from __future__ import annotations

import logging
from typing import Optional


_LOGGERS = {}


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a module-level logger configured with sensible defaults."""

    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    _LOGGERS[name] = logger
    return logger
