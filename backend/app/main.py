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
import asyncio  # 新增：用于异步执行同步DB初始化
import logging  # 新增：日志模块
import sys      # 新增：日志输出配置
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import get_settings, Settings  # 新增：导入Settings类型
from .db import init_db
from .api.routes import photos_router, ai_router, summary_router, export_router

# 新增：全局日志配置（替换print，生产环境必备）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 获取配置 - 新增：补充类型注解
settings: Settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化数据库，关闭时清理资源
    """
    # 启动时执行
    logger.info("🚀 正在初始化数据库...")  # 修改：替换print为logger
    try:
        # 修改：异步执行同步DB初始化，避免阻塞异步事件循环
        await asyncio.to_thread(init_db)
        logger.info("✅ 数据库初始化完成")  # 修改：替换print为logger
    except Exception as e:
        # 新增：异常捕获，避免DB初始化失败导致应用崩溃
        logger.error(f"❌ 数据库初始化失败: {str(e)}", exc_info=True)
        raise
    
    # 确保缩略图目录存在（仅保留一次创建）
    try:
        settings.thumbs_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 缩略图目录: {settings.thumbs_path}")  # 修改：替换print为logger
    except Exception as e:
        logger.error(f"❌ 缩略图目录创建失败: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # 关闭时执行
    logger.info("👋 应用正在关闭...")  # 修改：替换print为logger


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
    allow_origins=settings.CORS_ORIGINS,  # 修改：从配置读取，替代硬编码
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载静态文件目录（缩略图）
# 前端可通过 /static/thumbs/{sha1}.jpg 访问缩略图
# 修改：移除重复的目录创建代码，路径用as_posix()适配跨系统
app.mount("/static/thumbs", StaticFiles(directory=settings.thumbs_path.as_posix()), name="thumbs")


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