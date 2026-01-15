"""
导出相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...services import ExportService
from ..schemas import ApiResponse, ExportRequest


router = APIRouter(prefix="/export", tags=["导出功能"])


@router.post("/selected", response_model=ApiResponse, summary="导出精选照片")
async def export_selected(request: ExportRequest, db: Session = Depends(get_db)):
    """
    导出精选照片
    - 可选择是否包含RAW文件
    - 可选择打包为ZIP或直接复制到目录
    """
    try:
        export_service = ExportService(db)
        result = export_service.export_selected(
            export_dir=request.export_dir,
            include_raw=request.include_raw,
            as_zip=request.as_zip,
            photo_ids=request.photo_ids,
        )
        return ApiResponse(data=result, message=result.get("message", "导出完成"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
