# Visual Prompt Atlas Prompt JSON

Chinese version: [README.md](./README.md)

A real-world video-distilled visual prompt JSON dataset covering actions, outfits, expressions, and scene backgrounds for more realistic AI image generation.

## Introduction

This repository is a structured prompt dataset for AI image generation.

Instead of being a generic hand-written prompt collection, it is distilled from large-scale real-world video observations and organized into reusable JSON data. The goal is to preserve visual elements that feel natural, effective, and grounded in real photo references.

Core content includes:

- realistic body actions and poses
- realistic outfit combinations
- realistic facial expressions
- realistic scene backgrounds
- heuristic scene-outfit matching from existing scene and outfit fields

This repository can be used for:

- AI photo generation
- character image generation
- automatic prompt composition
- image generation workflow data sources
- realistic scene and pose references
- visual prompt libraries for multimodal agents

For Codex or other AI agents, read: [SKILL.md](./SKILL.md)

Install as a Codex Skill:

```bash
git clone https://github.com/xTreeRoot/visual-prompt-atlas-prompt-json.git ~/.codex/skills/visual-prompt-atlas-prompt-json
```

## Tooling

This repository includes functional Python scripts in addition to the dataset:

```bash
python3 scripts/visual_prompt_atlas.py validate
python3 scripts/visual_prompt_atlas.py stats
python3 scripts/visual_prompt_atlas.py search actions 直视镜头 --mood 温柔 --limit 5
python3 scripts/visual_prompt_atlas.py compose --mood 温柔 --scene-category 居家私密 --occasion 居家 --pose-type 坐 --interaction-min 3
python3 scripts/visual_prompt_atlas.py compose --outfit-id outfit_0081 --scene-category 城市街头 --strict-compatible --json
python3 scripts/visual_prompt_atlas.py compose --identity-slot rixia-long-leg-v1 --mood 温柔 --json
python3 scripts/visual_prompt_atlas.py ids next outfits --count 3
python3 scripts/visual_prompt_atlas.py ingest outfits new_outfits.json --dry-run
```

Script capabilities:

- `validate`: validate JSON files and required schema shape
- `stats`: summarize dataset size, common moods, scene categories, and more
- `search`: search entries by text, mood, scene, outfit occasion, action pose, and other filters
- `compose`: automatically combine scene, outfit, action, and expression entries while filtering awkward scene-outfit combinations
- `compose` can lock exact JSON-library entries with `--scene-id`, `--outfit-id`, `--action-id`, and `--expression-id`; `--*-index` remains available for temporary debugging
- `compose` can read a local identity slot with `--identity-slot <slot-id>`, add the identity description and reference path to output, and include the identity description in the generated prompt
- `ids`: preview or backfill stable entry ids
- `ingest`: accept new entry JSON, validate fields, and assign non-conflicting ids

Append `--json` when another program or agent should consume the output.

## Dataset Size

Current version:

| Type | File | Count |
| --- | --- | ---: |
| Actions | `references/璃夏_动作Prompt库v2.json` | 513 |
| Outfits | `references/璃夏_服装Prompt库v2.json` | 508 |
| Expressions | `references/璃夏_表情Prompt库v2.json` | 376 |
| Scene backgrounds | `references/璃夏_空间背景Prompt库v2.json` | 100 |

## Stable Entry IDs

Every entry in every library has a stable `id` for cross-tool references, reproducible composition, and safer ingestion:

- Actions: `action_0000`
- Outfits: `outfit_0000`
- Expressions: `expression_0000`
- Scenes: `scene_0000`

The first backfill maps ids to the current array positions. New entries should receive the next available id after scanning existing data through `ids next` or `ingest`. Do not renumber old ids; array order may change, but ids should remain stable.

## Directory Structure

```text
references/
  ACTIONS_INDEX.md
  CLOTHES_INDEX.md
  EXPRESSIONS_INDEX.md
  SCENES_INDEX.md
  璃夏_动作Prompt库v2.json
  璃夏_服装Prompt库v2.json
  璃夏_空间背景Prompt库v2.json
  璃夏_表情Prompt库v2.json
scripts/
  visual_prompt_atlas.py
  validate_atlas.py
  atlas/
```

## Included Data

### Actions

The action library includes action descriptions, keywords, mood labels, interaction direction, motion intensity, pose type, and camera view.

It can be used to filter prompts by:

- camera-facing, user-interactive, or non-interactive actions
- still, subtle-motion, or high-motion states
- standing, sitting, lying, kneeling, crouching, jumping, walking, running, and more
- pure, sweet, playful, gentle, sexy, lazy, and other moods

### Outfits

The outfit library includes outfit descriptions, keywords, mood labels, and suitable occasions.

It can be used to filter prompts by:

- school, home, urban, dating, sports, beach, party, and other occasions
- pure, sweet, elegant, sexy, lively, and other styles
- different photographic outfit styles

### Expressions

The expression library includes facial expression descriptions, eye direction, eye state, mouth shape, cheek details, and overall emotional intensity.

It can be used to filter prompts by:

- looking at the camera, looking sideways, looking down, closed eyes, and more
- smile, shy expression, cold expression, parted lips, and other details
- cute, gentle, playful, melancholic, cool, seductive, and other emotional styles

### Scene Backgrounds

The scene library includes realistic indoor, private home, urban street, urban landscape, and outdoor nature backgrounds.

It can be used to filter prompts by:

- bedroom, living room, classroom, convenience store, street, park, lakeside, and more
- private spaces, public spaces, city nights, natural waterfronts, and other atmospheres
- scene constraints that match natural body actions
- compatible outfit occasions and forbidden outfit keywords

### Scene-Outfit Matching

The CLI loads scene-outfit fit from each scene entry's `compatible_outfit_occasions` and `forbidden_outfit_keywords`, plus outfit `occasion`, `original_occasion`, and `keywords`.
When entries are explicitly locked with `--scene-id` or `--outfit-id`, those entries take priority; with `--strict-compatible`, the scene and outfit must still have a positive compatibility match.

For example:

- homewear works better in bedrooms and living rooms
- school outfits work better in classrooms and daily street scenes
- swimwear works better around beaches, pools, and waterfront spaces

## Usage

You can load the JSON files directly and combine action, outfit, expression, and scene descriptions into an image-generation prompt.

```python
import json
from pathlib import Path

base = Path("references")

actions = json.loads((base / "璃夏_动作Prompt库v2.json").read_text(encoding="utf-8"))
clothes = json.loads((base / "璃夏_服装Prompt库v2.json").read_text(encoding="utf-8"))
expressions = json.loads((base / "璃夏_表情Prompt库v2.json").read_text(encoding="utf-8"))
scenes = json.loads((base / "璃夏_空间背景Prompt库v2.json").read_text(encoding="utf-8"))

print(len(actions["actionLibrary"]))
print(len(clothes["clothesLibrary"]))
print(len(expressions["expressionLibrary"]))
print(len(scenes["scenes"]))
```

Recommended composition flow:

1. Select a scene background
2. Filter suitable outfits by scene
3. Select an action or pose
4. Select a facial expression
5. Combine the descriptions into an image-generation prompt
6. Use the matching heuristic to remove clearly unnatural combinations

If `search` has already found exact entries, lock their ids directly:

```bash
python3 scripts/visual_prompt_atlas.py compose \
  --scene-id scene_0037 \
  --outfit-id outfit_0081 \
  --action-id action_0278 \
  --expression-id expression_0000 \
  --identity-slot rixia-long-leg-v1 \
  --strict-compatible \
  --json
```

## Data Notice

This repository contains text-based structured prompt data only. It does not include source videos, video frames, images, or any media assets.

Use this dataset as a reference, retrieval source, or composition source inside your own image-generation workflow. Please follow the rules of the models, platforms, and regions where you use it.

## License

This repository is licensed under [CC BY-NC 4.0](./LICENSE).

Personal, research, educational, and other non-commercial use is allowed. Commercial use is not permitted. Please contact the repository owner separately for commercial licensing.
