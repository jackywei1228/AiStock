"""Board metadata access built on top of AKShare."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from ..utils import akshare_helper


@dataclass(frozen=True)
class Board:
    code: str
    name: str
    category: str = "industry"

    def member_symbols(self, limit: Optional[int] = None) -> List[str]:
        return akshare_helper.board_members(self.code, category=self.category, limit=limit)


def list_boards(
    limit: int | None = None,
    categories: Iterable[str] | None = None,
) -> List[Board]:
    infos = akshare_helper.list_boards(limit=None, categories=tuple(categories) if categories is not None else None)
    boards = [Board(code=info.code, name=info.name, category=info.category) for info in infos]
    if limit is not None:
        boards = boards[:limit]
    return boards


def list_industry_boards(limit: int | None = None) -> List[Board]:
    return [
        Board(code=info.code, name=info.name, category=info.category)
        for info in akshare_helper.list_industry_boards(limit=limit)
    ]


def list_concept_boards(limit: int | None = None) -> List[Board]:
    return [
        Board(code=info.code, name=info.name, category=info.category)
        for info in akshare_helper.list_concept_boards(limit=limit)
    ]


def list_board_members(board: Board, limit: Optional[int] = None) -> List[str]:
    return list(board.member_symbols(limit=limit))
