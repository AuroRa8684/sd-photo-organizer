# SD Photo Organizer 📸

> SD卡照片整理与拍摄总结工具 - 帮助摄影爱好者高效管理照片

## ✨ 功能特点

- 📁 **智能扫描**：扫描SD卡目录，自动识别JPG照片并匹配RAW文件
- 📊 **EXIF解析**：提取拍摄时间、相机型号、镜头、焦距、ISO、光圈、快门等信息
- 📂 **自动整理**：按 `日期/类别` 规则将照片整理到本地图库
- 🖼️ **照片墙**：缩略图网格展示，支持多条件筛选
- ⭐ **精选标记**：标记精选照片，一键导出（含RAW）
- 🤖 **AI分类**：调用多模态大模型自动识别照片内容并分类
- 📈 **拍摄总结**：统计图表 + AI生成拍摄复盘文案

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI (Python 3.11) |
| 前端 | Vue 3 + Vite + Element Plus |
| 数据库 | MySQL 8.0 (Docker) |
| 图表 | ECharts |
| AI | OpenAI兼容接口（多模态） |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/sd-photo-organizer.git
cd sd-photo-organizer
```

### 2. 启动MySQL数据库

```bash
docker compose up -d
```

### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
.\.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 复制配置文件并编辑
copy .env.example .env
# 编辑 .env，填写 AI_API_KEY 等配置

# 启动服务
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 复制配置文件
copy .env.example .env

# 启动开发服务器
npm run dev
```

### 5. 访问应用

- 🌐 前端页面：http://127.0.0.1:5173
- 📚 API文档：http://127.0.0.1:8000/docs

## 📁 项目结构

```
sd-photo-organizer/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口
│   │   ├── api/           # API路由和模型
│   │   ├── services/      # 业务逻辑
│   │   ├── db/            # 数据库操作
│   │   └── core/          # 配置和工具
│   ├── storage/thumbs/    # 缩略图存储
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── api/           # API封装
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   └── router/        # 路由配置
│   └── package.json
├── docker-compose.yml      # MySQL容器配置
├── DEVELOPMENT_LOG.md      # 开发日志
└── README.md
```

## 📖 使用流程

1. **导入照片**
   - 输入SD卡目录路径（如 `D:\DCIM`）
   - 点击"扫描"读取照片信息
   - 输入图库目录（如 `D:\PhotoLibrary`）
   - 点击"整理到图库"

2. **浏览照片**
   - 查看缩略图墙
   - 按日期、类别、ISO等条件筛选
   - 勾选复选框标记精选照片

3. **AI分类**
   - 在照片墙选择照片
   - 点击"AI分类"自动识别内容

4. **生成总结**
   - 选择日期范围
   - 点击"生成总结"
   - 查看统计图表和AI复盘文案

5. **导出精选**
   - 标记精选照片后
   - 点击"导出精选"
   - 选择导出目录，可打包ZIP

## ⚙️ 配置说明

### 后端配置 (backend/.env)

```env
# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=sd_user
MYSQL_PASSWORD=sd_pass
MYSQL_DB=sd_photo

# AI API（支持OpenAI兼容接口）
AI_API_KEY=your_api_key_here
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o
```

### 前端配置 (frontend/.env)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 📝 开发文档

详细的开发记录和代码说明请查看 [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md)

## 📄 License

MIT License
