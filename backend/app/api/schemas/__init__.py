"""
schemas模块初始化
"""
from .requests import (
    ApiResponse,
    ScanRequest,
    ScanPreviewRequest,
    ImportRequest,
    PhotoUpdateRequest,
    PhotoListQuery,
    ClassifyRequest,
    SummaryRequest,
    ExportRequest,
    BatchDeleteRequest,
    BatchUpdateRequest,
)

__all__ = [
    "ApiResponse",
    "ScanRequest",
    "ScanPreviewRequest",
    "ImportRequest",
    "PhotoUpdateRequest",
    "PhotoListQuery",
    "ClassifyRequest",
    "SummaryRequest",
    "ExportRequest",
    "BatchDeleteRequest",
    "BatchUpdateRequest",
]
