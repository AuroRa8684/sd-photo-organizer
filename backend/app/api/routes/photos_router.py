# api/routes/photos_router.py
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.db import get_db_connection
from app.crud.photos import upsert_photo, list_photos, update_photo, get_photo_by_sha1

router = APIRouter(prefix="/photos", tags=["照片管理"])

# 1. 新增/更新照片
@router.post("/upsert", summary="新增/更新照片（按SHA1去重）")
async def api_upsert_photo(
    photo_data: Dict[str, Any] = Body(...),
    conn = Depends(get_db_connection)
):
    try:
        affected_rows = await upsert_photo(conn, photo_data)
        return {
            "success": True,
            "affected_rows": affected_rows,
            "photo_id": photo_data.get("id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"照片插入失败: {str(e)}")

# 2. 分页查询照片
@router.get("/list", summary="分页查询照片列表")
async def api_list_photos(
    start_at: Optional[datetime] = Query(None, description="拍摄开始时间"),
    end_at: Optional[datetime] = Query(None, description="拍摄结束时间"),
    category: Optional[str] = Query(None, description="分类"),
    is_selected: Optional[int] = Query(None, description="是否精选（0/1）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    conn = Depends(get_db_connection)
):
    try:
        result = await list_photos(
            conn, start_at, end_at, category, is_selected, page, page_size
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"照片查询失败: {str(e)}")

# 3. 更新照片字段
@router.patch("/update", summary="更新照片指定字段")
async def api_update_photo(
    photo_id: Optional[int] = Query(None, description="照片ID"),
    sha1: Optional[str] = Query(None, description="照片SHA1"),
    update_data: Dict[str, Any] = Body(...),
    conn = Depends(get_db_connection)
):
    try:
        affected_rows = await update_photo(conn, photo_id, sha1, update_data)
        return {
            "success": True,
            "affected_rows": affected_rows
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"照片更新失败: {str(e)}")

# 4. 按SHA1查询单张照片
@router.get("/{sha1}", summary="按SHA1查询照片详情")
async def api_get_photo(
    sha1: str,
    conn = Depends(get_db_connection)
):
    try:
        photo = await get_photo_by_sha1(conn, sha1)
        if not photo:
            raise HTTPException(status_code=404, detail="照片不存在")
        return {"success": True, "data": photo}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询照片失败: {str(e)}")