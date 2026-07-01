#!/usr/bin/env python3
"""Validate the Visual Prompt Atlas dataset."""

from __future__ import annotations

import json
import sys

from visual_prompt_atlas import validate_atlas


def main() -> int:
    errors, warnings = validate_atlas()
    print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
