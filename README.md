# 视觉提示词图谱 JSON 数据库

英文版：[README_EN.md](./README_EN.md)

一个从真实视频参考中蒸馏整理的视觉提示词 JSON 数据库，覆盖动作、服装、表情与背景空间，帮助生成更真实自然的 AI 图片。

## 项目介绍

这个仓库是一套面向 AI 图片生成的结构化提示词数据库。

它不是凭空编写的普通提示词集合，而是基于大量真实视频画面观察与 AI 蒸馏整理出的高密度数据资产，重点保留真实人物照片中常见、自然、有效的视觉要素。

核心内容包括：

- 真实动作姿态
- 真实服装搭配
- 真实面部表情
- 真实背景空间
- 基于场景与服装字段的自然组合启发式

这个仓库适合用于：

- AI 写真生成
- 角色图片生成
- 提示词自动组合
- 图像生成工作流的数据源
- 真实感画面构图参考
- 多模态智能体的视觉素材库

给 Codex 或其他 AI 智能体使用时，可以直接阅读：[SKILL.md](./SKILL.md)

作为 Codex 技能安装：

```bash
git clone https://github.com/xTreeRoot/visual-prompt-atlas-prompt-json.git ~/.codex/skills/visual-prompt-atlas-prompt-json
```

## 工具脚本

这个仓库不仅包含数据，也包含可直接调用的 Python 工具脚本：

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

脚本能力：

- `validate`：校验 JSON 文件和基础字段结构
- `stats`：统计数据规模、常见情绪、场景分类等信息
- `search`：按文本、情绪、场景、服装场合、动作姿态等条件搜索条目
- `compose`：自动组合背景、服装、动作、表情，并根据场景分类与服装场合过滤明显违和组合
- `compose` 可用 `--scene-id`、`--outfit-id`、`--action-id`、`--expression-id` 锁定 JSON 库里的指定条目；`--*-index` 仍可用于临时调试
- `compose` 可用 `--identity-slot <slot-id>` 读取本地身份槽，把身份描述和参考图路径加入输出，并将身份描述写入生成提示词
- `ids`：预览或回填稳定条目 id
- `ingest`：接收新条目 JSON，校验字段并自动分配不冲突的 id

如果要把结果交给其他程序或智能体处理，可以追加 `--json`。

## 数据规模

当前版本包含：

| 类型 | 文件 | 数量 |
| --- | --- | ---: |
| 动作 | `references/璃夏_动作Prompt库v2.json` | 513 |
| 服装 | `references/璃夏_服装Prompt库v2.json` | 508 |
| 表情 | `references/璃夏_表情Prompt库v2.json` | 376 |
| 背景空间 | `references/璃夏_空间背景Prompt库v2.json` | 100 |

## 稳定条目 ID

每个库里的条目都有稳定 `id`，用于跨工具引用、复现组合结果和安全入库：

- 动作：`action_0000`
- 服装：`outfit_0000`
- 表情：`expression_0000`
- 场景：`scene_0000`

首轮 id 按当前数组位置回填，后续新增条目由 `ids next` 或 `ingest` 扫描现有数据后分配最大编号之后的可用 id。不要手动重排旧 id；数组顺序可以变化，但 id 应保持不变。

## 目录结构

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

## 数据内容

### 动作库

动作库包含动作描述、关键词、情绪标签、互动方向、动态强度、姿态类型与镜头视角等字段。

适合用于筛选：

- 面向镜头、用户互动、无互动动作
- 静止、微动、动起来的动态强度
- 站、坐、躺、跪、蹲、跳、走、跑等姿态
- 清纯、甜美、俏皮、温柔、性感、慵懒等情绪氛围

### 服装库

服装库包含服装描述、关键词、情绪标签与适用场景等信息。

适合用于筛选：

- 校园、居家、都市、约会、运动、海滩、派对等场景穿搭
- 清纯、甜美、优雅、性感、活泼等风格
- 不同风格的写真服装表达

### 表情库

表情库包含表情描述、眼神、嘴型、脸颊、整体情绪强度等字段。

适合用于筛选：

- 看镜头、侧看、低头、闭眼等眼神方向
- 微笑、抿嘴、张嘴、害羞、冷淡等表情细节
- 可爱、温柔、俏皮、忧郁、高冷、诱惑等情绪表达

### 背景空间库

背景空间库包含室内、居家私密、城市街头、城市景观、户外自然等真实空间场景。

适合用于筛选：

- 卧室、客厅、教室、便利店、街道、公园、湖边等背景
- 私密空间、公共空间、城市夜景、自然水岸等氛围
- 与动作姿态兼容的真实场景
- 可兼容服装场合与禁用服装关键词

### 场景服装组合启发式

脚本会从场景条目的 `compatible_outfit_occasions`、`forbidden_outfit_keywords` 和服装条目的 `occasion`、`original_occasion`、`keywords` 加载适配信息，过滤明显违和的组合。
如果通过 `--scene-id` 或 `--outfit-id` 显式指定条目，指定条目优先；开启 `--strict-compatible` 时，场景与服装仍必须得到正向兼容匹配。

例如：

- 居家服更适合卧室、客厅等私密空间
- 校园服装更适合教室、街道等日常场景
- 泳装更适合海滩、泳池、户外水岸等空间

## 使用方式

你可以直接读取 JSON 文件，并按动作、服装、表情、场景进行组合：

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

推荐组合流程：

1. 选择一个背景空间
2. 根据背景空间筛选合适服装
3. 选择动作姿态
4. 选择面部表情
5. 将描述字段组合成图像生成提示词
6. 使用组合启发式过滤明显不自然的搭配

如果已经通过 `search` 找到具体条目，可直接锁定 id 再组合：

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

## 数据声明

本仓库只包含文本化、结构化的提示词数据，不包含原始视频、视频帧、图片素材或任何媒体文件。

这些数据适合作为图像生成工作流中的参考素材、检索素材或组合素材。请在使用时遵守你所使用模型、平台和地区的相关规则。

## 许可证

本仓库采用 [CC BY-NC 4.0](./LICENSE) 许可。

允许个人、研究、教育和其他非商业使用；禁止商业使用。商业授权需另行联系仓库所有者。
