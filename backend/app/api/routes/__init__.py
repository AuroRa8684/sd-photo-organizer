"""
routes模块初始化
"""
from .photos import router as photos_router
from .ai_router import router as ai_router
from .summary_router import router as summary_router
from .export_router import router as export_router

__all__ = [
    "photos",
    "ai",
    "summary",
    "export",
]
