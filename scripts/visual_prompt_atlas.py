#!/usr/bin/env python3
"""视觉提示词图谱 CLI 兼容入口。

实际实现位于 `scripts/atlas/`，这里保留旧入口路径，避免 README、
SKILL 和自动化命令需要改名。
"""

from __future__ import annotations

import sys

from atlas.cli import main
from atlas.validation import validate_atlas


__all__ = ["main", "validate_atlas"]


if __name__ == "__main__":
    sys.exit(main())
