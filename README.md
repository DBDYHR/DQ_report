# 智能报告生成平台 (DQ Report)

基于 **Vue 3 + FastAPI** 的智能写作与报告生成系统：支持上传文档、联网检索、AI 生成开放报告，以及报告编辑、导出与模板管理。

---

## 已实现功能与效果

### 前端 + 后端均已实现

| 功能 | 说明 |
|------|------|
| **开放报告生成** | 在「聊天」页上传 PDF/DOCX/TXT 等材料，输入写作要求，调用后端 AI 生成 Markdown 报告。 |
| **联网检索** | 开启「联网搜索」后，先对报告主题做一次 DuckDuckGo 网页检索，展示检索结果卡片，用户确认后再生成报告；可选用检索内容或「不使用检索结果，直接生成」。 |
| **检索结果展示** | 展示检索词、每条结果的标题/摘要/链接，可点击链接新开页面；支持「确认并生成报告」与「直接生成」两种操作。 |
| **文件上传与解析** | 后端支持 PDF、DOCX、TXT 上传并解析为文本/摘要，供 AI 与报告使用。 |
| **报告 CRUD** | 报告的创建、列表、获取、更新均走后端 API；报告列表在「我的报告」展示，支持编辑、删除、预览。 |
| **报告编辑与预览** | 编辑页支持 Markdown 编辑、A4 文档预览、字体切换、保存、导出 Word。 |
| **AI 助手（编辑页）** | 在报告编辑页可调用 AI 润色/续写，请求体与开放报告接口一致（后端 open-report）。 |

### 前端有界面、后端未接或为演示

| 功能 | 说明 |
|------|------|
| **专业报告模式** | 聊天页可选择「专业」模式，目前为前端本地示例文案与打字机效果，未调用后端 AI。 |
| **向导式生成（/wizard）** | 选择模板 → 上传文件 → 开始生成：当前为前端模拟（固定 8 秒后复用一条预置报告），未调用后端文件解析与 AI 生成。 |
| **模板库（/templates）** | 模板分类与列表、新建/编辑/预览模板为前端 Store 与路由，未对接后端模板 CRUD。 |
| **报告数据持久化** | 报告列表与详情已对接后端；若后端未持久化到文件/数据库，重启后数据会丢失（当前为 JSON 文件存储）。 |

---

## 项目结构

```
DQ_report/
├── src/                 # Vue 3 前端
│   ├── views/           # 页面：ChatMode, PlatformMode, EditorView, ReportWizard, TemplatesView
│   ├── components/      # 编辑器、预览、侧边栏等
│   ├── api/             # 请求封装：ai, files, reports
│   ├── stores/          # Pinia：报告与模板状态
│   └── router/
├── server/              # FastAPI 后端
│   ├── app/
│   │   ├── api/endpoints/  # ai, files, reports, health
│   │   ├── models/         # 请求/响应模型
│   │   ├── services/       # ai_client, search_client, file_parser, reports_store
│   │   └── config.py
│   ├── requirements.txt
│   └── README.md         # 后端环境与接口说明
├── data/                # 后端使用的数据目录（上传文件、reports.json 等）
└── skills-main/         # （需自行放入）PPT 相关 Skill，见「后续规划」
```

---

## 如何使用

### 1. 环境要求

- **前端**：Node.js 18+，npm 或 pnpm
- **后端**：Python 3.10+，pip

### 2. 后端启动

```bash
cd server
pip install -r requirements.txt
cp .env.example .env   # 复制后编辑 .env，填写 AI 接口地址与 Key
```

编辑 `server/.env`：

```env
YEYSAI_BASE_URL=https://yeysai.com/v1
YEYSAI_MODEL=gpt-4o-mini
YEYSAI_API_KEY=sk-你的令牌
```

启动服务：

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- 健康检查：`GET http://localhost:8000/api/health`
- 接口文档：`http://localhost:8000/docs`（若已挂载）

### 3. 前端启动

```bash
npm install
npm run dev
```

浏览器访问控制台给出的本地地址（如 `http://localhost:5173`）。前端默认请求 `http://localhost:8000`，可在 `src/api/config.js` 中修改 `API_BASE_URL`。

### 4. 基本流程

1. 侧边栏进入「开启新报告」→ 聊天页。
2. 可选「开放」/「专业」模式；开放模式下可开关「联网搜索」。
3. 上传参考资料（或从模板库选模板占位），输入主题或写作要求，发送。
4. **联网搜索开启时**：先展示检索结果卡片，确认后点击「确认并生成报告」或「直接生成报告」。
5. 生成完成后跳转报告编辑页，可继续编辑、保存、导出 Word。

---

## 后端接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/health | 健康检查 |
| POST | /api/ai/search-for-report | 仅检索，返回 query + results，供前端展示 |
| POST | /api/ai/open-report | 生成开放报告（可带 search_results 预取结果） |
| POST | /api/files/upload | 文件上传与解析 |
| GET/POST | /api/reports | 报告列表 / 创建 |
| GET/PUT | /api/reports/{id} | 报告详情 / 更新 |

---

## 后续规划与 skills-main（PPT Skill）

- **PPT 能力**：本仓库规划接入「做 PPT」相关能力。请将 PPT 技能包放到项目下并命名为 `skills-main`（即项目根目录下存在 `skills-main/` 文件夹）。
  - **来源**：从 `D:\Skill\skills-main\skills-main` 整份复制或移动到 `DQ_report/skills-main`。
  - **内容**：Agent Skills 风格的技能包，内含 PPTX 的读取/编辑/创建说明与脚本（如 `skills/pptx/SKILL.md`、模板与排版建议、markitdown/pptxgenjs 等），计划与本系统集成，支持从报告或材料生成演示文稿。
- **skills-main 说明**：放入后详见 `skills-main/README.md` 与 `skills-main/skills/pptx/SKILL.md`。

---

## 其他说明

- 报告与上传文件默认落在项目下 `data/`，部署时注意备份或改为数据库/对象存储。
- 若出现「无法连接到 AI 服务」，请检查网络与代理（如 HTTP_PROXY/HTTPS_PROXY）及 `.env` 中的 `YEYSAI_BASE_URL` 是否可达。
- 上传到 GitHub 前建议将 `server/.env` 加入 `.gitignore`，仅提交 `.env.example`。
