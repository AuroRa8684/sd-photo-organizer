"""
配置管理模块
从环境变量/.env文件读取配置
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用配置
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    
    # 数据库配置
    # 使用 sqlite 则自动使用SQLite（开发方便，无需安装MySQL）
    # 使用 mysql 则连接MySQL数据库
    db_type: str = "sqlite"
    
    # MySQL配置（当db_type=mysql时使用）
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "sd_user"
    mysql_password: str = "sd_pass"
    mysql_db: str = "sd_photo"
    
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
            # 使用MySQL
            return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
    
    @property
    def thumbs_path(self) -> Path:
        """获取缩略图存储的绝对路径"""
        backend_dir = Path(__file__).parent.parent.parent
        return backend_dir / self.thumbs_dir
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例（缓存）"""
    return Settings()
