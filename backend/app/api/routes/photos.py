"""
照片相关API路由
包含：扫描、导入、查询、更新
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db import get_db, PhotosRepository
from ...services import ScannerService, OrganizerService
from ..schemas import (
    ApiResponse,
    ScanRequest,
    ScanPreviewRequest,
    ImportRequest,
    PhotoUpdateRequest,
)


router = APIRouter(prefix="/photos", tags=["照片管理"])


@router.post("/scan", response_model=ApiResponse, summary="扫描SD卡目录")
async def scan_directory(request: ScanRequest, db: Session = Depends(get_db)):
    """
    扫描指定目录下的所有照片
    - 解析EXIF信息
    - 生成缩略图
    - 匹配RAW文件
    - 入库（SHA1去重）
    """
    try:
        scanner = ScannerService(db)
        result = scanner.scan_directory(request.sd_path)
        return ApiResponse(data=result, message=result.get("message", "扫描完成"))
    except ValueError as e:
        return ApiResponse(data=None, message=str(e), error=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/preview", response_model=ApiResponse, summary="预览目录（不入库）")
async def scan_preview(request: ScanPreviewRequest, db: Session = Depends(get_db)):
    """
    快速预览目录，返回照片数量统计（不入库）
    """
    try:
        scanner = ScannerService(db)
        result = scanner.get_scan_preview(request.sd_path)
        return ApiResponse(data=result, message="预览完成")
    except Exception as e:
        return ApiResponse(data=None, message=str(e), error=str(e))


@router.post("/import", response_model=ApiResponse, summary="整理到本地图库")
async def import_to_library(request: ImportRequest, db: Session = Depends(get_db)):
    """
    将照片整理到本地图库
    - 按 YYYY-MM-DD/类别/ 规则创建目录
    - 复制JPG和RAW文件
    - 更新数据库中的library_path
    """
    try:
        organizer = OrganizerService(db)
        result = organizer.organize_to_library(
            library_root=request.library_root,
            photo_ids=request.photo_ids,
            date_from=request.date_from,
            date_to=request.date_to,
        )
        return ApiResponse(data=result, message=result.get("message", "整理完成"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ApiResponse, summary="查询照片列表")
async def list_photos(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    date_from: Optional[datetime] = Query(None, description="开始日期"),
    date_to: Optional[datetime] = Query(None, description="结束日期"),
    category: Optional[str] = Query(None, description="类别筛选"),
    is_selected: Optional[bool] = Query(None, description="精选筛选"),
    focal_min: Optional[float] = Query(None, description="最小焦距"),
    focal_max: Optional[float] = Query(None, description="最大焦距"),
    iso_min: Optional[int] = Query(None, description="最小ISO"),
    iso_max: Optional[int] = Query(None, description="最大ISO"),
    db: Session = Depends(get_db),
):
    """
    分页查询照片列表，支持多种筛选条件
    """
    try:
        repo = PhotosRepository(db)
        photos, total = repo.list_photos(
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            category=category,
            is_selected=is_selected,
            focal_min=focal_min,
            focal_max=focal_max,
            iso_min=iso_min,
            iso_max=iso_max,
        )
        
        return ApiResponse(
            data={
                "photos": [p.to_dict() for p in photos],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
            message=f"查询到 {total} 张照片"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{photo_id}", response_model=ApiResponse, summary="获取单张照片详情")
async def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """获取单张照片的详细信息"""
    repo = PhotosRepository(db)
    photo = repo.get_by_id(photo_id)
    
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")
    
    return ApiResponse(data=photo.to_dict(), message="获取成功")


@router.patch("/{photo_id}", response_model=ApiResponse, summary="更新照片信息")
async def update_photo(
    photo_id: int,
    request: PhotoUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    更新照片信息
    - 可更新：类别、标签、描述、精选状态
    """
    repo = PhotosRepository(db)
    
    updates = {}
    if request.category is not None:
        updates["category"] = request.category
    if request.tags is not None:
        updates["tags_json"] = request.tags
    if request.caption is not None:
        updates["caption"] = request.caption
    if request.is_selected is not None:
        updates["is_selected"] = 1 if request.is_selected else 0
    
    if not updates:
        return ApiResponse(data=None, message="没有要更新的字段")
    
    photo = repo.update_photo(photo_id, updates)
    
    if not photo:
        raise HTTPException(status_code=404, detail="照片不存在")
    
    return ApiResponse(data=photo.to_dict(), message="更新成功")


@router.get("/categories/list", response_model=ApiResponse, summary="获取所有类别")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有可用的照片类别"""
    from ...services.ai_service import CATEGORIES
    return ApiResponse(data=CATEGORIES, message="获取成功")
