# Visual Prompt Atlas Prompt JSON

Chinese version: [README.md](./README.md)

A real-world video-distilled visual prompt JSON dataset covering actions, outfits, expressions, scene backgrounds, and compatibility rules for more realistic AI image generation.

## Introduction

This repository is a structured prompt dataset for AI image generation.

Instead of being a generic hand-written prompt collection, it is distilled from large-scale real-world video observations and organized into reusable JSON data. The goal is to preserve visual elements that feel natural, effective, and grounded in real photo references.

Core content includes:

- realistic body actions and poses
- realistic outfit combinations
- realistic facial expressions
- realistic scene backgrounds
- compatibility rules between scenes and outfits

This repository can be used for:

- AI photo generation
- character image generation
- automatic prompt composition
- image generation workflow data sources
- realistic scene and pose references
- visual prompt libraries for multimodal agents

## Dataset Size

Current version:

| Type | File | Count |
| --- | --- | ---: |
| Actions | `references/璃夏_动作Prompt库v2.json` | 513 |
| Outfits | `references/璃夏_服装Prompt库v2.json` | 508 |
| Expressions | `references/璃夏_表情Prompt库v2.json` | 376 |
| Scene backgrounds | `references/璃夏_空间背景Prompt库v2.json` | 100 |
| Scene-outfit compatibility rules | `references/scene_clothes_compatibility.json` | 31 compatible groups / 14 incompatible groups |

## Directory Structure

```text
references/
  ACTIONS_INDEX.md
  CLOTHES_INDEX.md
  EXPRESSIONS_INDEX.md
  SCENES_INDEX.md
  scene_clothes_compatibility.json
  璃夏_动作Prompt库v2.json
  璃夏_服装Prompt库v2.json
  璃夏_空间背景Prompt库v2.json
  璃夏_表情Prompt库v2.json
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

The outfit library includes outfit descriptions, keywords, mood labels, suitable occasions, and spiciness levels.

It can be used to filter prompts by:

- school, home, urban, dating, sports, beach, party, and other occasions
- pure, sweet, elegant, sexy, lively, and other styles
- different levels of visual boldness

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

### Scene-Outfit Compatibility

The compatibility file helps avoid visually awkward combinations between outfits and scene backgrounds.

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
6. Use compatibility rules to remove unnatural combinations

## Data Notice

This repository contains text-based structured prompt data only. It does not include source videos, video frames, images, or any media assets.

Use this dataset as a reference, retrieval source, or composition source inside your own image-generation workflow. Please follow the rules of the models, platforms, and regions where you use it.

## License

This repository is licensed under [CC BY-NC 4.0](./LICENSE).

Personal, research, educational, and other non-commercial use is allowed. Commercial use is not permitted. Please contact the repository owner separately for commercial licensing.
