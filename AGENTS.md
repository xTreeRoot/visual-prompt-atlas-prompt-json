# AGENTS.md

## Project Scope

This repository is a text-only visual prompt atlas. It contains structured JSON references for actions, outfits, facial expressions, and scene backgrounds, plus Python tooling for validation, search, statistics, and prompt composition.

## Data Guidelines

- Keep JSON files UTF-8 encoded and human-readable.
- Preserve the existing top-level JSON keys:
  - `actionLibrary`
  - `clothesLibrary`
  - `expressionLibrary`
  - `scenes`
- Do not add a separate scene-outfit compatibility JSON file. Scene-outfit fit is derived in `scripts/visual_prompt_atlas.py` from scene categories, scene tags, outfit occasions, and outfit keywords.
- When changing schema, counts, or filtering semantics, update `README.md`, `README_EN.md`, `SKILL.md`, and the relevant `references/*_INDEX.md` file in the same change.
- Identity slots under `slots/identity/` are local private data and must not be committed.

## Validation

Run these checks before committing data or tooling changes:

```bash
python3 scripts/visual_prompt_atlas.py validate --json
python3 scripts/visual_prompt_atlas.py stats --json
python3 scripts/visual_prompt_atlas.py compose --scene-name 客厅 --strict-compatible --count 3 --seed 1 --json
python3 scripts/visual_prompt_atlas.py compose --scene-name 卧室 --strict-compatible --count 3 --seed 1 --json
```

## Git

Use the existing repository author for commits unless the user explicitly asks otherwise:

```text
xTreeRoot <xTreeRoot@users.noreply.github.com>
```
