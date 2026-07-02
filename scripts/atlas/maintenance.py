"""稳定 id 维护与新条目入库。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .constants import LIBRARIES, LIBRARY_LABELS, ROOT
from .data import entry_description, read_json, read_library_document, write_json, write_json_file
from .ids import (
    entry_id_is_valid,
    expected_id_prefix,
    format_entry_id,
    max_entry_id_number,
    next_entry_id,
    with_id_first,
)
from .validation import validate_entry_schema


def command_ids_backfill(args: argparse.Namespace) -> int:
    if args.write and args.dry_run:
        print("错误: --write 和 --dry-run 只能选择一个", file=sys.stderr)
        return 2

    dry_run = not args.write
    result: dict[str, Any] = {"dry_run": dry_run, "libraries": {}}

    for library in LIBRARIES:
        path, key, data, items = read_library_document(library)
        used_ids = {
            item["id"]
            for item in items
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        assigned: list[dict[str, Any]] = []
        changed = False

        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("id"), str) and entry_id_is_valid(library, item["id"]):
                reordered = with_id_first(item)
                if reordered != item:
                    items[index] = reordered
                    changed = True
                continue

            candidate = format_entry_id(library, index)
            if candidate in used_ids:
                candidate, _ = next_entry_id(library, used_ids, max_entry_id_number(library, items) + 1)
            used_ids.add(candidate)
            new_item = dict(item)
            new_item["id"] = candidate
            new_item = with_id_first(new_item)
            items[index] = new_item
            changed = True
            assigned.append(
                {
                    "index": index,
                    "id": candidate,
                    "description": entry_description(new_item),
                }
            )

        result["libraries"][library] = {
            "path": str(path.relative_to(ROOT)),
            "assigned": len(assigned),
            "changed": changed,
            "entries": assigned,
        }

        if changed and not dry_run:
            data[key] = items
            write_json_file(path, data)

    if args.json:
        write_json(result)
    else:
        mode = "预览" if dry_run else "写入"
        print(f"稳定 id 回填（{mode}）")
        for library, info in result["libraries"].items():
            print(f"{LIBRARY_LABELS[library]}: 分配={info['assigned']} 已变化={info['changed']}")
    return 0


def command_ids_next(args: argparse.Namespace) -> int:
    _, _, _, items = read_library_document(args.library)
    used_ids = {
        item["id"]
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    start = max_entry_id_number(args.library, items) + 1
    ids: list[str] = []
    for _ in range(args.count):
        entry_id, number = next_entry_id(args.library, used_ids, start)
        ids.append(entry_id)
        used_ids.add(entry_id)
        start = number + 1

    if args.json:
        write_json({"library": args.library, "ids": ids})
    else:
        for entry_id in ids:
            print(entry_id)
    return 0


def ingest_entries_from_payload(library: str, payload: Any) -> list[dict[str, Any]]:
    _, key = LIBRARIES[library]
    if isinstance(payload, dict) and isinstance(payload.get(key), list):
        payload = payload[key]
    elif isinstance(payload, dict):
        payload = [payload]

    if not isinstance(payload, list):
        raise ValueError("入库输入必须是对象、数组，或包含目标库顶层 key 的对象")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"入库条目 {index} 必须是对象")
        entries.append(dict(item))
    return entries


def command_ingest(args: argparse.Namespace) -> int:
    if args.write and args.dry_run:
        print("错误: --write 和 --dry-run 只能选择一个", file=sys.stderr)
        return 2

    dry_run = not args.write
    input_path = Path(args.input)
    try:
        payload = read_json(input_path)
        new_entries = ingest_entries_from_payload(args.library, payload)
        path, key, data, existing_items = read_library_document(args.library)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    existing_ids = {
        item["id"]
        for item in existing_items
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    used_ids = set(existing_ids)
    existing_descriptions = {
        entry_description(item)
        for item in existing_items
        if isinstance(item, dict) and entry_description(item)
    }
    batch_descriptions: set[str] = set()
    start = max_entry_id_number(args.library, existing_items) + 1
    accepted: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    for index, entry in enumerate(new_entries):
        item = dict(entry)
        prefix = f"{args.input}[{index}]"
        entry_id = item.get("id")
        if entry_id in (None, ""):
            entry_id, number = next_entry_id(args.library, used_ids, start)
            item["id"] = entry_id
            start = number + 1
        elif not isinstance(entry_id, str):
            errors.append(f"{prefix}: 提供 id 时必须是字符串")
        elif not entry_id_is_valid(args.library, entry_id):
            errors.append(f"{prefix}: id 必须符合 {expected_id_prefix(args.library)}_0000 格式")

        entry_id = item.get("id")
        if isinstance(entry_id, str):
            if entry_id in used_ids:
                errors.append(f"{prefix}: id 重复 {entry_id}")
            used_ids.add(entry_id)

        description = entry_description(item)
        if description:
            if not args.allow_duplicate_description and description in existing_descriptions:
                errors.append(f"{prefix}: description 已在 {LIBRARY_LABELS[args.library]} 中存在")
            if not args.allow_duplicate_description and description in batch_descriptions:
                errors.append(f"{prefix}: 入库批次内 description 重复")
            batch_descriptions.add(description)

        validate_entry_schema(args.library, item, prefix, errors, warnings)
        item = with_id_first(item)
        accepted.append(item)
        summaries.append({"id": item.get("id"), "description": description})

    result = {
        "library": args.library,
        "dry_run": dry_run,
        "target": str(path.relative_to(ROOT)),
        "accepted": 0 if errors else len(accepted),
        "errors": errors,
        "warnings": warnings,
        "entries": summaries if not errors else [],
    }

    if errors:
        if args.json:
            write_json(result)
        else:
            print("错误:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            if warnings:
                print("警告:", file=sys.stderr)
                for warning in warnings:
                    print(f"- {warning}", file=sys.stderr)
        return 2

    if not dry_run:
        data[key] = [*existing_items, *accepted]
        write_json_file(path, data)

    if args.json:
        write_json(result)
    else:
        mode = "预览" if dry_run else "写入"
        print(f"入库 {LIBRARY_LABELS[args.library]}（{mode}）: 接受={len(accepted)}")
        for entry in summaries:
            print(f"- {entry['id']}: {entry['description']}")
        if warnings:
            print("警告:")
            for warning in warnings:
                print(f"- {warning}")
    return 0

