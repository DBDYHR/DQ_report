---
name: "well-logging-report"
description: "撰写测井解释报告，包含8章固定结构：概述、测井质量、处理参数、新技术、成果分析、建议、图表目录、附录。Invoke when user needs to write a well logging interpretation report or mentions any of the 8 chapters."
---

# 测井解释报告写作

## 概述

本 Skill 用于协助撰写专业的测井解释报告，报告采用固定的8章结构，涵盖从基础信息到附录的完整内容。

## 报告结构

### 一、概述
- **内容来源**：专业软件 API 接口
- **数据需求**：基础信息表
- **API 接口**：`GET /api/well/{well_id}/basic-info`
- **输出内容**：
  - 井号、井型、井位坐标
  - 完钻井深、完钻层位
  - 开完钻日期
  - 测井目的

### 二、测井内容及质量评定
- **内容来源**：专业软件 API 接口
- **数据需求**：测井曲线施工质量评价表
- **API 接口**：`GET /api/well/{well_id}/quality-evaluation`
- **输出内容**：
  - 测井项目列表
  - 各曲线质量评价
  - 施工质量综合评定

### 三、测井解释程序处理参数
- **内容来源**：专业软件 API 接口
- **数据需求**：处理参数表
- **API 接口**：`GET /api/well/{well_id}/processing-params`
- **输出内容**：
  - 解释模型选择
  - 关键参数设置
  - 处理流程说明

### 四、新技术应用情况
- **内容来源**：知识库查询
- **查询方式**：检索与当前井相关的测井技术
- **输出内容**：
  - 应用的新技术列表
  - 技术原理简述
  - 应用效果说明

### 五、解释成果及分析
- **内容来源**：基于其他章节数据自动生成 + Few-shot 学习
- **写作风格**："八股"式分析性内容
- **预留位置**：等待用户提供示例进行 Few-shot 训练
- **预期内容**：
  - 储层识别结果分析
  - 流体性质判断
  - 物性参数解释
  - 综合评价结论

### 六、建议及要求
- **内容来源**：自由发挥 + 知识库历史经验
- **输出内容**：
  - 后续工作建议
  - 注意事项
  - 相关历史经验参考

### 七、图、表目录
- **内容来源**：第八章附录中所有图表的汇总
- **输出格式**：表格形式
- **包含字段**：
  - 序号
  - 图/表名称
  - 页码/位置

### 八、附录
- **内容来源**：专业软件 API 接口
- **数据需求**：所有与井相关的测井图表
- **API 接口**：`GET /api/well/{well_id}/appendix-charts`
- **输出内容**：
  - 测井曲线图
  - 解释成果图
  - 交会图
  - 数据表

## API 接口预留

### 基础信息接口
```
GET /api/well/{well_id}/basic-info
Response: {
  "well_name": "",
  "well_type": "",
  "coordinates": {"x": 0, "y": 0},
  "total_depth": 0,
  "target_formation": "",
  "spud_date": "",
  "completion_date": "",
  "logging_objective": ""
}
```

### 质量评价接口
```
GET /api/well/{well_id}/quality-evaluation
Response: {
  "logging_items": [],
  "curve_quality": [],
  "overall_evaluation": ""
}
```

### 处理参数接口
```
GET /api/well/{well_id}/processing-params
Response: {
  "interpretation_model": "",
  "key_parameters": {},
  "processing_flow": []
}
```

### 附录图表接口
```
GET /api/well/{well_id}/appendix-charts
Response: {
  "charts": [
    {"name": "", "type": "", "url": ""}
  ]
}
```

## 知识库查询

### 新技术查询
```
Query: 井号 {well_id} 应用的测井新技术
Return: 技术列表及说明
```

### 历史经验查询
```
Query: 类似井况 {formation_type} 的历史建议
Return: 历史经验总结
```

## 使用流程

1. **获取井号**：从用户输入中提取井号信息
2. **调用 API**：依次调用各章节所需的 API 接口
3. **查询知识库**：获取新技术和历史经验信息
4. **生成报告**：按8章结构组织内容
5. **预留分析章节**：第五章内容等待 Few-shot 示例

## 注意事项

- 所有 API 调用均为预留接口，需根据实际系统实现
- 第五章内容需要用户提供示例进行 Few-shot 训练
- 图表目录需在第八章内容确定后生成
- 报告格式遵循行业规范
