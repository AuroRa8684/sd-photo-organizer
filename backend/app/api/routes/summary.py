"""
总结相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
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
    - 自动保存到历史记录
    """
    try:
        summary_service = SummaryService(db)
        result = summary_service.generate_summary(
            date_from=request.date_from,
            date_to=request.date_to,
            save_history=request.save_history,
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


@router.get("/history", response_model=ApiResponse, summary="获取历史总结列表")
async def get_history_list(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: Session = Depends(get_db),
):
    """获取历史总结列表"""
    try:
        summary_service = SummaryService(db)
        result = summary_service.get_history_list(limit=limit)
        return ApiResponse(data=result, message=f"获取到 {len(result)} 条历史记录")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{history_id}", response_model=ApiResponse, summary="获取历史总结详情")
async def get_history_detail(history_id: int, db: Session = Depends(get_db)):
    """获取历史总结的完整详情"""
    try:
        summary_service = SummaryService(db)
        result = summary_service.get_history_detail(history_id)
        if not result:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return ApiResponse(data=result, message="获取成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{history_id}", response_model=ApiResponse, summary="删除历史总结")
async def delete_history(history_id: int, db: Session = Depends(get_db)):
    """删除指定的历史总结"""
    try:
        summary_service = SummaryService(db)
        success = summary_service.delete_history(history_id)
        if not success:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        return ApiResponse(data={"deleted": history_id}, message="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
