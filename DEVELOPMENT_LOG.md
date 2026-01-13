# SD Photo Organizer 开发日志

> 📅 项目开始时间：2026-01-13  
> 🎯 目标：5天内完成可演示的MVP版本  
> 📖 本文档记录所有开发进度和代码修改，方便理解和二次开发

---

## 📋 项目概述

**SD卡照片整理与拍摄总结工具** - 帮助摄影爱好者从SD卡导入照片，自动按日期分类整理，并通过AI生成拍摄总结。

### 技术栈
| 组件 | 技术 | 说明 |
|------|------|------|
| 后端 | FastAPI (Python 3.11) | REST API服务 |
| 前端 | Vue 3 + Vite | 单页应用 |
| 数据库 | MySQL 8.0 (Docker) | 照片元数据存储 |
| AI | 多模态大模型API | 图片分类与总结生成 |

### 核心功能
1. ✅ 扫描SD卡目录，提取照片EXIF信息
2. ✅ JPG与RAW同名配对
3. ✅ 按 `YYYY-MM-DD/类别/` 规则整理到本地图库
4. ✅ 照片墙展示、筛选、精选标记
5. ✅ 导出精选照片（含RAW，可打包ZIP）
6. ✅ AI自动分类 + 生成拍摄总结

---

## 📁 项目结构

```
sd-photo-organizer/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py            # 应用入口
│   │   ├── api/
│   │   │   ├── routes/        # API路由
│   │   │   │   ├── photos.py  # 照片扫描/导入/查询
│   │   │   │   ├── ai.py      # AI分类
│   │   │   │   ├── summary.py # 总结生成
│   │   │   │   └── export.py  # 导出功能
│   │   │   └── schemas/       # Pydantic模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── scanner_service.py   # 扫描服务
│   │   │   ├── organizer_service.py # 整理服务
│   │   │   ├── ai_service.py        # AI服务
│   │   │   ├── summary_service.py   # 总结服务
│   │   │   └── export_service.py    # 导出服务
│   │   ├── db/                # 数据库
│   │   │   ├── session.py     # 数据库连接
│   │   │   ├── models.py      # ORM模型
│   │   │   └── photos_repo.py # CRUD操作
│   │   └── core/              # 核心工具
│   │       ├── config.py      # 配置读取
│   │       └── utils.py       # 通用工具
│   ├── storage/
│   │   └── thumbs/            # 缩略图存储
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/               # API封装
│   │   ├── pages/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   ├── router/            # 路由配置
│   │   └── App.vue
│   ├── package.json
│   └── .env.example
├── docker-compose.yml          # MySQL容器
├── DEVELOPMENT_LOG.md          # 本开发日志
└── README.md
```

---

## 🔄 开发记录

### Day 1 - 2026-01-13

#### 1.1 初始化后端项目结构

**创建的文件：**

| 文件路径 | 说明 |
|----------|------|
| `backend/app/main.py` | FastAPI应用入口，配置CORS、挂载路由和静态文件 |
| `backend/app/core/config.py` | 从.env读取配置（数据库、AI等） |
| `backend/app/core/utils.py` | 通用工具函数（SHA1计算、缩略图生成等） |
| `backend/app/db/session.py` | SQLAlchemy数据库连接 |
| `backend/app/db/models.py` | Photo ORM模型定义 |
| `backend/app/db/photos_repo.py` | 照片CRUD操作 |
| `backend/requirements.txt` | Python依赖包 |

**关键实现说明：**

1. **配置管理** (`core/config.py`)
   - 使用 `pydantic-settings` 从环境变量读取配置
   - 支持 `.env` 文件自动加载
   - 包含数据库、AI API、应用端口等配置

2. **数据库模型** (`db/models.py`)
   - `Photo` 模型对应 `photos` 表
   - 字段包括：文件路径、EXIF信息、AI分类、精选标记等
   - 使用 `sha1` 字段去重，避免重复导入

3. **工具函数** (`core/utils.py`)
   - `calculate_sha1()`: 分块计算文件SHA1，支持大文件
   - `generate_thumbnail()`: 生成512px宽缩略图
   - `parse_exif()`: 解析EXIF信息（拍摄时间、相机、镜头等）

---

## 🚀 启动指南

### 1. 启动MySQL数据库
```bash
cd sd-photo-organizer
docker compose up -d
```

### 2. 启动后端
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# 编辑 .env 填写AI API Key
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. 启动前端
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### 4. 访问
- 后端API文档：http://127.0.0.1:8000/docs
- 前端页面：http://127.0.0.1:5173

---

## 📝 API接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/photos/scan` | 扫描SD卡目录 |
| POST | `/photos/import` | 整理到Library |
| GET | `/photos` | 查询照片列表 |
| PATCH | `/photos/{id}` | 更新照片信息 |
| POST | `/ai/classify` | AI分类照片 |
| POST | `/summary/generate` | 生成拍摄总结 |
| POST | `/export/selected` | 导出精选照片 |

---

## ⚠️ 注意事项

1. **路径处理**：后端统一使用 `pathlib.Path`，避免Windows反斜杠问题
2. **AI调用**：只对JPG缩略图调用AI，RAW只做文件同步
3. **安全第一**：整理操作使用复制（copy），不删除SD卡原片
4. **API Key**：`.env` 文件已在 `.gitignore` 中，不要提交到仓库

---

## 🔧 后续更新

（此处将持续记录每次代码修改...）

---

## 📚 代码详解（新手友好）

### 后端架构说明

#### 1. 入口文件 `app/main.py`

这是整个后端的入口，主要做了以下事情：

```python
# 创建FastAPI应用
app = FastAPI(title="SD Photo Organizer")

# 配置CORS，允许前端跨域访问
app.add_middleware(CORSMiddleware, ...)

# 挂载静态文件（缩略图）
app.mount("/static/thumbs", StaticFiles(...))

# 注册API路由
app.include_router(photos_router)  # 照片相关接口
app.include_router(ai_router)      # AI分类接口
...
```

#### 2. 配置管理 `app/core/config.py`

使用`pydantic-settings`从环境变量读取配置：

```python
class Settings(BaseSettings):
    mysql_host: str = "127.0.0.1"  # 有默认值
    ai_api_key: str = ""           # 需要在.env中配置
    
    class Config:
        env_file = ".env"  # 自动读取.env文件
```

#### 3. 数据库模型 `app/db/models.py`

使用SQLAlchemy ORM定义Photo表：

```python
class Photo(Base):
    __tablename__ = "photos"
    
    id = Column(BigInteger, primary_key=True)
    file_name = Column(String(255), nullable=False)
    sha1 = Column(String(40), unique=True)  # 用于去重
    # ... 更多字段
```

#### 4. 服务层设计

服务层是**业务逻辑**的核心，按功能划分：

| 服务 | 文件 | 职责 |
|------|------|------|
| ScannerService | scanner_service.py | 扫描目录、解析EXIF、生成缩略图 |
| OrganizerService | organizer_service.py | 按规则复制文件到图库 |
| ExportService | export_service.py | 导出精选照片 |
| AIService | ai_service.py | 调用多模态API分类 |
| SummaryService | summary_service.py | 统计数据、生成总结 |

#### 5. API路由设计

路由层很"薄"，只做参数校验和调用服务：

```python
@router.post("/photos/scan")
async def scan_directory(request: ScanRequest, db: Session = Depends(get_db)):
    scanner = ScannerService(db)           # 创建服务实例
    result = scanner.scan_directory(...)   # 调用业务逻辑
    return ApiResponse(data=result)        # 统一返回格式
```

### 前端架构说明

#### 1. 项目结构

```
src/
├── api/          # API封装（不要在页面里直接写axios）
├── pages/        # 页面组件（3个主页面）
├── components/   # 可复用组件
├── router/       # 路由配置
└── styles/       # 全局样式
```

#### 2. API封装 `src/api/http.js`

统一配置axios，处理错误：

```javascript
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,  // 从环境变量读取
  timeout: 60000,
})

// 响应拦截器：统一错误处理
http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    ElMessage.error('请求失败')
    return Promise.reject(error)
  }
)
```

#### 3. 页面组件

| 页面 | 文件 | 功能 |
|------|------|------|
| 导入页 | ImportPage.vue | 输入路径、扫描、整理 |
| 照片墙 | GalleryPage.vue | 浏览、筛选、标记精选 |
| 总结页 | SummaryPage.vue | 图表展示、AI复盘 |

---

## ❓ 常见问题

### Q1: 后端启动报错 "ModuleNotFoundError"

确保激活了虚拟环境并安装了依赖：
```bash
cd backend
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Q2: 前端报 "Network Error"

检查后端是否启动，以及CORS配置是否正确。后端默认允许 `http://127.0.0.1:5173`。

### Q3: AI分类不工作

1. 检查 `backend/.env` 中的 `AI_API_KEY` 是否正确
2. 确认 `AI_BASE_URL` 和 `AI_MODEL` 配置正确
3. 查看后端控制台是否有错误信息

### Q4: 扫描很慢

对于大量照片（>1000张），扫描可能需要几分钟。这是因为需要：
- 计算每张照片的SHA1哈希
- 解析EXIF信息
- 生成缩略图

### Q5: 如何使用国产AI模型？

修改 `backend/.env`：
```env
# 例如使用通义千问
AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL=qwen-vl-max
AI_API_KEY=你的API Key
```

---

## 🎯 后续可优化方向

1. **性能优化**
   - 添加扫描进度条（WebSocket或轮询）
   - 缩略图懒加载
   - 虚拟滚动支持大量照片

2. **功能增强**
   - 照片详情弹窗
   - 批量编辑类别/标签
   - 地图视图（根据GPS信息）
   - 人脸识别分组

3. **用户体验**
   - 拖拽选择文件夹
   - 键盘快捷键
   - 暗色主题

4. **部署相关**
   - Docker一键部署
   - 生产环境配置
   - 日志记录完善
