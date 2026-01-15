"""
配置管理模块
从环境变量/.env文件读取配置
"""
from typing import List
from pathlib import Path
from pydantic import Field  # 新增：用于配置验证
from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus  # 新增：处理MySQL密码特殊字符


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    
    # 跨域配置（新增：解决main.py CORS报错）
    CORS_ORIGINS: List[str] = Field(default=["http://127.0.0.1:5173"])  # 前端默认地址
    
    # 数据库配置
    # 使用 sqlite 则自动使用SQLite（开发方便，无需安装MySQL）
    # 使用 mysql 则连接MySQL数据库
    db_type: str = Field(default="sqlite", pattern="^(sqlite|mysql)$")  # 核心修改：限制仅允许sqlite/mysql
    
    # MySQL配置（当db_type=mysql时使用）
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "photoapp"  # 原sd_user → 改为photoapp
    mysql_password: str = "photoapp_pwd"  # 原sd_pass → 改为photoapp_pwd
    mysql_db: str = "photoapp"  # 原sd_photo → 改为photoapp
    
    # AI配置
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o"
    
    # 缩略图目录
    thumbs_dir: str = "storage/thumbs"
    
    @property
    def database_url(self) -> str:
        """生成数据库连接字符串"""
        if self.db_type == "sqlite":
            # 使用SQLite（开发方便）
            db_path = Path(__file__).parent.parent.parent / "data" / "photos.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        else:
            # 核心修改：对用户名/密码URL编码，处理特殊字符；新增pool_pre_ping检测连接有效性
            encoded_user = quote_plus(self.mysql_user)
            encoded_pwd = quote_plus(self.mysql_password)
            return (
                f"mysql+pymysql://{encoded_user}:{encoded_pwd}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
                "?charset=utf8mb4&pool_pre_ping=True"
            )
    
    @property
    def thumbs_path(self) -> Path:
        """获取缩略图存储的绝对路径"""
        backend_dir = Path(__file__).parent.parent.parent
        thumbs_path = backend_dir / self.thumbs_dir
        thumbs_path.mkdir(parents=True, exist_ok=True)  # 核心修改：自动创建缩略图目录
        return thumbs_path
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例（缓存）"""
    return Settings()