"""
数据库连接模块
使用SQLAlchemy管理MySQL连接
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import get_settings

settings = get_settings()

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 自动检测断开的连接
    pool_recycle=3600,   # 1小时后回收连接
    echo=settings.app_env == "dev",  # 开发环境打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话的依赖注入函数
    用于FastAPI的Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    from . import models  # 确保模型被加载
    Base.metadata.create_all(bind=engine)
