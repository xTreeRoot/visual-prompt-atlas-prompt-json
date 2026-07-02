# 表情库索引

## 文件信息
- **文件名**：璃夏_表情Prompt库v2.json
- **位置**：references/
- **最后更新**：2026-03-30
- **格式**：情感化结构化格式

---

## 数据结构

### 格式说明（情感化）
```json
{
  "expressionLibrary": [
    {
      "description": "表情描述文本",
      "keywords": ["关键词数组"],
      "mood": {
        "情感标签": 等级（1-5）
      },
      "eyes": {
        "look": "眼神状态",
        "direction": "眼神方向",
        "state": "眼睛状态",
        "action": "特殊动作"
      },
      "mouth": {
        "shape": "嘴角形态",
        "detail": "细节描述"
      },
      "cheek": {
        "color": "脸颊颜色",
        "blushLevel": 1-4
      },
      "overall": {
        "emotion": "整体情感",
        "intensity": 1-4
      }
    }
  ]
}
```

---

## 情感标签体系

### 清纯系
- 清纯、清新、青春、纯真

### 撒娇系
- 可爱、甜美、俏皮、撒娇、灵动、活泼、元气

### 性感系
- 性感、诱惑、妖娆、冷艳、魅惑、妖艳

### 温柔系
- 温柔、恬静、知性、优雅、温暖、安静、柔美

### 其他
- 忧郁、忧伤、冷漠、高冷

---

## 筛选维度说明

### 1. Eyes（眼睛）
**look（眼神状态）**：
- 清澈、明亮、温柔、温暖、灵动、俏皮
- 迷离、诱惑、妖娆、魅惑
- 无辜、纯真、青春
- 冰冷、高冷、冷漠、忧郁
- 专注、认真、深情

**direction（眼神方向）**：
- 前方、看镜头
- 侧看、侧视
- 低头看下方
- 仰视、看上方
- 漫不经心

**state（眼睛状态）**：
- 正常
- 睁大
- 眯起
- 半闭
- 闭目

**action（特殊动作，可选）**：
- 眨眼
- 眨左眼（单眼眨眼）
- 眨右眼（单眼眨眼）

### 2. Mouth（嘴巴）
**shape（嘴角形态）**：
- 微笑
- 大笑
- 抿嘴
- 咬唇
- 嘟嘴
- 不笑
- 微勾
- 张嘴

**detail（细节描述）**：
- 嘴角上扬约15度
- 嘴角轻微上扬
- 露出洁白的牙齿
- 嘴唇微张
- 嘴角微微抿起

### 3. Cheek（脸颊）
**color（脸颊颜色）**：
- 无红、无脸红
- 微红
- 明显红
- 深红、潮红

**blushLevel（脸红等级，1-4）**：
- 1级：无脸红
- 2级：微红
- 3级：明显红
- 4级：深红、潮红

### 4. Overall（整体）
**emotion（整体情感）**：
- 用一句话概括整体表情的情感
- 如：甜美、冷艳、俏皮、忧郁、无辜、性感、温柔等

**intensity（表情强度，1-4）**：
- 1级：平淡
- 2级：明显
- 3级：强烈
- 4级：非常强烈

---

## 快速筛选指南

### 按情感筛选
- **温柔/甜美**：mood包含"温柔"、"甜美"（等级>=4）
- **可爱/俏皮**：mood包含"可爱"、"俏皮"、"灵动"（等级>=4）
- **性感/诱惑**：mood包含"性感"、"诱惑"、"妖娆"（等级>=4）
- **害羞/羞涩**：mood包含"害羞"、"羞涩"（等级>=4）
- **高冷/冷艳**：mood包含"高冷"、"冷艳"（等级>=4）
- **忧郁/忧伤**：mood包含"忧郁"、"忧伤"（等级>=4）

### 按眼睛筛选
- **看镜头**：eyes.direction == "看镜头"
- **眼神清澈**：eyes.look == "清澈" or "明亮"
- **眼神迷离**：eyes.look == "迷离" or "诱惑"
- **眨眼**：eyes.action == "眨眼"

### 按嘴巴筛选
- **微笑**：mouth.shape == "微笑"
- **不笑**：mouth.shape in ["不笑", "抿嘴"]
- **抿嘴**：mouth.shape == "抿嘴"
- **嘟嘴**：mouth.shape == "嘟嘴"

### 按脸颊筛选
- **明显脸红**：cheek.blushLevel >= 3
- **微红**：cheek.blushLevel == 2
- **无脸红**：cheek.blushLevel == 1

---

## 用户需求映射

| 用户说 | 转换条件 |
|--------|----------|
| "对我微笑" | eyes.direction == "看镜头" + mouth.shape == "微笑" + mood包含"甜美、温柔" |
| "诱惑地看着我" | eyes.look == "诱惑" + eyes.direction == "看镜头" + mouth.shape in ["微勾", "不笑"] |
| "害羞的样子" | cheek.blushLevel >= 3 + mood包含"害羞" 或 mouth.shape == "嘟嘴/抿嘴" |
| "高冷的样子" | eyes.look in ["冰冷", "高冷", "冷漠"] + mouth.shape in ["不笑", "抿嘴"] |
| "俏皮地眨眨眼" | eyes.action == "眨眼" + mood包含"俏皮" |
| "清纯的笑脸" | mood包含"清纯"、"甜美" + mouth.shape == "微笑" + eyes.look in ["清澈", "明亮"] |
| "没有表情" | mouth.shape == "不笑" + cheek.blushLevel == 1 + overall.intensity == 1 |
| "脸红红的" | cheek.blushLevel >= 3 |

---

## 组合筛选示例

### 清甜互动风
- mood: 温柔、甜美（等级>=4）
- eyes.direction: 看镜头
- eyes.look: 清澈、明亮
- mouth.shape: 微笑

### 性感诱惑风
- mood: 性感、诱惑（等级>=4）
- eyes.look: 迷离、诱惑
- eyes.direction: 看镜头
- mouth.shape: 微勾或不笑

### 俏皮可爱风
- mood: 可爱、俏皮（等级>=4）
- eyes.action: 眨眼
- mouth.shape: 微笑
- cheek.blushLevel: 2-3

### 高冷御姐风
- mood: 冷艳、高冷（等级>=4）
- eyes.look: 冰冷、高冷
- mouth.shape: 不笑或抿嘴
- cheek.blushLevel: 1

---

## API使用示例

### Python代码示例
```python
from scripts.library_loader import LibraryLoader

# 加载表情库
loader = LibraryLoader()
expressions = loader.load_expressions()

# 按情感筛选
sweet_expressions = [
    e for e in expressions
    if any(e['mood'].get(mood, 0) >= 4 for mood in ['甜美', '温柔'])
]

# 按眼睛筛选
look_camera = [
    e for e in expressions
    if e['eyes']['direction'] == '看镜头'
]

# 按嘴巴筛选
smiling = [
    e for e in expressions
    if e['mouth']['shape'] == '微笑'
]

# 按脸颊筛选
blushing = [
    e for e in expressions
    if e['cheek']['blushLevel'] >= 3
]

# 组合筛选
result = [
    e for e in expressions
    if any(e['mood'].get(mood, 0) >= 4 for mood in ['可爱', '俏皮'])
    and e['eyes']['direction'] == '看镜头'
    and e['mouth']['shape'] == '微笑'
    and e['cheek']['blushLevel'] >= 2
]
```

---

## 与服装库、动作库协同

三个库使用**相同的情感标签体系**，实现精准的情感匹配：

### 清纯约会风
- 服装：清纯、可爱、甜美（优先日常、校园、约会）
- 动作：可爱、甜美、互动性3-4
- 表情：清纯、甜美、微笑+看镜头+眼神清澈
- 场景：校园或约会场所

### 性感夜店风
- 服装：性感、诱惑、妖娆（优先派对、舞台、夜景）
- 动作：性感、诱惑、互动性4-5
- 表情：性感、诱惑、眼神迷离+嘴角微勾+看镜头
- 场景：夜店或都市夜景

### 俏皮可爱风
- 服装：可爱、甜美、俏皮（优先约会、派对）
- 动作：可爱、俏皮、动态性3-4
- 表情：可爱、俏皮、眨眼+微笑+脸红
- 场景：室内或户外休闲

### 高冷御姐风
- 服装：冷艳、优雅（优先正式、职场、夜景）
- 动作：冷艳、优雅、互动性2-3
- 表情：冷艳、高冷、眼神冰冷+不笑+无脸红
- 场景：都市或室内

---

## 更新记录
- 2026-03-30：更新为情感化结构化格式
