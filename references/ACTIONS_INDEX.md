# 璃夏动作库索引

## 文件信息
- **文件名**：璃夏_动作Prompt库v2.json
- **位置**：references/
- **最后更新**：2026-03-30
- **格式**：情感化结构化格式

---

## 数据结构

### 格式说明（情感化）
```json
{
  "actionLibrary": [
    {
      "description": "动作描述文本",
      "keywords": ["关键词数组"],
      "mood": {
        "情感标签": 等级（1-5）
      },
      "interaction": {
        "direction": "镜头/用户/无人",
        "level": 1-5
      },
      "dynamic": {
        "state": "静止/微动/动起来",
        "intensity": 1-5
      },
      "pose": {
        "type": "站/坐/躺/跪/蹲/跳/其他",
        "view": "正面/侧面/背面/俯视/仰视"
      }
    }
  ]
}
```

---

## 情感标签体系

### 清纯系
- 清纯、清新、青春

### 撒娇系
- 可爱、甜美、俏皮、撒娇、灵动、活泼、元气

### 性感系
- 性感、诱惑、妖娆、冷艳、魅惑、妖艳

### 温柔系
- 温柔、恬静、知性、优雅、温暖、安静、柔美

### 其他
- 慵懒、活力

---

## 筛选维度说明

### 1. Mood（情感标签）
从情感标签库中选择相关标签，并评定 1-5 等级：
- **5级**（主导）：该情感是核心特征
- **4级**（明显）：该情感非常明显
- **3级**（中等）：该情感中等程度
- **2级**（较弱）：该情感轻微
- **1级**（极轻微）：该情感极轻微

### 2. Interaction（交互性）
**direction（方向）**：
- `镜头`：面向镜头
- `用户`：仿佛与用户互动
- `无人`：不面向特定对象

**level（等级，1-5）**：
- 5级（强互动）：挥手打招呼、飞吻、伸手要抱抱
- 4级（明显互动）：注视镜头、微笑、眨眼
- 3级（中等互动）：稍微偏向镜头、轻微互动
- 2级（轻微互动）：偶然看向镜头
- 1级（无互动）：完全沉浸在动作中

### 3. Dynamic（动态性）
**state（状态）**：
- `静止`：完全静止
- `微动`：轻微摆动、呼吸感
- `动起来`：明显的动作

**intensity（强度，1-5）**：
- 5级（高动态）：跳跃、旋转、舞蹈动作
- 4级（中高动态）：走路、奔跑、转身
- 3级（中等动态）：轻微转身、挥手
- 2级（低动态）：轻微摆动、调整姿势
- 1级（静止）：站立、坐着不动

### 4. Pose（姿态）
**type（类型）**：
- 站、坐、躺、跪、蹲、跳、走、跑、旋转、其他

**view（视角）**：
- 正面、侧面、背面、俯视、仰视、45度角

---

## 快速筛选指南

### 按情感筛选
- **温柔/甜蜜**：mood包含"温柔"、"甜美"（等级>=4）
- **可爱/俏皮**：mood包含"可爱"、"俏皮"、"灵动"（等级>=4）
- **性感/诱惑**：mood包含"性感"、"诱惑"、"妖娆"（等级>=4）
- **慵懒/放松**：mood包含"慵懒"（等级>=4）
- **自信/活力**：mood包含"自信"、"活力"（等级>=4）

### 按交互性筛选
- **强互动**：interaction.level >= 4 + interaction.direction == "镜头"
- **中等互动**：interaction.level == 3
- **无互动**：interaction.level <= 2

### 按动态性筛选
- **高动态**：dynamic.intensity >= 4
- **中等动态**：dynamic.intensity == 3
- **低动态**：dynamic.intensity <= 2

### 按姿态筛选
- **站姿**：pose.type == "站"
- **坐姿**：pose.type == "坐"
- **躺姿**：pose.type == "躺"
- **正面**：pose.view == "正面"
- **侧面**：pose.view == "侧面"

---

## 组合筛选示例

### 清甜互动风
- mood: 温柔、甜美（等级>=4）
- interaction.level: 4
- pose.view: 正面

### 性感诱惑风
- mood: 性感、诱惑（等级>=4）
- interaction.level: 4
- dynamic.intensity: 2-3

### 活力动感风
- mood: 活力、可爱（等级>=4）
- dynamic.intensity: 4-5
- pose.type: 跳、跑、走

---

## 使用建议

### 与服装库、表情库协同
三个库使用**相同的情感标签体系**，实现精准的情感匹配：

**清纯约会风**
- 服装：清纯、可爱、甜美（spiciness: 1-2）
- 动作：可爱、甜美、互动性3-4
- 表情：清纯、甜美、微笑+看镜头+眼神清澈

**性感夜店风**
- 服装：性感、诱惑、妖娆（spiciness: 4-5）
- 动作：性感、诱惑、互动性4-5
- 表情：性感、诱惑、眼神迷离+嘴角微勾+看镜头

**俏皮可爱风**
- 服装：可爱、甜美、小性感（spiciness: 2-3）
- 动作：可爱、俏皮、动态性3-4
- 表情：可爱、俏皮、眨眼+微笑+脸红

**高冷御姐风**
- 服装：冷艳、优雅（spiciness: 3-4）
- 动作：冷艳、优雅、互动性2-3
- 表情：冷艳、高冷、眼神冰冷+不笑+无脸红

---

## API使用示例

### Python代码示例
```python
from scripts.library_loader import LibraryLoader

# 加载动作库
loader = LibraryLoader()
actions = loader.load_actions()

# 按情感筛选
sweet_actions = [
    a for a in actions
    if any(a['mood'].get(mood, 0) >= 4 for mood in ['温柔', '甜美'])
]

# 按交互性筛选
interactive_actions = [
    a for a in actions
    if a['interaction']['level'] >= 4
]

# 按动态性筛选
dynamic_actions = [
    a for a in actions
    if a['dynamic']['intensity'] >= 4
]

# 组合筛选
result = [
    a for a in actions
    if any(a['mood'].get(mood, 0) >= 4 for mood in ['可爱', '俏皮'])
    and a['interaction']['level'] >= 3
    and a['dynamic']['state'] == '微动'
]
```

---

## 更新记录
- 2026-03-30：更新为情感化结构化格式
- 2026-03-29：初始版本创建，包含625个动作
