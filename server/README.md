# DQ Report Backend (FastAPI)

这是智能报告生成平台的后端服务，基于 **Python + FastAPI** 实现，提供：

- AI 写作接口：`POST /api/ai/open-report`
- 文件上传与解析接口：`POST /api/files/upload`
- 报告持久化接口：`GET/POST/PUT /api/reports`

## 环境准备

1. 安装 Python（建议 3.10+）。
2. 安装依赖：

```bash
cd server
pip install -r requirements.txt
```

3. 配置模型相关环境变量（以 yeysai 为例，具体值按你拿到的文档填写）：

**方式一：在 `.env` 文件中配置（推荐）**

在 `server` 目录下复制示例文件并填写你的配置：

```bash
cd server
cp .env.example .env   # Windows PowerShell 可用：Copy-Item .env.example .env
```

然后编辑 `.env`：

```bash
YEYSAI_BASE_URL=https://yeysai.com/v1
YEYSAI_MODEL=gpt-4o-mini
YEYSAI_API_KEY=sk-你的令牌
```

**方式二：使用命令行临时设置环境变量**

```bash
set YEYSAI_BASE_URL=https://yeysai.com/v1
set YEYSAI_API_KEY=你的apikey
set YEYSAI_MODEL=你的模型名称
```

（在 PowerShell 中也可以用 `$env:YEYSAI_BASE_URL="..."` 这种方式临时设置）

## 启动服务

在 `server` 目录下运行：

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后，你可以访问：

- 健康检查（基础）：`GET http://localhost:8000/health`
- 健康检查（API）：`GET http://localhost:8000/api/health`

## 关键接口示例

### 1. AI 开放报告生成

`POST http://localhost:8000/api/ai/open-report`

```json
{
  "task_type": "open_report",
  "title": "开放报告示例",
  "outline": "一、背景 二、主要内容 三、结论与建议",
  "draft": "这里是已有的一些草稿内容……",
  "materials": [
    {
      "file_id": "file-1",
      "name": "材料1.txt",
      "text": "这里是解析后的全文……",
      "summary": "这里是材料摘要……"
    }
  ],
  "user_config": {
    "tone": "formal",
    "length": "long"
  }
}
```

返回：

```json
{
  "content": "# 标题\n这里是模型生成或润色后的 Markdown 报告内容……"
}
```

### 2. 文件上传解析

`POST http://localhost:8000/api/files/upload`

`multipart/form-data`，字段名为 `file`。

返回：

```json
{
  "file_id": "uuid",
  "name": "xx.docx",
  "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text": "解析得到的全文……",
  "summary": "前若干字符作为摘要……"
}
```

### 3. 报告 CRUD（最小版）

- `GET  /api/reports`          列出全部报告
- `POST /api/reports`          创建报告
- `GET  /api/reports/{id}`     获取单个报告
- `PUT  /api/reports/{id}`     更新报告

创建示例：

```json
{
  "title": "开放报告示例",
  "type": "open_report",
  "content": "# 标题\n这里是正文……",
  "sources": ["材料1.txt", "材料2.pdf"]
}
```

后续可以在前端中将 `useReportStore` 的增删改查逐步改为调用这些接口。***
