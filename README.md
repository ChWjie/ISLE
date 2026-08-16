# ISLE · 智弈法衡

智弈法衡是一个面向中国企业合规与争议分析的法律博弈平台。本仓库收录已确认的最终前端、后端与 SQLite 数据库版本，并针对 Tencent Cloud Studio 做了可直接运行的配置。

## 最终版特征

- 首页使用 ECharts 中国地图，地图数据位于 `frontend/public/maps/china.json`。
- 首页从后端 `/api/v1/events` 读取数据，内置 13 条国内企业合规案例。
- 前端保留了方案生成流式数据的分段缓冲修复。
- 后端包含得理法律检索的可选接入，凭据仅通过环境变量配置。
- 不配置 LLM 或外部检索密钥时，中国地图、国内案例列表和基础页面仍可运行；方案生成与博弈推演需要额外配置 LLM。

## 目录结构

```text
ISLE/
├── .vscode/preview.yml       # Cloud Studio 双服务启动配置
├── frontend/                 # Vue 3 + TypeScript + Vite + ECharts
├── backend/                  # FastAPI + SQLAlchemy
│   └── law_game.db           # 后端运行时数据库
└── database/
    └── law_game.db           # 最终数据库备份
```

`backend/law_game.db` 是默认运行数据库；`database/law_game.db` 是同版本备份。修改数据时请注意同步备份。

## Cloud Studio 部署（推荐）

Cloud Studio 适合云端开发、调试和 Demo 演示。预览链接需要工作空间和对应服务处于运行状态；如需 7×24 小时正式服务，建议后续迁移到云托管或容器服务。

1. 登录 [Cloud Studio](https://cloudstudio.net/)，点击「创建应用」。
2. 选择「从 Git 仓库导入」，填写：

   ```text
   https://github.com/ChWjie/ISLE.git
   ```

3. 选择 All In One 或同时包含 Node.js 22.12+ 与 Python 3.11+ 的环境，创建并进入工作空间。
4. 如果只查看中国地图和内置案例，可直接点击顶部「运行」。Cloud Studio 会读取 `.vscode/preview.yml`，自动安装依赖并启动：

   - 后端 API：`8000`
   - 前端：`5173`（主预览端口）

5. 在左侧「端口」插件中找到 `5173`，点击「查看预览」或「在浏览器中打开」。
6. 如需 AI 方案生成和博弈推演，在 Cloud Studio 终端执行：

   ```bash
   cp backend/.env.example backend/.env
   ```

   然后编辑 `backend/.env`，至少设置 `LLM_API_KEY`、`LLM_BASE_URL` 和 `LLM_MODEL`。使用得理检索时，再配置 `DELILEGAL_APP_ID` 与 `DELILEGAL_SECRET`。修改后在「端口」面板重启 `8000` 后端服务。

Cloud Studio 官方参考：[从 Git 仓库创建应用](https://ide.cloud.tencent.com/docs/guide/quick_start/developer/create-your-app/)、[`preview.yml` 运行配置](https://ide.cloud.tencent.com/docs/guide/quick_start/developer/how-to-run/)、[端口与 Web 预览](https://ide.cloud.tencent.com/docs/guide/code_editing/productivity_plugin/port-plug/)。

## 本地运行

需求：Node.js 22.12+ （或 20.19+）、Python 3.11+。

### 1. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

健康检查：`http://localhost:8000/health`

API 文档：`http://localhost:8000/docs`

### 2. 启动前端

在另一个终端中：

```bash
cd frontend
npm ci
npm run dev -- --host 0.0.0.0
```

打开 `http://localhost:5173`。Vite 会将同源 `/api` 请求代理到 `http://127.0.0.1:8000`。

## 配置说明

### 前端

`frontend/.env.example`：

```dotenv
VITE_API_BASE_URL=
```

- 留空：使用同源 `/api`，适合本地与 Cloud Studio。
- 前后端分开部署：填写公开的 HTTPS 后端根地址，不要带末尾 `/`。

### 后端

配置模板见 `backend/.env.example`。仓库不包含任何真实 API 密钥或云数据库密码，`backend/.env` 已被 Git 忽略。

## 验证命令

```bash
# 前端类型检查与生产构建
cd frontend && npm ci && npm run build

# 后端语法检查
cd backend && python3 -m compileall -q app

# 查看内置国内事件数量
sqlite3 backend/law_game.db 'SELECT COUNT(*) FROM events;'
```

## 安全提示

- 不要提交 `.env`、API Key、数据库密码或私有服务凭据。
- Cloud Studio 端口可设为「公开」或「仅自己可见」；调试期间建议将 `8000` 后端端口设为「仅自己可见」。
- 本项目用于技术演示与法律分析辅助，生成内容不构成正式法律意见。
