"""
Pydantic 请求/响应模型
用于API参数校验和文档生成
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ========== 通用响应 ==========

class ApiResponse(BaseModel):
    """通用API响应格式"""
    data: Any = None
    message: str = ""
    error: Optional[str] = None


# ========== 照片相关 ==========

class ScanRequest(BaseModel):
    """扫描请求"""
    sd_path: str = Field(..., description="SD卡或照片目录路径")


class ScanPreviewRequest(BaseModel):
    """扫描预览请求"""
    sd_path: str = Field(..., description="要预览的目录路径")


class ImportRequest(BaseModel):
    """整理导入请求"""
    library_root: str = Field(..., description="本地图库根目录")
    photo_ids: Optional[List[int]] = Field(None, description="指定照片ID列表（可选）")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")


class PhotoUpdateRequest(BaseModel):
    """照片更新请求"""
    category: Optional[str] = Field(None, description="类别")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    caption: Optional[str] = Field(None, description="描述")
    is_selected: Optional[bool] = Field(None, description="是否精选")


class PhotoListQuery(BaseModel):
    """照片列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(50, ge=1, le=200, description="每页数量")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")
    category: Optional[str] = Field(None, description="类别筛选")
    is_selected: Optional[bool] = Field(None, description="精选筛选")
    focal_min: Optional[float] = Field(None, description="最小焦距")
    focal_max: Optional[float] = Field(None, description="最大焦距")
    iso_min: Optional[int] = Field(None, description="最小ISO")
    iso_max: Optional[int] = Field(None, description="最大ISO")


# ========== AI相关 ==========

class ClassifyRequest(BaseModel):
    """AI分类请求"""
    photo_ids: List[int] = Field(..., description="要分类的照片ID列表")
    max_workers: int = Field(4, ge=1, le=8, description="并发线程数")


# ========== 总结相关 ==========

class SummaryRequest(BaseModel):
    """生成总结请求"""
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")


# ========== 导出相关 ==========

class ExportRequest(BaseModel):
    """导出请求"""
    export_dir: str = Field(..., description="导出目录")
    include_raw: bool = Field(True, description="是否包含RAW文件")
    as_zip: bool = Field(False, description="是否打包为ZIP")
    photo_ids: Optional[List[int]] = Field(None, description="指定导出的照片ID（可选）")
