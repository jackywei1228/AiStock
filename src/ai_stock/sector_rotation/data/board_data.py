"""Synthetic board data access."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from ..utils import akshare_helper


@dataclass(frozen=True)
class Board:
    code: str
    name: str

    def member_symbols(self) -> List[str]:
        return akshare_helper.get_board(self.code).members


def list_boards(limit: int | None = None) -> List[Board]:
    """Return a deterministic set of boards.

    The helper keeps the API shape similar to the real project where
    external data would be queried.
    """

    boards = [Board(code=board.code, name=board.name) for board in akshare_helper.list_boards()]
    if limit is not None:
        boards = boards[:limit]
    return boards


def list_board_members(board: Board) -> List[str]:
    return list(board.member_symbols())
