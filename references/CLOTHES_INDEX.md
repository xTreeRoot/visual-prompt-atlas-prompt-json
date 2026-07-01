# 璃夏服装库索引

## 文件信息
- **文件名**：璃夏_服装Prompt库v2.json
- **位置**：references/
- **最后更新**：2026-03-30
- **格式**：情感化结构化格式

---

## 数据结构

### 格式说明（情感化）
```json
{
  "clothesLibrary": [
    {
      "description": "服装描述文本",
      "keywords": ["关键词数组"],
      "mood": {
        "情感标签": 等级（1-5）
      },
      "occasion": ["适用场景数组"]
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

---

## Spiciness等级说明

服装的性感程度分为 1-5 级：
- **1级**：清纯无性感元素
- **2级**：轻微性感
- **3级**：中等性感
- **4级**：明显性感
- **5级**：极致性感

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
- **温柔/优雅**：mood包含"温柔"、"恬静"、"优雅"（等级>=4）

### 按关键词筛选
- **黑丝**：keywords包含"黑丝"、"长筒袜"
- **白丝**：keywords包含"白丝"、"透明丝袜"
- **JK**：keywords包含"JK"、"校服"、"百褶裙"
- **比基尼**：keywords包含"比基尼"、"泳装"
- **连衣裙**：keywords包含"连衣裙"、"裙装"

### 按场景筛选
- **校园**：occasion包含"校园"
- **海滩**：occasion包含"海滩"、"泳池"
- **派对**：occasion包含"派对"、"夜店"

---

## 用户需求映射

| 用户说 | 转换条件 |
|--------|----------|
| "给我看点骚的" | mood包含"性感"、"诱惑"（等级>=4） |
| "给我看点清纯的" | mood包含"清纯"、"可爱"（等级>=4） |
| "给我看看黑丝" | keywords包含"黑丝" |
| "给我看看白丝" | keywords包含"白丝" |
| "JK校服" | keywords包含"JK"、"校服" |

---

## 组合筛选示例

### 清纯约会风
- mood: 清纯、可爱、甜美（等级>=4）
- occasion: 校园、约会对

### 性感夜店风
- mood: 性感、诱惑、妖娆（等级>=4）
- occasion: 派对、夜店

### 俏皮可爱风
- mood: 可爱、甜美、性感（等级2-3）
- occasion: 约会、派对

---

## API使用示例

### Python代码示例
```python
from scripts.library_loader import LibraryLoader

# 加载服装库
loader = LibraryLoader()
clothes = loader.load_clothes()

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
- 2026-03-30：更新为情感化结构化格式
- 2026-03-29：初始版本创建，包含2777件服装
