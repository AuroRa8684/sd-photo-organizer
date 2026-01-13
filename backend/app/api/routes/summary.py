"""
总结相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db import get_db
from ...services import SummaryService
from ..schemas import ApiResponse, SummaryRequest


router = APIRouter(prefix="/summary", tags=["拍摄总结"])


@router.post("/generate", response_model=ApiResponse, summary="生成拍摄总结")
async def generate_summary(request: SummaryRequest, db: Session = Depends(get_db)):
    """
    生成拍摄总结
    - 统计照片数据（类别、焦段、ISO等分布）
    - 调用LLM生成总结文案
    - 返回图表数据供前端展示
    """
    try:
        summary_service = SummaryService(db)
        result = summary_service.generate_summary(
            date_from=request.date_from,
            date_to=request.date_to,
        )
        return ApiResponse(data=result, message=result.get("message", "生成完成"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick-stats", response_model=ApiResponse, summary="获取快速统计")
async def get_quick_stats(db: Session = Depends(get_db)):
    """获取快速统计数据（首页展示用）"""
    try:
        summary_service = SummaryService(db)
        result = summary_service.get_quick_stats()
        return ApiResponse(data=result, message="获取成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
