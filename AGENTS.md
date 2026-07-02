# AGENTS.md

## 项目范围

本仓库是一个纯文本视觉提示词图谱。它包含动作、服装、面部表情、场景背景等结构化 JSON 参考数据，并提供用于校验、检索、统计和提示词组合的 Python 工具。

## 语言规范

- 除 `README_EN.md` 明确作为英文版文档外，其它面向用户或智能体阅读的文档优先使用中文。
- Python 代码中的标识符、JSON 字段名、CLI 命令名和参数名可以保持英文，以保证接口稳定。
- Python 脚本的帮助信息、报错信息、普通文本输出和注释，凡不影响兼容性的，优先使用中文。
- 新增或修改文档时，中文文档不要夹杂可翻译的英文标题或英文说明；英文只保留在专有名词、文件名、命令、字段名、代码和 `README_EN.md` 中。

## 数据规范

- JSON 文件保持 UTF-8 编码，并保持易读的缩进格式。
- 保留现有顶层 JSON key：
  - `actionLibrary`
  - `clothesLibrary`
  - `expressionLibrary`
  - `scenes`
- 每个库里的条目必须有稳定 `id`：
  - 动作：`action_0000`
  - 服装：`outfit_0000`
  - 表情：`expression_0000`
  - 场景：`scene_0000`
- 不要手动重排、复用、覆盖或补洞旧 id。数组顺序可以调整，但已存在条目的 id 必须保持稳定。
- 新 id 必须由现有数据扫描结果决定，保证全库唯一；不得只凭肉眼估算下一个编号。
- 新增数据应优先通过 `scripts/visual_prompt_atlas.py ingest` 入库，让脚本扫描现有数据并自动分配不冲突的 id。
- 不要新增单独的场景服装兼容 JSON 文件。场景服装适配关系由场景条目、服装条目和 `scripts/visual_prompt_atlas.py` 的组合逻辑共同推导。
- 跨库适配规则应优先落在 JSON 库字段里，再由 Python 加载；不要把姿态、场景服装或动作场景词表裸写成 Python 常量。
- 修改数据结构、数量统计、过滤语义或 id 语义时，同步更新 `README.md`、`README_EN.md`、`SKILL.md` 和相关 `references/*_INDEX.md`。
- `slots/identity/` 下的身份槽是本地私有数据，不能提交。
- 使用图谱生成真实感人物图片、人物写真提示词或其它会出现固定人物主体的结果时，默认必须使用 `slots/identity/` 下的身份槽固定人物身份，除非用户明确要求不固定身份。
- 如果用户未指定身份槽，先扫描 `slots/identity/*/` 中同时包含 `reference.jpg` 和 `description.md` 的可用槽；只有一个可用槽时直接使用，多个可用槽时询问用户选择。
- 如果没有可用身份槽，先提示用户提供人物参考图；收到参考图后由 AI 生成只描述脸部、发型和身体轮廓的 `description.md`，再继续生成，不要静默跳过身份固定。

## Python 工具规范

- Python 实现要保持朴素、清晰、可维护，优先小函数和明确的数据流，避免把业务规则散落在多个分支里。
- 不为了“灵活”引入过度抽象；优先沿用现有 CLI 风格、数据结构和校验函数。
- 入库、回填、校验这类会影响数据完整性的逻辑，要先 dry-run 可验证，再支持显式 `--write` 写入。
- 对外输出的 JSON key 要保持稳定；如果需要中文提示，放在人类可读文本或错误信息里，不随意改机器消费字段。
- 写脚本时优先使用标准库和清晰错误信息；失败路径要可解释，不要让普通 CLI 使用者看到无意义的 Python traceback。

## 验证

提交数据或工具改动前运行：

```bash
python3 scripts/visual_prompt_atlas.py validate --json
python3 scripts/visual_prompt_atlas.py stats --json
python3 scripts/visual_prompt_atlas.py compose --scene-name 客厅 --strict-compatible --count 3 --seed 1 --json
python3 scripts/visual_prompt_atlas.py compose --scene-name 卧室 --strict-compatible --count 3 --seed 1 --json
```

如果修改了 Python 脚本，还应运行：

```bash
python3 -m compileall -q scripts
git diff --check
```

## Git

除非用户明确要求，否则提交时使用仓库现有作者：

```text
xTreeRoot <xTreeRoot@users.noreply.github.com>
```
