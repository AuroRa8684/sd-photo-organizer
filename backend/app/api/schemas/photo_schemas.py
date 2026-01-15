"""
Pydantic 模型：照片相关入参/出参校验
"""
from pydantic import BaseModel
from typing import Optional, List

class PhotoUpdateRequest(BaseModel):
    """照片更新入参模型（仅允许更新以下字段）"""
    # 分类（固定类别体系：人像/风光/街拍等，前端下拉选择）
    category: Optional[str] = None
    # 标签（数组格式，如 ["海边","日落"]，关键修改：tags_json → tags）
    tags: Optional[List[str]] = None
    # 精选状态（0=未精选，1=精选）
    is_selected: Optional[int] = None
    # 整理后在 Library 的路径（由后端整理服务更新）
    library_path: Optional[str] = None

# 关键修改：删除冗余的 orm_mode 配置