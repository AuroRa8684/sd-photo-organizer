# PhotoFlow 

> 智能照片整理与拍摄总结工具 - 帮助摄影爱好者高效管理照片

##  功能特点

-  **智能扫描**：扫描SD卡目录，自动识别JPG照片并匹配RAW文件
-  **EXIF解析**：提取拍摄时间、相机型号、镜头、焦距、ISO、光圈、快门等信息
-  **自动整理**：按 日期/类别 规则将照片整理到本地图库
-  **照片墙**：缩略图网格展示，支持多条件筛选
-  **精选标记**：标记精选照片，一键导出（含RAW）
-  **AI分类**：调用多模态大模型自动识别照片内容并分类
-  **拍摄总结**：统计图表 + AI生成拍摄复盘文案（含社交媒体发布建议）

##  技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI (Python 3.11) |
| 前端 | Vue 3 + Vite + Element Plus |
| 数据库 | SQLite（轻量级，无需额外安装） |
| 图表 | ECharts |
| AI | OpenAI兼容接口（多模态） |

##  快速开始

### 方式一：一键启动（推荐）

双击运行 `start_all.bat`

### 方式二：手动启动

#### 1. 启动后端

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. 启动前端

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### 3. 访问应用

-  前端页面：http://127.0.0.1:5173
-  API文档：http://127.0.0.1:8000/docs

##  配置说明

### 后端配置 (backend/.env)

```env
AI_API_KEY=your_api_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o
```

### 前端配置 (frontend/.env)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

##  常用命令

- `start_all.bat` - 一键启动前后端
- `reset_database.bat` - 重置数据库
- `start_backend.bat` - 单独启动后端
- `start_frontend.bat` - 单独启动前端

##  License

MIT License
