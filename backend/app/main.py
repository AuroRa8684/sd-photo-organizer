"""
SD Photo Organizer - FastAPI 后端应用入口

这是应用的主入口文件，负责：
1. 创建 FastAPI 应用实例
2. 配置 CORS（跨域资源共享）
3. 挂载 API 路由
4. 挂载静态文件目录（缩略图）
5. 初始化数据库
"""
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import get_settings
from .db import init_db
from .api.routes import photos_router, ai_router, summary_router, export_router


# 获取配置
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    print("🚀 正在初始化数据库...")
    init_db()
    print("✅ 数据库初始化完成")
    
    # 确保缩略图目录存在
    settings.thumbs_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 缩略图目录: {settings.thumbs_path}")
    
    yield
    
    # 关闭时执行
    print("👋 应用正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="SD Photo Organizer",
    description="SD卡照片整理与拍摄总结工具 - API文档",
    version="1.0.0",
    lifespan=lifespan,
)


# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",  # Vite 默认端口
        "http://127.0.0.1:5174",  # Vite 备用端口
        "http://127.0.0.1:5175",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载静态文件目录（缩略图）
# 前端可通过 /static/thumbs/{sha1}.jpg 访问缩略图
thumbs_dir = settings.thumbs_path
thumbs_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/thumbs", StaticFiles(directory=str(thumbs_dir)), name="thumbs")


# 注册 API 路由
app.include_router(photos_router)
app.include_router(ai_router)
app.include_router(summary_router)
app.include_router(export_router)


# 健康检查接口
@app.get("/health", tags=["系统"])
async def health_check():
    """
    健康检查接口
    用于确认后端服务是否正常运行
    """
    return {"status": "ok", "message": "SD Photo Organizer 后端服务运行正常"}


@app.get("/", tags=["系统"])
async def root():
    """根路径，返回API信息"""
    return {
        "name": "SD Photo Organizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# 开发环境直接运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
