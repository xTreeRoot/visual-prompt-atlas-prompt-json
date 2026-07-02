"""JSON 读写与条目通用工具。"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .constants import LIBRARIES, REFERENCES


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_file(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def library_path_and_key(library: str, base: Path = REFERENCES) -> tuple[Path, str]:
    filename, key = LIBRARIES[library]
    return base / filename, key


def read_library_document(library: str, base: Path = REFERENCES) -> tuple[Path, str, dict[str, Any], list[dict[str, Any]]]:
    path, key = library_path_and_key(library, base)
    data = read_json(path)
    items = data.get(key)
    if not isinstance(items, list):
        raise ValueError(f"{path.name}: {key} 必须是数组")
    return path, key, data, items


def load_atlas(base: Path = REFERENCES) -> dict[str, Any]:
    atlas: dict[str, Any] = {}
    for name, (filename, key) in LIBRARIES.items():
        data = read_json(base / filename)
        atlas[name] = data[key]
    return atlas


def flatten_text(value: Any) -> str:
    """把 JSON 条目压平成可搜索文本。"""

    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        parts: list[str] = []
        for key, item in value.items():
            parts.append(str(key))
            parts.append(flatten_text(item))
        return " ".join(parts)
    return str(value)


def mood_value(item: dict[str, Any], mood: str | None) -> int:
    if not mood:
        return 0
    mood_map = item.get("mood")
    if isinstance(mood_map, dict):
        value = mood_map.get(mood, 0)
        return int(value) if isinstance(value, (int, float)) else 0
    core_moods = item.get("coreMoods")
    if isinstance(core_moods, dict) and mood in core_moods:
        return 5
    return 0


def entry_title(library: str, item: dict[str, Any]) -> str:
    if library == "scenes":
        return str(item.get("scene", ""))
    text = str(item.get("description", ""))
    return text[:44] + ("..." if len(text) > 44 else "")


def entry_description(item: dict[str, Any]) -> str:
    return str(item.get("description") or item.get("scene_summary") or "")


def normalize_terms(values: Any) -> set[str]:
    if not values:
        return set()
    if isinstance(values, str):
        values = [values]
    terms: set[str] = set()
    for value in values:
        if value is None:
            continue
        terms.add(str(value))
    return terms


def item_has_any(item: dict[str, Any], terms: set[str]) -> bool:
    if not terms:
        return True
    text = flatten_text(item).casefold()
    return any(term.casefold() in text for term in terms)


def top_counter(items: list[dict[str, Any]], field: str, limit: int = 12) -> list[tuple[str, int]]:
    counter: Counter[str] = Counter()
    for item in items:
        value = item.get(field)
        if isinstance(value, dict):
            counter.update(str(key) for key in value)
        elif isinstance(value, list):
            counter.update(str(part) for part in value)
        elif value:
            counter[str(value)] += 1
    return counter.most_common(limit)

