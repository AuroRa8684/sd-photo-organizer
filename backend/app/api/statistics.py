# app/api/statistics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.statistics import get_photo_total_count, get_photo_count_by_category
from app.db.session import get_db  # 数据库会话依赖

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

# 统一响应模型（可选，用于规范格式）
from pydantic import BaseModel
class SuccessResponse(BaseModel):
    data: dict | list | int

class ErrorResponse(BaseModel):
    error: str

# 1. 照片总数统计接口
@router.get("/photo-total", responses={
    200: {"model": SuccessResponse},
    500: {"model": ErrorResponse}
})
def get_photo_total(user_id: int = None, db: Session = Depends(get_db)):
    try:
        count = get_photo_total_count(db, user_id)
        # 前端会取data，因此返回{"data": 统计结果}
        return {"data": count}
    except Exception as e:
        # 前端会捕获error字段或500状态码，返回error信息
        raise HTTPException(status_code=500, detail=f"统计照片总数失败：{str(e)}")

# 2. 按分类统计照片接口
@router.get("/photo-by-category", responses={
    200: {"model": SuccessResponse},
    500: {"model": ErrorResponse}
})
def get_photo_by_category(user_id: int = None, db: Session = Depends(get_db)):
    try:
        stats = get_photo_count_by_category(db, user_id)
        return {"data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"按分类统计失败：{str(e)}")