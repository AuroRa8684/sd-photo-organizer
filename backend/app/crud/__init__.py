# 从photos模块导出核心操作函数
from .photos import (
    upsert_photo,
    list_photos,
    update_photo,
    get_photo_by_sha1
)

# 定义公共导出接口（规范外部导入，避免暴露内部细节）
__all__ = [
    "upsert_photo",
    "list_photos",
    "update_photo",
    "get_photo_by_sha1"
]