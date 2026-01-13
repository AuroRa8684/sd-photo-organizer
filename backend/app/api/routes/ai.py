"""
AI相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...services import AIService
from ..schemas import ApiResponse, ClassifyRequest


router = APIRouter(prefix="/ai", tags=["AI功能"])


@router.post("/classify", response_model=ApiResponse, summary="AI分类照片")
async def classify_photos(request: ClassifyRequest, db: Session = Depends(get_db)):
    """
    对指定照片进行AI分类
    - 使用多模态大模型识别图片内容
    - 自动分配类别和标签
    - 支持并发处理（4线程）
    """
    try:
        ai_service = AIService(db)
        result = ai_service.classify_photos(
            photo_ids=request.photo_ids,
            max_workers=request.max_workers,
        )
        return ApiResponse(data=result, message=result.get("message", "分类完成"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=ApiResponse, summary="获取可用类别列表")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有可用的照片类别"""
    ai_service = AIService(db)
    categories = ai_service.get_categories()
    return ApiResponse(data=categories, message="获取成功")
