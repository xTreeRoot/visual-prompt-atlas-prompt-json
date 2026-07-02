"""视觉提示词图谱的共享常量。"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCES = ROOT / "references"

LIBRARIES = {
    "actions": ("璃夏_动作Prompt库v2.json", "actionLibrary"),
    "outfits": ("璃夏_服装Prompt库v2.json", "clothesLibrary"),
    "expressions": ("璃夏_表情Prompt库v2.json", "expressionLibrary"),
    "scenes": ("璃夏_空间背景Prompt库v2.json", "scenes"),
}

ID_PREFIXES = {
    "actions": "action",
    "outfits": "outfit",
    "expressions": "expression",
    "scenes": "scene",
}

LIBRARY_LABELS = {
    "actions": "动作库",
    "outfits": "服装库",
    "expressions": "表情库",
    "scenes": "场景库",
}

STAT_LABELS = {
    "count": "条目数",
    "top_categories": "高频分类",
    "top_moods": "高频情绪",
    "top_keywords": "高频关键词",
    "top_occasions": "高频适用场合",
}

COMPATIBILITY_LABELS = {
    "compatible": "兼容",
    "incompatible": "不兼容",
    "unknown": "未知",
}
