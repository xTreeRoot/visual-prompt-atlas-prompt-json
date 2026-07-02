---
name: visual-prompt-atlas-prompt-json
description: 使用这个从真实视频观察中蒸馏出的视觉提示词 JSON 图谱来组合真实感图片提示词、构建提示词生成器、选择动作/服装/表情/场景背景，或根据内置参考数据过滤不自然的场景服装组合。当用户需要真实感照片提示词、角色写真提示词组合、视觉提示词数据集、提示词 JSON 检索，或基于动作/服装/表情/背景的 AI 图像生成流程时使用。
---

# 视觉提示词图谱 JSON

使用本技能从仓库内的结构化 JSON 提示词图谱构建真实感图像生成提示词。

本数据集是从真实世界视频观察中蒸馏出的纯文本提示词数据，包含动作、服装、面部表情和场景背景。不包含源视频、视频帧、图片或其它媒体素材。

## 快速路径

优先使用仓库内置 Python CLI，不要一开始就手动读取大 JSON 文件：

```bash
python3 scripts/visual_prompt_atlas.py validate
python3 scripts/visual_prompt_atlas.py stats
python3 scripts/visual_prompt_atlas.py search actions 直视镜头 --mood 温柔 --limit 5
python3 scripts/visual_prompt_atlas.py compose --mood 温柔 --scene-category 居家私密 --occasion 居家 --pose-type 坐 --interaction-min 3
python3 scripts/visual_prompt_atlas.py compose --outfit-id outfit_0081 --scene-category 城市街头 --strict-compatible --json
python3 scripts/visual_prompt_atlas.py compose --identity-slot rixia-long-leg-v1 --mood 温柔 --json
```

当结果要交给其它程序或智能体消费时，追加 `--json`。

## 身份参考槽

使用图谱生成真实感人物图片、人物写真提示词或其它会出现固定人物主体的结果时，默认必须使用项目本地身份槽：`slots/identity/<slot-id>/`。只有用户明确要求“不固定身份”“随机人物”或“不要身份槽”时，才可以跳过身份槽；不要因为用户没有主动提到身份槽就生成通用人物。

每个身份槽只应包含：

- `reference.jpg`：人物参考图。
- `description.md`：从参考图提炼的简短描述，只写脸部、发型和整体身体轮廓。

身份槽是本地私有数据，不应提交或推送到远端仓库。

不要把场景、服装、动作、表情、样式规则、生成结果或 JSON 图谱数据放进身份槽。

身份槽选择规则：

1. 如果用户指定了身份槽，优先使用该槽。
2. 如果用户没有指定身份槽，先扫描 `slots/identity/*/`，查找同时包含 `reference.jpg` 和 `description.md` 的可用槽。
3. 如果只有一个可用身份槽，直接使用它，不再额外询问。
4. 如果有多个可用身份槽，先简短询问用户使用哪一个；不要擅自挑选。
5. 如果没有可用身份槽，必须先提示用户提供人物参考图；收到参考图后创建或更新身份槽，将图片保存为 `reference.jpg`，并由 AI 根据参考图写入 `description.md`，再继续生成提示词或图片。
6. 如果已有 `reference.jpg` 但缺少 `description.md`，先读取参考图并补写 `description.md`，再继续。

运行身份锁定工作流时：

1. 身份槽只用于固定人物身份：脸部、发型、身体轮廓和身体比例。
2. 其它视觉元素都从提示词图谱中选择：服装、场景、动作、表情、道具、背景和风格。
3. 让 `compose` 输出带上身份信息时，必须使用 `--identity-slot <slot-id>`。脚本会读取 `description.md`，在 JSON 输出中加入 `identity_slot`、`identity_reference`、`identity`，并把身份描述写进 `prompt`。
4. 如果没有可用身份槽且用户还没有提供参考图，不要继续生成通用人物；先等待用户补充参考图。用户明确要求跳过身份固定时，才可以只从提示词图谱组合，并说明未使用固定身份参考。

## 资源

使用 `references/` 里的这些文件：

- `ACTIONS_INDEX.md`：动作数据结构、情绪标签、互动等级、动态等级、姿态/视角筛选。
- `CLOTHES_INDEX.md`：服装数据结构、情绪标签、适用场合和关键词筛选。
- `EXPRESSIONS_INDEX.md`：表情数据结构、眼神/嘴型/脸颊/整体情绪筛选。
- `SCENES_INDEX.md`：场景分类、高频场景名、标签和推荐动作。
- `璃夏_动作Prompt库v2.json`：513 条动作，位于 `actionLibrary`。
- `璃夏_服装Prompt库v2.json`：508 条服装，位于 `clothesLibrary`。
- `璃夏_表情Prompt库v2.json`：376 条表情，位于 `expressionLibrary`。
- `璃夏_空间背景Prompt库v2.json`：100 条场景，位于 `scenes`。

需要精确数据结构或过滤语义时，先读对应索引文件。做选择、搜索、抽样或生成时应直接解析 JSON，避免只靠字符串拼凑。

每个库条目都有稳定 id：`action_0000`、`outfit_0000`、`expression_0000`、`scene_0000`。长期引用优先使用 id，不要依赖数组 index。

场景服装适配从场景条目的 `compatible_outfit_occasions`、`forbidden_outfit_keywords` 和服装条目的 `occasion`、`original_occasion`、`keywords` 加载；不要在 Python 里新增硬编码场景服装词表。

动作场景适配从场景条目的 `allowed_actions`、`forbidden_actions` 和动作条目的 `pose.type`、`required_scene_terms` 加载。

## 脚本

- `scripts/visual_prompt_atlas.py`：主 CLI 入口，保持对外命令路径稳定。
- `scripts/atlas/`：CLI 的实际实现，按常量、数据读写、校验、检索、id 维护、入库和组合逻辑拆分。
- `scripts/validate_atlas.py`：用于 CI 或自动化的轻量校验入口。

常用 CLI：

```bash
# 统计数据规模、高频情绪、分类和标签摘要
python3 scripts/visual_prompt_atlas.py stats --json

# 校验必需文件和数据结构
python3 scripts/visual_prompt_atlas.py validate

# 搜索单个库或所有库
python3 scripts/visual_prompt_atlas.py search all 卧室 --limit 5 --json
python3 scripts/visual_prompt_atlas.py search outfits 连衣裙 --mood 优雅 --min-mood 4

# 组合一个或多个真实感提示词
python3 scripts/visual_prompt_atlas.py compose --mood 甜美 --scene-category 城市街头 --count 3 --seed 12 --json
python3 scripts/visual_prompt_atlas.py compose --scene-id scene_0037 --outfit-id outfit_0081 --action-id action_0278 --expression-id expression_0000 --strict-compatible --json
python3 scripts/visual_prompt_atlas.py compose --identity-slot rixia-long-leg-v1 --strict-compatible --json

# 预览稳定 id 与入库新条目
python3 scripts/visual_prompt_atlas.py ids next outfits --count 3
python3 scripts/visual_prompt_atlas.py ingest outfits new_outfits.json --dry-run
```

用户要生成提示词选项时，调用 `compose`。用户要查找合适条目时，调用 `search`。用户要确认数据集健康或可安装为技能时，调用 `validate`。

`search` 和 `compose` 返回的是图谱匹配结果与素材片段，不是面向生图模型的最终主提示词。面向用户输出时，必须把选中的场景、服装、动作和表情作为约束；默认还必须加入身份槽描述作为固定人物身份约束，由 AI 自行改写成完整、连贯、可直接使用的主提示词。只有用户明确要求跳过身份固定时，才可以不使用 `--identity-slot`。

用户要新增数据时，使用 `ingest`，让脚本扫描目标库并自动分配 id。用户已经指定精确 JSON 条目时，使用 `--scene-id`、`--outfit-id`、`--action-id` 或 `--expression-id` 锁定条目。锁定条目优先，其余筛选条件只作用于未锁定的库。`--*-index` 仅用于临时调试或过渡。

## 核心流程

1. 理解用户需要的图像风格、主体、情绪、场景、服装约束和输出格式。
2. 按身份槽选择规则确定 `--identity-slot`；没有可用身份槽时先让用户补充人物参考图，不继续生成通用人物。
3. 从 `璃夏_空间背景Prompt库v2.json` 选择场景。
4. 从 `璃夏_服装Prompt库v2.json` 选择服装；用场景分类、场景标签、服装场合和服装关键词避免不自然组合。
5. 从 `璃夏_动作Prompt库v2.json` 选择适合场景推荐动作和互动强度的动作。
6. 从 `璃夏_表情Prompt库v2.json` 选择符合情绪和姿态的表情。
7. 把选中条目的 `description` 字段当作素材约束，而不是最终文本。先提取场景、服装、动作、表情里必须保留的视觉要点，并读取身份槽的 `description.md` 作为固定人物身份约束。
8. 由 AI 自行生成每一条完整主提示词：补足主体、构图、镜头距离、光线、空间关系、材质细节和真实摄影语气，让结果像一段自然的生图提示词，而不是四段匹配片段的机械拼接。
9. 主提示词必须忠于已选素材和身份槽描述，不要凭空替换场景、服装、动作、表情或人物身份；可以补充不冲突的摄影细节和风格控制词。关键词有助于控制时可以保留，但不要无故把整个 JSON 对象塞进最终提示词。
10. 用户要多个选项时，每个选项都要有独立主提示词；每次只变化一两个维度，例如场景加服装，或动作加表情，方便比较。
11. 如果用户指定精确 id，先锁定这些条目，只抽样未指定的库。开启 `--strict-compatible` 时，锁定的场景/服装组合仍必须通过正向兼容启发式。

## 选择启发式

- 用户明确要求某种情绪时，优先选择该情绪等级为 4 或 5 的条目。
- 直面镜头的人像提示词，优先选择 `interaction.level >= 4` 且 `interaction.direction == "镜头"` 的动作。
- 平静人像优先低动态，日常照片优先中等动态，舞蹈、运动或强动作画面才用高动态。
- 姿态要匹配场景约束：沙发、床、教室、长椅适合坐姿；街道、平台、走廊、户外空间适合站立或行走。
- 场景服装适配是启发式，不是唯一选择标准。用户明确要求不常见组合时，说明可能不自然，并给出更自然的替代方案。
- 最终提示词要保持真实物理空间、合理服装和自然肢体语言。

## 输出模式

单条提示词使用：

```text
场景: ...
服装: ...
动作: ...
表情: ...
主提示词: ...
```

JSON 输出使用稳定 key：

```json
{
  "scene": "...",
  "scene_id": "scene_0037",
  "outfit": "...",
  "outfit_id": "outfit_0081",
  "action": "...",
  "action_id": "action_0278",
  "expression": "...",
  "expression_id": "expression_0000",
  "identity_slot": "rixia-long-leg-v1",
  "identity_reference": "slots/identity/rixia-long-leg-v1/reference.jpg",
  "identity": "从身份槽 description.md 压缩出的身份描述",
  "prompt": "AI 根据匹配素材生成的完整主提示词，不是素材片段原文拼接",
  "fixed": {"scene": true, "outfit": true, "action": true, "expression": true},
  "notes": "..."
}
```

提示词生成器代码应按 UTF-8 加载数据：

```python
import json
from pathlib import Path

base = Path("references")
actions = json.loads((base / "璃夏_动作Prompt库v2.json").read_text(encoding="utf-8"))["actionLibrary"]
outfits = json.loads((base / "璃夏_服装Prompt库v2.json").read_text(encoding="utf-8"))["clothesLibrary"]
expressions = json.loads((base / "璃夏_表情Prompt库v2.json").read_text(encoding="utf-8"))["expressionLibrary"]
scenes = json.loads((base / "璃夏_空间背景Prompt库v2.json").read_text(encoding="utf-8"))["scenes"]
```

## 约束

- 遵守仓库许可证：除非仓库所有者另行书面授权，仅允许非商业使用。
- 不要声称可以访问原始视频或源媒体。本仓库只提供结构化文本数据。
- 不要凭空编造数据规模或数据结构字段；精确性重要时检查 JSON 或索引文件。
- 不要在生成输出中包含敏感本地路径、git 元数据或私有项目历史。
- 提示词内容要适合用户使用的模型和平台规则。
