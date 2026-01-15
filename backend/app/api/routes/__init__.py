"""
routes模块初始化
"""
from .photos_router import router as photos_router
from .ai_router import router as ai_router
from .summary_router import router as summary_router
from .export_router import router as export_router

__all__ = [
    "photos_router",
    "ai_router",
    "summary_router",
    "export_router",
]
