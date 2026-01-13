"""
routes模块初始化
"""
from .photos import router as photos_router
from .ai import router as ai_router
from .summary import router as summary_router
from .export import router as export_router

__all__ = [
    "photos_router",
    "ai_router",
    "summary_router",
    "export_router",
]
