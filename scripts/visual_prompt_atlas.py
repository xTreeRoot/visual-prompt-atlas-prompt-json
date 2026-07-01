#!/usr/bin/env python3
"""CLI tools for the Visual Prompt Atlas dataset."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "references"

LIBRARIES = {
    "actions": ("璃夏_动作Prompt库v2.json", "actionLibrary"),
    "outfits": ("璃夏_服装Prompt库v2.json", "clothesLibrary"),
    "expressions": ("璃夏_表情Prompt库v2.json", "expressionLibrary"),
    "scenes": ("璃夏_空间背景Prompt库v2.json", "scenes"),
}

COMPATIBILITY_FILE = "scene_clothes_compatibility.json"

POSE_HINTS = {
    "站": ["站", "站立", "倚靠", "靠栏杆", "行走", "步行"],
    "坐": ["坐", "坐于", "坐在", "倚坐", "靠床", "床边", "沙发", "椅", "长椅", "课桌"],
    "躺": ["躺", "躺卧", "床面"],
    "跪": ["跪", "跪坐"],
    "蹲": ["蹲", "蹲坐"],
    "跳": ["跳", "跳跃"],
    "走": ["走", "行走", "步行"],
    "跑": ["跑", "奔跑"],
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def load_atlas(base: Path = REFERENCES) -> dict[str, Any]:
    atlas: dict[str, Any] = {}
    for name, (filename, key) in LIBRARIES.items():
        data = read_json(base / filename)
        atlas[name] = data[key]
    atlas["compatibility"] = read_json(base / COMPATIBILITY_FILE)
    return atlas


def flatten_text(value: Any) -> str:
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

    compat = atlas["compatibility"]
    result["compatibility"] = {
        "compatible_scene_count": len(compat.get("compatible", {})),
        "incompatible_scene_count": len(compat.get("incompatible", {})),
        "confidence_scene_count": len(compat.get("confidence", {})),
    }

    if args.json:
        write_json(result)
    else:
        for name, info in result.items():
            print(f"{name}:")
            for key, value in info.items():
                print(f"  {key}: {value}")
    return 0


def check_entry(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_atlas(base: Path = REFERENCES) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for library, (filename, key) in LIBRARIES.items():
        path = base / filename
        check_entry(path.exists(), errors, f"missing file: {path}")
        if not path.exists():
            continue
        try:
            data = read_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid json in {filename}: {exc}")
            continue
        items = data.get(key)
        check_entry(isinstance(items, list), errors, f"{filename}: {key} must be a list")
        if not isinstance(items, list):
            continue
        check_entry(bool(items), errors, f"{filename}: {key} is empty")
        for index, item in enumerate(items):
            prefix = f"{filename}[{index}]"
            check_entry(isinstance(item, dict), errors, f"{prefix}: entry must be an object")
            if not isinstance(item, dict):
                continue
            if library == "scenes":
                check_entry(isinstance(item.get("scene"), str), errors, f"{prefix}: scene must be a string")
                check_entry(
                    isinstance(item.get("scene_summary"), str),
                    errors,
                    f"{prefix}: scene_summary must be a string",
                )
                check_entry(isinstance(item.get("category"), str), errors, f"{prefix}: category must be a string")
                check_entry(
                    isinstance(item.get("allowed_actions"), list),
                    errors,
                    f"{prefix}: allowed_actions must be a list",
                )
                check_entry(
                    isinstance(item.get("forbidden_actions"), list),
                    errors,
                    f"{prefix}: forbidden_actions must be a list",
                )
                if not isinstance(item.get("coreMoods"), dict):
                    warnings.append(f"{prefix}: coreMoods is missing or not an object")
                continue

            check_entry(isinstance(item.get("description"), str), errors, f"{prefix}: description must be a string")
            check_entry(isinstance(item.get("keywords"), list), errors, f"{prefix}: keywords must be a list")
            check_entry(isinstance(item.get("mood"), dict), errors, f"{prefix}: mood must be an object")
            if library == "actions":
                for section in ("interaction", "dynamic", "pose"):
                    check_entry(isinstance(item.get(section), dict), errors, f"{prefix}: {section} must be an object")
            elif library == "outfits":
                check_entry(isinstance(item.get("occasion"), list), errors, f"{prefix}: occasion must be a list")
            elif library == "expressions":
                for section in ("eyes", "mouth", "cheek", "overall"):
                    check_entry(isinstance(item.get(section), dict), errors, f"{prefix}: {section} must be an object")

    compat_path = base / COMPATIBILITY_FILE
    check_entry(compat_path.exists(), errors, f"missing file: {compat_path}")
    if compat_path.exists():
        try:
            compat = read_json(compat_path)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid json in {COMPATIBILITY_FILE}: {exc}")
        else:
            for key in ("compatible", "incompatible", "confidence", "metadata"):
                check_entry(isinstance(compat.get(key), dict), errors, f"{COMPATIBILITY_FILE}: {key} must be an object")

    return errors, warnings


def command_validate(args: argparse.Namespace) -> int:
    errors, warnings = validate_atlas()
    result = {"ok": not errors, "errors": errors, "warnings": warnings}
    if args.json:
        write_json(result)
    else:
        if errors:
            print("ERRORS:")
            for error in errors:
                print(f"- {error}")
        if warnings:
            print("WARNINGS:")
            for warning in warnings:
                print(f"- {warning}")
        if not errors:
            print("Atlas validation passed.")
    return 1 if errors else 0


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
            print(f"[{row['library']}:{row['index']}] score={row['score']} {row['title']}")
            print(f"  {row['description']}")
    return 0


def outfit_tags(outfit: dict[str, Any], compatibility: dict[str, Any]) -> set[str]:
    known_tags: set[str] = set()
    for section in ("compatible", "incompatible"):
        for values in compatibility.get(section, {}).values():
            known_tags.update(str(value) for value in values)
    text = flatten_text(outfit)
    return {tag for tag in known_tags if tag and tag in text}


def scene_rule(scene_name: str, compatibility: dict[str, Any], section: str) -> tuple[str | None, set[str]]:
    rules = compatibility.get(section, {})
    if scene_name in rules:
        return scene_name, set(str(value) for value in rules[scene_name])
    for key, values in rules.items():
        if key in scene_name or scene_name in key:
            return key, set(str(value) for value in values)
    return None, set()


def compatibility_status(scene: dict[str, Any], outfit: dict[str, Any], compatibility: dict[str, Any]) -> tuple[str, str]:
    scene_name = str(scene.get("scene", ""))
    tags = outfit_tags(outfit, compatibility)
    incompatible_key, incompatible = scene_rule(scene_name, compatibility, "incompatible")
    compatible_key, compatible = scene_rule(scene_name, compatibility, "compatible")

    bad = sorted(tags & incompatible)
    if bad:
        return "incompatible", f"{incompatible_key}: {', '.join(bad)}"

    good = sorted(tags & compatible)
    if good:
        return "compatible", f"{compatible_key}: {', '.join(good)}"

    if compatible:
        return "unknown", f"{compatible_key}: no known matching outfit tag"
    return "unknown", "no compatibility rule for this scene"


def allowed_action_score(scene: dict[str, Any], action: dict[str, Any]) -> int:
    text = flatten_text(action)
    pose = action.get("pose") if isinstance(action.get("pose"), dict) else {}
    pose_type = str(pose.get("type", ""))
    score = 0
    for action_name in scene.get("allowed_actions", []) or []:
        action_name = str(action_name)
        if action_name and (action_name in text or action_name == pose_type):
            score += 4
    for forbidden in scene.get("forbidden_actions", []) or []:
        forbidden = str(forbidden)
        if forbidden and (forbidden in text or forbidden == pose_type):
            return -100
    return score


def scene_pose_score(scene: dict[str, Any], pose_type: str | None) -> int:
    if not pose_type:
        return 0
    hints = POSE_HINTS.get(pose_type, [pose_type])
    text = flatten_text(
        {
            "scene": scene.get("scene"),
            "scene_summary": scene.get("scene_summary"),
            "best_action": scene.get("best_action"),
            "allowed_actions": scene.get("allowed_actions"),
            "forbidden_actions": scene.get("forbidden_actions"),
        }
    )
    forbidden_text = flatten_text(scene.get("forbidden_actions"))
    if any(hint in forbidden_text for hint in hints):
        return -20
    return 16 if any(hint in text for hint in hints) else 0


def candidates(
    items: list[dict[str, Any]],
    score_func: Any,
    fallback_score_func: Any | None = None,
    top: int = 40,
) -> list[tuple[int, int, dict[str, Any]]]:
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for index, item in enumerate(items):
        score = score_func(item)
        if score >= 0:
            scored.append((score, index, item))
    if not scored and fallback_score_func:
        for index, item in enumerate(items):
            score = fallback_score_func(item)
            if score >= 0:
                scored.append((score, index, item))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return scored[:top]


def choose(scored: list[tuple[int, int, dict[str, Any]]], rng: random.Random) -> tuple[int, dict[str, Any]]:
    if not scored:
        raise RuntimeError("no candidates available")
    shortlist = scored[: min(12, len(scored))]
    weights = [max(1, score + 1) for score, _, _ in shortlist]
    picked = rng.choices(shortlist, weights=weights, k=1)[0]
    return picked[1], picked[2]


def compact_prompt(scene: dict[str, Any], outfit: dict[str, Any], action: dict[str, Any], expression: dict[str, Any]) -> str:
    parts = [
        str(scene.get("scene_summary", "")).strip(),
        str(outfit.get("description", "")).strip(),
        str(action.get("description", "")).strip(),
        str(expression.get("description", "")).strip(),
        "真实照片感，空间透视一致，人物与环境光影统一，动作自然，服装材质清晰，背景细节真实。",
    ]
    return " ".join(part for part in parts if part)


def command_compose(args: argparse.Namespace) -> int:
    atlas = load_atlas()
    rng = random.Random(args.seed)
    outputs: list[dict[str, Any]] = []

    scene_terms = normalize_terms(args.scene_name)

    for _ in range(args.count):
        def scene_score(item: dict[str, Any], include_mood: bool = True) -> int:
            if args.scene_category and item.get("category") != args.scene_category:
                return -1
            if scene_terms and not item_has_any(item, scene_terms):
                return -1
            score = scene_pose_score(item, args.pose_type)
            if score < 0:
                return -1
            if include_mood:
                score += mood_value(item, args.mood) * 5
            return score

        scene_candidates = candidates(
            atlas["scenes"],
            lambda item: scene_score(item, include_mood=True),
            fallback_score_func=lambda item: scene_score(item, include_mood=False),
        )
        scene_index, scene = choose(scene_candidates, rng)

        def outfit_score(item: dict[str, Any]) -> int:
            score = 0
            if args.mood:
                value = mood_value(item, args.mood)
                if value < args.min_mood:
                    return -1
                score += value * 5
            if args.occasion and args.occasion not in normalize_terms(item.get("occasion")):
                return -1
            status, _ = compatibility_status(scene, item, atlas["compatibility"])
            if status == "incompatible":
                return -1
            if args.strict_compatible and status != "compatible":
                return -1
            if status == "compatible":
                score += 12
            return score

        outfit_index, outfit = choose(candidates(atlas["outfits"], outfit_score, lambda item: 0), rng)
        compat_status, compat_note = compatibility_status(scene, outfit, atlas["compatibility"])

        def action_score(item: dict[str, Any]) -> int:
            score = allowed_action_score(scene, item)
            if score < 0:
                return -1
            if args.mood:
                value = mood_value(item, args.mood)
                if value < args.min_mood:
                    return -1
                score += value * 5
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

        action_index, action = choose(candidates(atlas["actions"], action_score, lambda item: 0), rng)

        def expression_score(item: dict[str, Any]) -> int:
            if args.mood:
                value = mood_value(item, args.mood)
                if value < args.min_mood:
                    return -1
                return value * 5
            return int(item.get("overall", {}).get("intensity", 0) or 0)

        expression_index, expression = choose(candidates(atlas["expressions"], expression_score, lambda item: 0), rng)

        outputs.append(
            {
                "scene": scene.get("scene"),
                "scene_index": scene_index,
                "scene_category": scene.get("category"),
                "outfit_index": outfit_index,
                "action_index": action_index,
                "expression_index": expression_index,
                "compatibility": compat_status,
                "compatibility_note": compat_note,
                "outfit": outfit.get("description"),
                "action": action.get("description"),
                "expression": expression.get("description"),
                "prompt": compact_prompt(scene, outfit, action, expression),
            }
        )

    if args.json:
        write_json(outputs if args.count != 1 else outputs[0])
    else:
        for index, output in enumerate(outputs, start=1):
            if len(outputs) > 1:
                print(f"## Prompt {index}")
            print(f"Scene: {output['scene']} ({output['scene_category']})")
            print(f"Outfit: {output['outfit']}")
            print(f"Action: {output['action']}")
            print(f"Expression: {output['expression']}")
            print(f"Compatibility: {output['compatibility']} - {output['compatibility_note']}")
            print(f"Prompt: {output['prompt']}")
            if index != len(outputs):
                print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visual Prompt Atlas dataset tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stats = subparsers.add_parser("stats", help="Show dataset counts and top labels")
    stats.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    stats.set_defaults(func=command_stats)

    validate = subparsers.add_parser("validate", help="Validate required files and schema shape")
    validate.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    validate.set_defaults(func=command_validate)

    search = subparsers.add_parser("search", help="Search prompt entries")
    search.add_argument("library", choices=["all", *LIBRARIES.keys()])
    search.add_argument("query", nargs="?", help="Search text")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--mood")
    search.add_argument("--min-mood", type=int, default=1)
    search.add_argument("--category", help="Scene category filter")
    search.add_argument("--occasion", help="Outfit occasion filter")
    search.add_argument("--pose-type", help="Action pose.type filter, e.g. 站 or 坐")
    search.add_argument("--interaction-min", type=int, help="Minimum action interaction.level")
    search.add_argument("--dynamic-max", type=int, help="Maximum action dynamic.intensity")
    search.add_argument("--full", action="store_true", help="Include full source item in JSON output")
    search.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    search.set_defaults(func=command_search)

    compose = subparsers.add_parser("compose", help="Compose realistic image prompts from the atlas")
    compose.add_argument("--mood", help="Preferred mood label, e.g. 温柔, 甜美, 清纯")
    compose.add_argument("--min-mood", type=int, default=3, help="Minimum mood score when --mood is used")
    compose.add_argument("--scene-name", action="append", help="Scene name or text filter; repeatable")
    compose.add_argument("--scene-category", help="Scene category filter")
    compose.add_argument("--occasion", help="Outfit occasion filter")
    compose.add_argument("--pose-type", help="Action pose.type filter")
    compose.add_argument("--interaction-min", type=int, help="Minimum action interaction.level")
    compose.add_argument("--dynamic-max", type=int, help="Maximum action dynamic.intensity")
    compose.add_argument("--strict-compatible", action="store_true", help="Require known scene-outfit compatibility")
    compose.add_argument("--count", type=int, default=1)
    compose.add_argument("--seed", type=int, default=7)
    compose.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    compose.set_defaults(func=command_compose)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
