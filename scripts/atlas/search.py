"""统计与检索命令。"""

from __future__ import annotations

import argparse
from typing import Any

from .constants import LIBRARIES, LIBRARY_LABELS, STAT_LABELS
from .data import (
    entry_description,
    entry_title,
    flatten_text,
    load_atlas,
    mood_value,
    normalize_terms,
    top_counter,
    write_json,
)


def command_stats(args: argparse.Namespace) -> int:
    atlas = load_atlas()
    result: dict[str, Any] = {}
    for name in ("actions", "outfits", "expressions", "scenes"):
        items = atlas[name]
        result[name] = {"count": len(items)}
        if name == "scenes":
            result[name]["top_categories"] = top_counter(items, "category")
            result[name]["top_moods"] = top_counter(items, "coreMoods")
        else:
            result[name]["top_moods"] = top_counter(items, "mood")
            result[name]["top_keywords"] = top_counter(items, "keywords")
        if name == "outfits":
            result[name]["top_occasions"] = top_counter(items, "occasion")

    if args.json:
        write_json(result)
    else:
        for name, info in result.items():
            print(f"{LIBRARY_LABELS[name]}:")
            for key, value in info.items():
                print(f"  {STAT_LABELS.get(key, key)}: {value}")
    return 0


def search_score(library: str, item: dict[str, Any], query: str | None, args: argparse.Namespace) -> int:
    score = 0
    text = flatten_text(item).casefold()
    if query:
        query_folded = query.casefold()
        if query_folded not in text:
            return -1
        score += 10
        title = entry_title(library, item).casefold()
        description = entry_description(item).casefold()
        if query_folded in title:
            score += 20
        if query_folded in description:
            score += 12
        if any(query_folded in str(keyword).casefold() for keyword in item.get("keywords", [])):
            score += 8

    if args.mood:
        value = mood_value(item, args.mood)
        if value < args.min_mood:
            return -1
        score += value * 5

    if args.category:
        if str(item.get("category", "")) != args.category:
            return -1
        score += 8

    if args.occasion:
        occasions = normalize_terms(item.get("occasion"))
        if args.occasion not in occasions:
            return -1
        score += 8

    if args.pose_type:
        pose = item.get("pose") if isinstance(item.get("pose"), dict) else {}
        if pose.get("type") != args.pose_type:
            return -1
        score += 8

    if args.interaction_min is not None:
        interaction = item.get("interaction") if isinstance(item.get("interaction"), dict) else {}
        if int(interaction.get("level", 0) or 0) < args.interaction_min:
            return -1
        score += int(interaction.get("level", 0) or 0)

    if args.dynamic_max is not None:
        dynamic = item.get("dynamic") if isinstance(item.get("dynamic"), dict) else {}
        if int(dynamic.get("intensity", 0) or 0) > args.dynamic_max:
            return -1
        score += max(0, 6 - int(dynamic.get("intensity", 0) or 0))

    return score


def command_search(args: argparse.Namespace) -> int:
    atlas = load_atlas()
    libraries = list(LIBRARIES) if args.library == "all" else [args.library]
    rows: list[dict[str, Any]] = []
    for library in libraries:
        for index, item in enumerate(atlas[library]):
            score = search_score(library, item, args.query, args)
            if score < 0:
                continue
            rows.append(
                {
                    "library": library,
                    "index": index,
                    "id": item.get("id"),
                    "score": score,
                    "title": entry_title(library, item),
                    "description": entry_description(item),
                    "item": item if args.full else None,
                }
            )
    rows.sort(key=lambda row: (-row["score"], row["library"], row["index"]))
    rows = rows[: args.limit]

    if args.json:
        if not args.full:
            for row in rows:
                row.pop("item", None)
        write_json(rows)
    else:
        for row in rows:
            entry_id = row.get("id") or "未分配id"
            library_label = LIBRARY_LABELS.get(str(row["library"]), str(row["library"]))
            print(f"[{library_label}:{entry_id}@{row['index']}] 分数={row['score']} {row['title']}")
            print(f"  {row['description']}")
    return 0

