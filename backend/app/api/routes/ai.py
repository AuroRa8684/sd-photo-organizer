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
    - 可选跳过已分类照片
    """
    try:
        if not request.photo_ids:
            return ApiResponse(data=None, message="请先选择要分类的照片", error="未选择照片")
        
        ai_service = AIService(db)
        result = ai_service.classify_photos(
            photo_ids=request.photo_ids,
            max_workers=request.max_workers,
            skip_classified=request.skip_classified,
        )
        return ApiResponse(data=result, message=result.get("message", "分类完成"))
    except Exception as e:
        error_msg = str(e)
        if "API" in error_msg or "key" in error_msg.lower():
            return ApiResponse(data=None, message="AI服务配置错误，请检查API密钥", error=error_msg)
        elif "timeout" in error_msg.lower():
            return ApiResponse(data=None, message="AI服务响应超时，请稍后重试", error=error_msg)
        else:
            raise HTTPException(status_code=500, detail=f"AI分类失败：{error_msg}")


@router.get("/categories", response_model=ApiResponse, summary="获取可用类别列表")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有可用的照片类别"""
    ai_service = AIService(db)
    categories = ai_service.get_categories()
    return ApiResponse(data=categories, message="获取成功")
