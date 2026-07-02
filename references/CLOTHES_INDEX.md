# 璃夏服装库索引

## 文件信息
- **文件名**：璃夏_服装Prompt库v2.json
- **位置**：references/
- **最后更新**：2026-07-02
- **格式**：情感化结构化格式

---

## 数据结构

### 格式说明（情感化）
```json
{
  "clothesLibrary": [
    {
      "id": "outfit_0000",
      "description": "服装描述文本",
      "keywords": ["关键词数组"],
      "mood": {
        "情感标签": 等级（1-5）
      },
      "occasion": ["标准化适用场合数组"],
      "original_occasion": ["可选：原始适用场合数组"]
    }
  ]
}
```

---

## 稳定 ID

- 每条服装记录都有稳定 `id`，格式为 `outfit_0000`。
- 首轮 id 按当前数组位置回填；后续新增服装应通过 `python3 scripts/visual_prompt_atlas.py ingest outfits <file> --write` 分配新 id。
- 数组可以重排，但旧 id 不应重排或复用。使用 `compose --outfit-id outfit_0000` 可锁定指定服装。

---

## 场景适配字段

- `occasion`：标准化后的适用场合，用于和场景 `compatible_outfit_occasions` 做正向匹配。
- `original_occasion`：保留原始场合描述，组合脚本也会参与匹配；没有该字段时可省略。
- `keywords`：会和场景 `forbidden_outfit_keywords` 对照，用于过滤明显违和穿搭。

---

## 情感标签体系

### 清纯系
- 清纯、清新、青春、纯真

### 撒娇系
- 可爱、甜美、俏皮、撒娇、灵动、活泼、元气

### 性感系
- 性感、诱惑、妖娆、冷艳、魅惑、妖艳

### 成熟系
- 成熟、成人化、成年女性、轻熟

### 温柔系
- 温柔、恬静、知性、优雅、温暖、安静、柔美

---

## 风格强度说明

当前 JSON 不包含独立的 `spiciness` 数值字段。需要控制服装表达强度时，优先结合 `mood`、`keywords` 与 `occasion` 判断：
- 清纯、清新、青春、日常、校园：偏清爽自然
- 优雅、知性、正式、职场：偏成熟克制
- 性感、诱惑、魅惑、派对、舞台：偏强烈写真表达
- 成熟、成人化、成年女性、夜景、约会：偏成熟女性都市表达

---

## 场景分类

### 校园
- JK、校服、学生穿搭

### 海滩
- 比基尼、泳装、度假风

### 都市
- 都市时尚、夜生活、职场

### 居家
- 家居服、睡衣、休闲装

### 约会
- 连衣裙、甜美造型

### 派对
- 性感装、夜店风

### 运动
- 运动装、健身服

### 工作
- 职场穿搭、通勤装

---

## 快速筛选指南

### 按情感筛选
- **清纯/清新**：mood包含"清纯"、"清新"、"青春"（等级>=4）
- **可爱/甜美**：mood包含"可爱"、"甜美"、"俏皮"（等级>=4）
- **性感/诱惑**：mood包含"性感"、"诱惑"、"妖娆"（等级>=4）
- **成熟/成人化**：mood包含"成熟"（等级>=4）或keywords包含"成人化"、"成年女性"
- **温柔/优雅**：mood包含"温柔"、"恬静"、"优雅"（等级>=4）

### 按关键词筛选
- **黑丝**：keywords包含"黑丝"、"长筒袜"
- **白丝**：keywords包含"白丝"、"透明丝袜"
- **JK**：keywords包含"JK"、"校服"、"百褶裙"
- **比基尼**：keywords包含"比基尼"、"泳装"
- **连衣裙**：keywords包含"连衣裙"、"裙装"
- **成熟大衣/长裤**：keywords包含"大衣"、"修身长裤"、"长裤"，并优先匹配"成人化"、"成熟"、"性感"、"诱惑"

### 按场景筛选
- **校园**：occasion包含"校园"
- **海滩**：occasion包含"海滩"、"泳池"
- **派对**：occasion包含"派对"、"夜店"

---

## 用户需求映射

| 用户说 | 转换条件 |
|--------|----------|
| "给我看点骚的" | mood包含"性感"、"诱惑"（等级>=4） |
| "成熟性感大衣/长裤" | keywords包含"大衣"、"修身长裤"、"长裤"，且mood包含"成熟"、"性感"、"诱惑" |
| "给我看点清纯的" | mood包含"清纯"、"可爱"（等级>=4） |
| "给我看看黑丝" | keywords包含"黑丝" |
| "给我看看白丝" | keywords包含"白丝" |
| "JK校服" | keywords包含"JK"、"校服" |

---

## 组合筛选示例

### 清纯约会风
- mood: 清纯、可爱、甜美（等级>=4）
- occasion: 校园、约会

### 性感夜店风
- mood: 性感、诱惑、妖娆（等级>=4）
- occasion: 派对、夜店

### 俏皮可爱风
- mood: 可爱、甜美、性感（等级2-3）
- occasion: 约会、派对

---

## 程序使用示例

### Python 代码示例
```python
import json
from pathlib import Path

clothes = json.loads(
    Path("references/璃夏_服装Prompt库v2.json").read_text(encoding="utf-8")
)["clothesLibrary"]

# 按情感筛选
sweet_clothes = [
    c for c in clothes
    if any(c['mood'].get(mood, 0) >= 4 for mood in ['可爱', '甜美'])
]

# 按关键词筛选
stockings = [
    c for c in clothes
    if any(keyword in c['keywords'] for keyword in ['黑丝', '白丝'])
]

# 按场景筛选
date_clothes = [
    c for c in clothes
    if any(scene in c.get('occasion', []) for scene in ['校园', '约会'])
]

# 组合筛选
result = [
    c for c in clothes
    if any(c['mood'].get(mood, 0) >= 4 for mood in ['清纯', '可爱'])
    and any(keyword in c['keywords'] for keyword in ['JK', '百褶裙'])
]
```

---

## 更新记录
- 2026-07-02：回填稳定 id，并更新入库、检索与锁定说明；当前服装库 508 条
- 2026-03-30：更新为情感化结构化格式
- 2026-03-29：初始版本创建，包含2777件服装
