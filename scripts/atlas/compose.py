"""提示词组合与场景适配启发式。"""

from __future__ import annotations

import argparse
import random
import sys
from typing import Any

from .constants import (
    COMPATIBILITY_LABELS,
    LIBRARY_LABELS,
)
from .data import flatten_text, item_has_any, load_atlas, mood_value, normalize_terms, write_json
from .errors import AtlasCliError
from .ids import entry_id_is_valid


def contains_any(text: str, terms: set[str]) -> bool:
    return any(term and term in text for term in terms)


def scene_outfit_occasions(scene: dict[str, Any]) -> set[str]:
    return normalize_terms(scene.get("compatible_outfit_occasions"))


def compatibility_status(scene: dict[str, Any], outfit: dict[str, Any]) -> tuple[str, str]:
    """判断场景和服装是否正向匹配；未知不等于冲突。"""

    scene_name = str(scene.get("scene", ""))
    outfit_text = flatten_text(outfit)

    forbidden_keywords = normalize_terms(scene.get("forbidden_outfit_keywords"))
    if contains_any(outfit_text, forbidden_keywords):
        matched = sorted(keyword for keyword in forbidden_keywords if keyword and keyword in outfit_text)
        return "incompatible", f"场景禁用服装关键词: {', '.join(matched)}"

    preferred = scene_outfit_occasions(scene)
    outfit_occasions = normalize_terms(outfit.get("occasion")) | normalize_terms(outfit.get("original_occasion"))
    matched_occasions = sorted(preferred & outfit_occasions)
    if matched_occasions:
        return "compatible", f"{scene_name}: 匹配场合 {', '.join(matched_occasions)}"

    if preferred:
        return "unknown", f"{scene_name}: 未匹配到服装场合"
    return "unknown", f"{scene_name}: 没有可用的场景服装启发式"


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


def action_scene_conflict(scene: dict[str, Any], action: dict[str, Any]) -> str | None:
    required_scene_terms = normalize_terms(action.get("required_scene_terms"))
    if not required_scene_terms:
        return None
    scene_text = flatten_text(
        {
            "scene": scene.get("scene"),
            "scene_summary": scene.get("scene_summary"),
            "scene_tags": scene.get("scene_tags"),
            "category": scene.get("category"),
        }
    )
    if not contains_any(scene_text, required_scene_terms):
        return "missing_required_scene_terms"
    return None


def action_fit_score(scene: dict[str, Any], action: dict[str, Any]) -> int:
    if action_scene_conflict(scene, action):
        return -1
    score = allowed_action_score(scene, action)
    if score < 0:
        return -1
    if scene.get("allowed_actions") and score == 0:
        return -1
    return score


def scene_pose_score(scene: dict[str, Any], pose_type: str | None, actions: list[dict[str, Any]]) -> int:
    if not pose_type:
        return 0
    forbidden_text = flatten_text(scene.get("forbidden_actions"))
    if pose_type in forbidden_text:
        return -20
    for action in actions:
        pose = action.get("pose") if isinstance(action.get("pose"), dict) else {}
        if pose.get("type") == pose_type and action_fit_score(scene, action) > 0:
            return 16
    return 0


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
        raise AtlasCliError("没有可用候选条目，请放宽筛选条件")
    shortlist = scored[: min(12, len(scored))]
    weights = [max(1, score + 1) for score, _, _ in shortlist]
    picked = rng.choices(shortlist, weights=weights, k=1)[0]
    return picked[1], picked[2]


def fixed_entry(
    items: list[dict[str, Any]],
    index: int | None,
    entry_id: str | None,
    library: str,
) -> tuple[int, dict[str, Any]] | None:
    if entry_id:
        if not entry_id_is_valid(library, entry_id):
            raise ValueError(f"{LIBRARY_LABELS[library]} id 格式无效: {entry_id}")
        for found_index, item in enumerate(items):
            if item.get("id") == entry_id:
                if index is not None and index != found_index:
                    raise ValueError(
                        f"{LIBRARY_LABELS[library]} index/id 不一致: "
                        f"index {index} 指向其它条目，但 {entry_id} 位于 index {found_index}"
                    )
                return found_index, item
        raise ValueError(f"{LIBRARY_LABELS[library]}未找到 id: {entry_id}")

    if index is None:
        return None
    if index < 0 or index >= len(items):
        raise ValueError(f"{LIBRARY_LABELS[library]} index 越界: {index}，有效范围 0-{len(items) - 1}")
    return index, items[index]


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

    try:
        fixed_scene = fixed_entry(atlas["scenes"], args.scene_index, args.scene_id, "scenes")
        fixed_outfit = fixed_entry(atlas["outfits"], args.outfit_index, args.outfit_id, "outfits")
        fixed_action = fixed_entry(atlas["actions"], args.action_index, args.action_id, "actions")
        fixed_expression = fixed_entry(
            atlas["expressions"],
            args.expression_index,
            args.expression_id,
            "expressions",
        )
    except ValueError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 2

    scene_terms = normalize_terms(args.scene_name)

    for _ in range(args.count):
        def scene_score(item: dict[str, Any], include_mood: bool = True) -> int:
            if args.scene_category and item.get("category") != args.scene_category:
                return -1
            if scene_terms and not item_has_any(item, scene_terms):
                return -1
            pose_type = args.pose_type
            if not pose_type and fixed_action:
                pose = fixed_action[1].get("pose") if isinstance(fixed_action[1].get("pose"), dict) else {}
                pose_type = str(pose.get("type", ""))
            score = scene_pose_score(item, pose_type, atlas["actions"])
            if score < 0:
                return -1
            if include_mood:
                score += mood_value(item, args.mood) * 5
            if fixed_outfit:
                status, _ = compatibility_status(item, fixed_outfit[1])
                if status == "incompatible":
                    return -1
                if args.strict_compatible and status != "compatible":
                    return -1
                if status == "compatible":
                    score += 12
            if fixed_action:
                action_score_value = action_fit_score(item, fixed_action[1])
                if action_score_value < 0:
                    return -1
                score += action_score_value
            return score

        if fixed_scene:
            scene_index, scene = fixed_scene
        else:
            scene_candidates = candidates(
                atlas["scenes"],
                lambda item: scene_score(item, include_mood=True),
                fallback_score_func=lambda item: scene_score(item, include_mood=False),
            )
            scene_index, scene = choose(scene_candidates, rng)

        def outfit_base_score(item: dict[str, Any]) -> int:
            score = 0
            if args.mood:
                value = mood_value(item, args.mood)
                if value < args.min_mood:
                    return -1
                score += value * 5
            if args.occasion and args.occasion not in normalize_terms(item.get("occasion")):
                return -1
            return score

        def outfit_score(item: dict[str, Any]) -> int:
            score = outfit_base_score(item)
            if score < 0:
                return -1
            status, _ = compatibility_status(scene, item)
            if status == "incompatible":
                return -1
            if args.strict_compatible and status != "compatible":
                return -1
            if status == "compatible":
                score += 12
            return score

        def outfit_relaxed_score(item: dict[str, Any]) -> int:
            score = outfit_base_score(item)
            if score < 0:
                return -1
            status, _ = compatibility_status(scene, item)
            if status == "incompatible":
                return -1
            return score

        outfit_fallback = None if args.strict_compatible else outfit_relaxed_score
        if fixed_outfit:
            outfit_index, outfit = fixed_outfit
        else:
            outfit_index, outfit = choose(candidates(atlas["outfits"], outfit_score, outfit_fallback), rng)
        compat_status, compat_note = compatibility_status(scene, outfit)
        if args.strict_compatible and compat_status != "compatible":
            print(
                f"错误: 固定场景/服装未通过 strict-compatible 检查: {compat_note}",
                file=sys.stderr,
            )
            return 2

        def action_scene_score(item: dict[str, Any]) -> int:
            return action_fit_score(scene, item)

        def action_score(item: dict[str, Any]) -> int:
            score = action_scene_score(item)
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

        if fixed_action:
            action_index, action = fixed_action
        else:
            action_index, action = choose(candidates(atlas["actions"], action_score, action_scene_score), rng)

        def expression_score(item: dict[str, Any]) -> int:
            if args.mood:
                value = mood_value(item, args.mood)
                if value < args.min_mood:
                    return -1
                return value * 5
            return int(item.get("overall", {}).get("intensity", 0) or 0)

        if fixed_expression:
            expression_index, expression = fixed_expression
        else:
            expression_index, expression = choose(candidates(atlas["expressions"], expression_score, lambda item: 0), rng)

        outputs.append(
            {
                "scene": scene.get("scene"),
                "scene_index": scene_index,
                "scene_id": scene.get("id"),
                "scene_category": scene.get("category"),
                "outfit_index": outfit_index,
                "outfit_id": outfit.get("id"),
                "action_index": action_index,
                "action_id": action.get("id"),
                "expression_index": expression_index,
                "expression_id": expression.get("id"),
                "compatibility": compat_status,
                "compatibility_note": compat_note,
                "outfit": outfit.get("description"),
                "action": action.get("description"),
                "expression": expression.get("description"),
                "prompt": compact_prompt(scene, outfit, action, expression),
                "fixed": {
                    "scene": fixed_scene is not None,
                    "outfit": fixed_outfit is not None,
                    "action": fixed_action is not None,
                    "expression": fixed_expression is not None,
                },
            }
        )

    if args.json:
        write_json(outputs if args.count != 1 else outputs[0])
    else:
        for index, output in enumerate(outputs, start=1):
            if len(outputs) > 1:
                print(f"## 提示词 {index}")
            print(f"场景: {output['scene']} ({output['scene_category']}, {output['scene_id']}@{output['scene_index']})")
            print(f"服装: {output['outfit']} ({output['outfit_id']}@{output['outfit_index']})")
            print(f"动作: {output['action']} ({output['action_id']}@{output['action_index']})")
            print(f"表情: {output['expression']} ({output['expression_id']}@{output['expression_index']})")
            compatibility = COMPATIBILITY_LABELS.get(str(output["compatibility"]), str(output["compatibility"]))
            print(f"兼容性: {compatibility} - {output['compatibility_note']}")
            print(f"提示词: {output['prompt']}")
            if index != len(outputs):
                print()
    return 0
