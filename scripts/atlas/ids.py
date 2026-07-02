"""稳定条目 id 生成与校验。"""

from __future__ import annotations

import re
from typing import Any

from .constants import ID_PREFIXES


ID_PATTERN = re.compile(r"^(?P<prefix>[a-z]+)_(?P<number>\d{4,})$")


def expected_id_prefix(library: str) -> str:
    return ID_PREFIXES[library]


def format_entry_id(library: str, number: int) -> str:
    return f"{expected_id_prefix(library)}_{number:04d}"


def entry_id_number(library: str, entry_id: str) -> int | None:
    match = ID_PATTERN.match(entry_id)
    if not match or match.group("prefix") != expected_id_prefix(library):
        return None
    return int(match.group("number"))


def entry_id_is_valid(library: str, entry_id: str) -> bool:
    return entry_id_number(library, entry_id) is not None


def max_entry_id_number(library: str, items: list[dict[str, Any]]) -> int:
    numbers = [
        number
        for item in items
        if isinstance(item.get("id"), str)
        for number in [entry_id_number(library, item["id"])]
        if number is not None
    ]
    return max(numbers, default=-1)


def next_entry_id(library: str, used_ids: set[str], start: int = 0) -> tuple[str, int]:
    """从 start 往后找第一个未占用 id，避免人工估算造成冲突。"""

    number = start
    while True:
        entry_id = format_entry_id(library, number)
        if entry_id not in used_ids:
            return entry_id, number
        number += 1


def with_id_first(item: dict[str, Any]) -> dict[str, Any]:
    if "id" not in item:
        return dict(item)
    return {"id": item["id"], **{key: value for key, value in item.items() if key != "id"}}

