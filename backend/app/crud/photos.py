# crud/photos.py
import logging
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ====================== 核心操作 ======================
async def upsert_photo(conn, photo_data: Dict[str, Any]) -> int:
    """
    按sha1去重插入/更新照片数据
    :param conn: asyncmy.Connection 实例
    :param photo_data: 照片数据字典（需包含sha1，其他字段见表结构）
    :return: 影响的行数（1=插入/更新成功，0=无变化）
    """
    # 字段映射（确保与表结构一致）
    fields = [
        "file_name", "file_path", "raw_path", "library_path", "taken_at",
        "camera_model", "lens", "focal_length", "iso", "aperture", "shutter",
        "category", "tags_json", "is_selected", "sha1"
    ]
    
    # 处理JSON字段
    if "tags_json" in photo_data and isinstance(photo_data["tags_json"], list):
        photo_data["tags_json"] = json.dumps(photo_data["tags_json"], ensure_ascii=False)
    
    # 处理时间字段
    if "taken_at" in photo_data and isinstance(photo_data["taken_at"], datetime):
        photo_data["taken_at"] = photo_data["taken_at"].strftime("%Y-%m-%d %H:%M:%S")

    # 构建INSERT ... ON DUPLICATE KEY UPDATE语句
    placeholders = ", ".join([f"%({f})s" for f in fields])
    update_fields = ", ".join([f"{f}=VALUES({f})" for f in ["file_path", "raw_path", "library_path"]])  # 仅更新指定字段
    
    sql = f"""
    INSERT INTO photos ({', '.join(fields)})
    VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE {update_fields}
    """
    
    try:
        async with conn.cursor() as cur:
            await cur.execute(sql, photo_data)
            affected_rows = cur.rowcount
            # 获取自增ID（插入时）
            if affected_rows > 0 and cur.lastrowid:
                photo_data["id"] = cur.lastrowid
            logger.info(f"📸 照片[{photo_data['sha1']}] upsert完成，影响行数: {affected_rows}")
            return affected_rows
    except Exception as e:
        logger.error(f"❌ 照片upsert失败: {str(e)} | 数据: {photo_data}", exc_info=True)
        raise

async def list_photos(
    conn,
    start_at: Optional[datetime] = None,
    end_at: Optional[datetime] = None,
    category: Optional[str] = None,
    is_selected: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """
    按条件查询照片列表（支持分页、过滤）
    :return: {"total": 总数, "items": 照片列表}
    """
    # 基础查询
    where_conditions = []
    params = {}
    
    # 时间范围过滤
    if start_at:
        where_conditions.append("taken_at >= %(start_at)s")
        params["start_at"] = start_at.strftime("%Y-%m-%d %H:%M:%S")
    if end_at:
        where_conditions.append("taken_at <= %(end_at)s")
        params["end_at"] = end_at.strftime("%Y-%m-%d %H:%M:%S")
    
    # 类别过滤
    if category:
        where_conditions.append("category = %(category)s")
        params["category"] = category
    
    # 精选状态过滤
    if is_selected is not None:
        where_conditions.append("is_selected = %(is_selected)s")
        params["is_selected"] = is_selected
    
    # 构建WHERE子句
    where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
    
    # 1. 查询总数
    count_sql = f"SELECT COUNT(*) as total FROM photos {where_clause}"
    async with conn.cursor() as cur:
        await cur.execute(count_sql, params)
        total = (await cur.fetchone())["total"]
    
    # 2. 查询分页数据
    offset = (page - 1) * page_size
    list_sql = f"""
    SELECT * FROM photos {where_clause}
    ORDER BY taken_at DESC, id DESC
    LIMIT %(page_size)s OFFSET %(offset)s
    """
    params["page_size"] = page_size
    params["offset"] = offset
    
    async with conn.cursor() as cur:
        await cur.execute(list_sql, params)
        rows = await cur.fetchall()
        
        # 格式化结果（JSON字段转列表，时间字段转字符串）
        items = []
        for row in rows:
            item = dict(row)
            if item.get("tags_json"):
                item["tags_json"] = json.loads(item["tags_json"])
            if item.get("taken_at"):
                item["taken_at"] = item["taken_at"].strftime("%Y-%m-%d %H:%M:%S")
            items.append(item)
    
    logger.info(f"📋 照片查询完成: 总数={total}, 分页={page}/{(total + page_size -1)//page_size}")
    return {"total": total, "items": items}

async def update_photo(
    conn,
    photo_id: Optional[int] = None,
    sha1: Optional[str] = None,
    update_data: Dict[str, Any]
) -> int:
    """
    更新照片指定字段
    :param conn: asyncmy.Connection 实例
    :param photo_id: 照片ID（二选一）
    :param sha1: 照片SHA1（二选一）
    :param update_data: 要更新的字段（category/tags_json/is_selected/library_path等）
    :return: 影响的行数
    """
    if not photo_id and not sha1:
        raise ValueError("必须指定photo_id或sha1")
    
    # 处理JSON字段
    if "tags_json" in update_data and isinstance(update_data["tags_json"], list):
        update_data["tags_json"] = json.dumps(update_data["tags_json"], ensure_ascii=False)
    
    # 构建更新语句
    set_clause = ", ".join([f"{k}=%({k})s" for k in update_data.keys()])
    where_clause = "id=%(photo_id)s" if photo_id else "sha1=%(sha1)s"
    
    sql = f"""
    UPDATE photos
    SET {set_clause}, updated_at=CURRENT_TIMESTAMP
    WHERE {where_clause}
    """
    
    # 合并参数
    params = update_data.copy()
    if photo_id:
        params["photo_id"] = photo_id
    if sha1:
        params["sha1"] = sha1
    
    try:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            affected_rows = cur.rowcount
            logger.info(f"✏️ 照片[{photo_id or sha1}]更新完成，影响行数: {affected_rows}")
            return affected_rows
    except Exception as e:
        logger.error(f"❌ 照片更新失败: {str(e)} | 参数: {params}", exc_info=True)
        raise

# ====================== 辅助操作（可选） ======================
async def get_photo_by_sha1(conn, sha1: str) -> Optional[Dict[str, Any]]:
    """按SHA1查询单张照片"""
    sql = "SELECT * FROM photos WHERE sha1=%(sha1)s LIMIT 1"
    async with conn.cursor() as cur:
        await cur.execute(sql, {"sha1": sha1})
        row = await cur.fetchone()
        if row:
            item = dict(row)
            if item.get("tags_json"):
                item["tags_json"] = json.loads(item["tags_json"])
            return item
    return None