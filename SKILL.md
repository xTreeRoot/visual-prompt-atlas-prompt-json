---
name: visual-prompt-atlas-prompt-json
description: Use this real-world video-distilled visual prompt JSON atlas when composing realistic AI image prompts, building prompt generators, selecting actions/outfits/expressions/scene backgrounds, or filtering awkward scene-outfit combinations from the bundled references data. Trigger when the user asks for realistic photo prompts, character photo prompt combinations, visual prompt datasets, prompt JSON lookup, or AI image-generation workflows based on actions, clothing, expressions, and backgrounds.
---

# Visual Prompt Atlas Prompt JSON

Use this skill to build realistic image-generation prompts from the repository's structured JSON prompt atlas.

The dataset contains text-only prompt data distilled from real-world video references. It includes actions, outfits, facial expressions, and scene backgrounds. It does not include source videos, frames, images, or media assets.

## Fast Path

Prefer the bundled Python CLI before manually reading large JSON files:

```bash
python3 scripts/visual_prompt_atlas.py validate
python3 scripts/visual_prompt_atlas.py stats
python3 scripts/visual_prompt_atlas.py search actions 直视镜头 --mood 温柔 --limit 5
python3 scripts/visual_prompt_atlas.py compose --mood 温柔 --scene-category 居家私密 --occasion 居家 --pose-type 坐 --interaction-min 3
```

Use `--json` when another program or agent will consume the output.

## Identity Reference Slot

When the user wants a fixed person identity across generated images, use a project-local identity slot under `slots/identity/<slot-id>/`.

Each identity slot should contain only:

- `reference.jpg`: the person reference image.
- `description.md`: a concise description derived from the image, limited to face, hair, and overall body silhouette.

Identity slots are local/private user data and must not be committed or pushed to a remote repository.

Do not put scene, outfit, action, expression, styling rules, generated outputs, or JSON atlas data inside the identity slot.

Before running an identity-locked image workflow:

1. Tell the AI/user that a person reference image is required first.
2. If the user provides a person reference image, create or update an identity slot by saving the image as `reference.jpg` and writing `description.md` from the image.
3. Use the identity slot only for the fixed person identity: face, hair, body silhouette, and body proportions.
4. Select every other visual element from the prompt JSON atlas: outfit, scene, action, expression, props, background, and styling.
5. If no reference image or usable identity slot exists, the identity-locked workflow cannot run. The user may explicitly force a run; in that case, compose from the prompt JSON atlas without identity locking and state that no fixed identity reference was used.

## Resources

Use these files in `references/`:

- `ACTIONS_INDEX.md`: action schema, mood tags, interaction levels, dynamic levels, pose/view filters.
- `CLOTHES_INDEX.md`: outfit schema, mood tags, occasions, and keyword filters.
- `EXPRESSIONS_INDEX.md`: expression schema, eye/mouth/cheek/overall emotion filters.
- `SCENES_INDEX.md`: scene categories, high-frequency scene names, tags, recommended actions.
- `璃夏_动作Prompt库v2.json`: 513 action entries under `actionLibrary`.
- `璃夏_服装Prompt库v2.json`: 508 outfit entries under `clothesLibrary`.
- `璃夏_表情Prompt库v2.json`: 376 expression entries under `expressionLibrary`.
- `璃夏_空间背景Prompt库v2.json`: 100 scene entries under `scenes`.

Read the relevant index file first when you need schema or filtering semantics. Parse JSON directly for selection, search, sampling, or generation. Avoid ad hoc string-only processing when JSON parsing is available.

## Scripts

- `scripts/visual_prompt_atlas.py`: main CLI for stats, validation, search, and prompt composition.
- `scripts/validate_atlas.py`: compact validation entrypoint for CI or automated checks.

Main CLI commands:

```bash
# Show dataset counts, top moods, categories, and label summaries.
python3 scripts/visual_prompt_atlas.py stats --json

# Validate required files and schema shape.
python3 scripts/visual_prompt_atlas.py validate

# Search one library or all libraries.
python3 scripts/visual_prompt_atlas.py search all 卧室 --limit 5 --json
python3 scripts/visual_prompt_atlas.py search outfits 连衣裙 --mood 优雅 --min-mood 4

# Compose one or more realistic prompts.
python3 scripts/visual_prompt_atlas.py compose --mood 甜美 --scene-category 城市街头 --count 3 --seed 12 --json
```

When a task asks for generated prompt options, call `compose`. When a task asks for finding suitable entries, call `search`. When a task asks whether the dataset is healthy or installable as a skill, call `validate`.

## Core Workflow

1. Understand the user's requested image style, subject, mood, setting, outfit constraints, and output format.
2. Select a scene from `璃夏_空间背景Prompt库v2.json`.
3. Select an outfit from `璃夏_服装Prompt库v2.json`; use scene category, scene tags, outfit occasion, and outfit keywords to avoid unnatural combinations.
4. Select an action from `璃夏_动作Prompt库v2.json` that fits the scene's recommended actions and the requested interaction level.
5. Select an expression from `璃夏_表情Prompt库v2.json` that matches the requested mood and pose.
6. Combine the chosen `description` fields into a concise image prompt. Preserve useful keywords when they add control, but avoid dumping entire JSON objects into the final prompt unless requested.
7. When asked for multiple options, vary one or two axes at a time, such as scene plus outfit, or action plus expression, so comparisons remain meaningful.

## Selection Heuristics

- Prefer entries with matching mood labels at level 4 or 5 when the user asks for a clear mood.
- Prefer `interaction.level >= 4` and `interaction.direction == "镜头"` for direct camera-facing portrait prompts.
- Prefer low dynamic intensity for calm portraits, medium intensity for natural daily photos, and high intensity for dance, sports, or motion shots.
- Match pose type to scene constraints: sitting actions for sofas, beds, classrooms, and benches; standing or walking actions for streets, platforms, corridors, and outdoor spaces.
- Use scene-outfit fit as a heuristic filter, not as the only selection signal. If the user explicitly requests an unusual combination, mention the mismatch and offer a more natural alternative.
- Keep the final prompt grounded in realistic physical space, plausible clothing, and natural body language.

## Output Patterns

For a single prompt, return:

```text
Scene: ...
Outfit: ...
Action: ...
Expression: ...
Prompt: ...
```

For JSON output, return stable keys:

```json
{
  "scene": "...",
  "outfit": "...",
  "action": "...",
  "expression": "...",
  "prompt": "...",
  "notes": "..."
}
```

For prompt-generator code, load the data with UTF-8:

```python
import json
from pathlib import Path

base = Path("references")
actions = json.loads((base / "璃夏_动作Prompt库v2.json").read_text(encoding="utf-8"))["actionLibrary"]
outfits = json.loads((base / "璃夏_服装Prompt库v2.json").read_text(encoding="utf-8"))["clothesLibrary"]
expressions = json.loads((base / "璃夏_表情Prompt库v2.json").read_text(encoding="utf-8"))["expressionLibrary"]
scenes = json.loads((base / "璃夏_空间背景Prompt库v2.json").read_text(encoding="utf-8"))["scenes"]
```

## Guardrails

- Respect the repository license: non-commercial use only unless the repository owner grants separate written permission.
- Do not claim access to the original videos or source media. Only this structured text dataset is available.
- Do not invent dataset counts or schema fields. Inspect the JSON or index files when precision matters.
- Do not include sensitive local paths, git metadata, or private project history in generated output.
- Keep prompts suitable for the user's model and platform rules.
