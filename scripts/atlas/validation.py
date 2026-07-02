"""图谱数据校验。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .constants import LIBRARIES, REFERENCES
from .data import read_json, write_json
from .ids import entry_id_is_valid, expected_id_prefix


def check_entry(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_entry_schema(
    library: str,
    item: dict[str, Any],
    prefix: str,
    errors: list[str],
    warnings: list[str],
    require_id: bool = True,
) -> None:
    """校验单条记录的必需字段，不在这里做业务筛选。"""

    entry_id = item.get("id")
    if require_id:
        check_entry(isinstance(entry_id, str), errors, f"{prefix}: id 必须是字符串")
        if isinstance(entry_id, str):
            check_entry(
                entry_id_is_valid(library, entry_id),
                errors,
                f"{prefix}: id 必须符合 {expected_id_prefix(library)}_0000 格式",
            )

    if library == "scenes":
        check_entry(isinstance(item.get("scene"), str), errors, f"{prefix}: scene 必须是字符串")
        check_entry(
            isinstance(item.get("scene_summary"), str),
            errors,
            f"{prefix}: scene_summary 必须是字符串",
        )
        check_entry(isinstance(item.get("category"), str), errors, f"{prefix}: category 必须是字符串")
        check_entry(
            isinstance(item.get("allowed_actions"), list),
            errors,
            f"{prefix}: allowed_actions 必须是数组",
        )
        check_entry(
            isinstance(item.get("forbidden_actions"), list),
            errors,
            f"{prefix}: forbidden_actions 必须是数组",
        )
        if not isinstance(item.get("coreMoods"), dict):
            warnings.append(f"{prefix}: coreMoods 缺失或不是对象")
        if "compatible_outfit_occasions" in item:
            check_entry(
                isinstance(item.get("compatible_outfit_occasions"), list),
                errors,
                f"{prefix}: compatible_outfit_occasions 必须是数组",
            )
        if "forbidden_outfit_keywords" in item:
            check_entry(
                isinstance(item.get("forbidden_outfit_keywords"), list),
                errors,
                f"{prefix}: forbidden_outfit_keywords 必须是数组",
            )
        return

    check_entry(isinstance(item.get("description"), str), errors, f"{prefix}: description 必须是字符串")
    check_entry(isinstance(item.get("keywords"), list), errors, f"{prefix}: keywords 必须是数组")
    check_entry(isinstance(item.get("mood"), dict), errors, f"{prefix}: mood 必须是对象")
    if library == "actions":
        for section in ("interaction", "dynamic", "pose"):
            check_entry(isinstance(item.get(section), dict), errors, f"{prefix}: {section} 必须是对象")
        if "required_scene_terms" in item:
            check_entry(
                isinstance(item.get("required_scene_terms"), list),
                errors,
                f"{prefix}: required_scene_terms 必须是数组",
            )
    elif library == "outfits":
        check_entry(isinstance(item.get("occasion"), list), errors, f"{prefix}: occasion 必须是数组")
    elif library == "expressions":
        for section in ("eyes", "mouth", "cheek", "overall"):
            check_entry(isinstance(item.get(section), dict), errors, f"{prefix}: {section} 必须是对象")


def validate_atlas(base: Path = REFERENCES) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for library, (filename, key) in LIBRARIES.items():
        path = base / filename
        check_entry(path.exists(), errors, f"缺少文件: {path}")
        if not path.exists():
            continue
        try:
            data = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{filename}: JSON 格式无效: {exc}")
            continue
        items = data.get(key)
        check_entry(isinstance(items, list), errors, f"{filename}: {key} 必须是数组")
        if not isinstance(items, list):
            continue
        check_entry(bool(items), errors, f"{filename}: {key} 不能为空")
        seen_ids: dict[str, int] = {}
        for index, item in enumerate(items):
            prefix = f"{filename}[{index}]"
            check_entry(isinstance(item, dict), errors, f"{prefix}: 条目必须是对象")
            if not isinstance(item, dict):
                continue
            validate_entry_schema(library, item, prefix, errors, warnings)
            entry_id = item.get("id")
            if isinstance(entry_id, str):
                if entry_id in seen_ids:
                    errors.append(f"{prefix}: id 重复 {entry_id}，首次出现在 index {seen_ids[entry_id]}")
                else:
                    seen_ids[entry_id] = index

    return errors, warnings


def command_validate(args: argparse.Namespace) -> int:
    errors, warnings = validate_atlas()
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        write_json(result)
    else:
        if errors:
            print("错误:")
            for error in errors:
                print(f"- {error}")
        if warnings:
            print("警告:")
            for warning in warnings:
                print(f"- {warning}")
        if not errors:
            print("图谱校验通过。")
    return 1 if errors else 0
