"""
照片数据库操作模块
实现CRUD操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from .models import Photo


class PhotosRepository:
    """照片数据仓库，封装所有数据库操作"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def upsert_by_sha1(self, photo_data: Dict[str, Any]) -> tuple[Photo, bool]:
        """
        按SHA1去重插入照片
        如果已存在则跳过（返回已存在记录）
        
        Args:
            photo_data: 照片数据字典
        
        Returns:
            (Photo对象, 是否新插入)
        """
        sha1 = photo_data.get("sha1")
        existing = self.db.query(Photo).filter(Photo.sha1 == sha1).first()
        
        if existing:
            return existing, False
        
        # 创建新记录
        photo = Photo(
            file_name=photo_data.get("file_name"),
            file_path=photo_data.get("file_path"),
            raw_path=photo_data.get("raw_path"),
            taken_at=photo_data.get("taken_at"),
            camera_model=photo_data.get("camera_model"),
            lens=photo_data.get("lens"),
            focal_length=photo_data.get("focal_length"),
            iso=photo_data.get("iso"),
            aperture=photo_data.get("aperture"),
            shutter=photo_data.get("shutter"),
            category=photo_data.get("category", "未分类"),
            tags_json=photo_data.get("tags"),
            sha1=sha1,
        )
        self.db.add(photo)
        # 注意：不在这里commit，由调用方统一提交（支持批量操作）
        return photo, True
    
    def batch_insert_photos(self, photos_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        批量插入照片（优化性能）
        
        Args:
            photos_data: 照片数据列表
        
        Returns:
            {"new": 新插入数量, "duplicates": 重复数量}
        """
        new_count = 0
        dup_count = 0
        
        # 获取所有已存在的SHA1
        sha1_list = [p.get("sha1") for p in photos_data if p.get("sha1")]
        existing_sha1s = set(
            row[0] for row in 
            self.db.query(Photo.sha1).filter(Photo.sha1.in_(sha1_list)).all()
        )
        
        # 批量创建新记录
        new_photos = []
        for photo_data in photos_data:
            sha1 = photo_data.get("sha1")
            if sha1 in existing_sha1s:
                dup_count += 1
                continue
            
            photo = Photo(
                file_name=photo_data.get("file_name"),
                file_path=photo_data.get("file_path"),
                raw_path=photo_data.get("raw_path"),
                taken_at=photo_data.get("taken_at"),
                camera_model=photo_data.get("camera_model"),
                lens=photo_data.get("lens"),
                focal_length=photo_data.get("focal_length"),
                iso=photo_data.get("iso"),
                aperture=photo_data.get("aperture"),
                shutter=photo_data.get("shutter"),
                category=photo_data.get("category", "未分类"),
                tags_json=photo_data.get("tags"),
                sha1=sha1,
            )
            new_photos.append(photo)
            existing_sha1s.add(sha1)  # 防止同批次重复
            new_count += 1
        
        # 批量插入
        if new_photos:
            self.db.add_all(new_photos)
            self.db.commit()
        
        return {"new": new_count, "duplicates": dup_count}
    
    def list_photos(
        self,
        page: int = 1,
        page_size: int = 50,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        category: Optional[str] = None,
        is_selected: Optional[bool] = None,
        focal_min: Optional[float] = None,
        focal_max: Optional[float] = None,
        iso_min: Optional[int] = None,
        iso_max: Optional[int] = None,
    ) -> tuple[List[Photo], int]:
        """
        分页查询照片列表
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            date_from: 开始日期
            date_to: 结束日期
            category: 类别筛选
            is_selected: 精选筛选
            focal_min/focal_max: 焦距范围
            iso_min/iso_max: ISO范围
        
        Returns:
            (照片列表, 总数)
        """
        query = self.db.query(Photo)
        
        # 构建筛选条件
        conditions = []
        
        if date_from:
            conditions.append(Photo.taken_at >= date_from)
        if date_to:
            conditions.append(Photo.taken_at <= date_to)
        if category and category != "全部":
            conditions.append(Photo.category == category)
        if is_selected is not None:
            conditions.append(Photo.is_selected == (1 if is_selected else 0))
        if focal_min is not None:
            conditions.append(Photo.focal_length >= focal_min)
        if focal_max is not None:
            conditions.append(Photo.focal_length <= focal_max)
        if iso_min is not None:
            conditions.append(Photo.iso >= iso_min)
        if iso_max is not None:
            conditions.append(Photo.iso <= iso_max)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 统计总数
        total = query.count()
        
        # 分页查询，按拍摄时间倒序
        photos = query.order_by(Photo.taken_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        
        return photos, total
    
    def get_by_id(self, photo_id: int) -> Optional[Photo]:
        """根据ID获取照片"""
        return self.db.query(Photo).filter(Photo.id == photo_id).first()
    
    def get_by_sha1(self, sha1: str) -> Optional[Photo]:
        """根据SHA1获取照片"""
        return self.db.query(Photo).filter(Photo.sha1 == sha1).first()
    
    def update_photo(self, photo_id: int, updates: Dict[str, Any]) -> Optional[Photo]:
        """
        更新照片信息
        
        Args:
            photo_id: 照片ID
            updates: 要更新的字段字典
        
        Returns:
            更新后的照片对象
        """
        photo = self.get_by_id(photo_id)
        if not photo:
            return None
        
        # 允许更新的字段
        allowed_fields = [
            "category", "tags_json", "caption", "is_selected", 
            "library_path", "raw_path"
        ]
        
        for field, value in updates.items():
            if field in allowed_fields:
                # 特殊处理tags字段
                if field == "tags":
                    setattr(photo, "tags_json", value)
                else:
                    setattr(photo, field, value)
        
        self.db.commit()
        self.db.refresh(photo)
        return photo
    
    def batch_update_category(self, photo_ids: List[int], category: str, tags: List[str] = None, caption: str = None) -> int:
        """
        批量更新照片分类
        
        Returns:
            更新的照片数量
        """
        updates = {"category": category}
        if tags is not None:
            updates["tags_json"] = tags
        if caption is not None:
            updates["caption"] = caption
            
        result = self.db.query(Photo).filter(Photo.id.in_(photo_ids)).update(
            updates, synchronize_session=False
        )
        self.db.commit()
        return result
    
    def get_selected_photos(self) -> List[Photo]:
        """获取所有精选照片"""
        return self.db.query(Photo).filter(Photo.is_selected == 1).all()
    
    def get_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        获取统计数据（优化版：使用SQL聚合）
        用于生成拍摄总结
        """
        # 构建基础查询条件
        conditions = []
        if date_from:
            conditions.append(Photo.taken_at >= date_from)
        if date_to:
            conditions.append(Photo.taken_at <= date_to)
        
        base_filter = and_(*conditions) if conditions else True
        
        # 1. 基础统计（单次查询）
        basic_stats = self.db.query(
            func.count(Photo.id).label("total"),
            func.sum(case((Photo.raw_path.isnot(None), 1), else_=0)).label("with_raw"),
            func.sum(Photo.is_selected).label("selected"),
        ).filter(base_filter).first()
        
        if not basic_stats or basic_stats.total == 0:
            return {"total": 0}
        
        stats = {
            "total": basic_stats.total or 0,
            "with_raw": int(basic_stats.with_raw or 0),
            "selected": int(basic_stats.selected or 0),
            "categories": {},
            "focal_lengths": {},
            "isos": {},
            "apertures": {},
            "cameras": {},
        }
        
        # 2. 类别统计（SQL GROUP BY）
        category_stats = self.db.query(
            Photo.category, func.count(Photo.id)
        ).filter(base_filter).group_by(Photo.category).all()
        
        for cat, count in category_stats:
            stats["categories"][cat or "未分类"] = count
        
        # 3. 相机统计
        camera_stats = self.db.query(
            Photo.camera_model, func.count(Photo.id)
        ).filter(base_filter).filter(Photo.camera_model.isnot(None)).group_by(Photo.camera_model).all()
        
        for cam, count in camera_stats:
            if cam:
                stats["cameras"][cam] = count
        
        # 4. 焦距/ISO/光圈 分段统计（需要在应用层处理分段逻辑）
        # 只查询有值的记录，减少数据传输
        photo_params = self.db.query(
            Photo.focal_length, Photo.iso, Photo.aperture
        ).filter(base_filter).filter(
            or_(Photo.focal_length.isnot(None), Photo.iso.isnot(None), Photo.aperture.isnot(None))
        ).all()
        
        for focal, iso, aperture in photo_params:
            if focal:
                focal_range = self._get_focal_range(focal)
                stats["focal_lengths"][focal_range] = stats["focal_lengths"].get(focal_range, 0) + 1
            if iso:
                iso_range = self._get_iso_range(iso)
                stats["isos"][iso_range] = stats["isos"].get(iso_range, 0) + 1
            if aperture:
                ap_range = self._get_aperture_range(aperture)
                stats["apertures"][ap_range] = stats["apertures"].get(ap_range, 0) + 1
        
        return stats
    
    def _get_focal_range(self, focal: float) -> str:
        """焦距分段"""
        if focal < 24:
            return "超广角(<24mm)"
        elif focal < 35:
            return "广角(24-35mm)"
        elif focal < 50:
            return "标准(35-50mm)"
        elif focal < 85:
            return "中焦(50-85mm)"
        elif focal < 135:
            return "中长焦(85-135mm)"
        else:
            return "长焦(>135mm)"
    
    def _get_iso_range(self, iso: int) -> str:
        """ISO分段"""
        if iso <= 200:
            return "低ISO(≤200)"
        elif iso <= 800:
            return "中ISO(201-800)"
        elif iso <= 3200:
            return "高ISO(801-3200)"
        else:
            return "超高ISO(>3200)"
    
    def _get_aperture_range(self, aperture: float) -> str:
        """光圈分段"""
        if aperture <= 2.8:
            return "大光圈(≤f/2.8)"
        elif aperture <= 5.6:
            return "中光圈(f/2.8-5.6)"
        else:
            return "小光圈(>f/5.6)"
    
    def batch_delete_photos(self, photo_ids: List[int]) -> Dict[str, Any]:
        """
        批量删除照片记录（不删除文件）
        
        Args:
            photo_ids: 要删除的照片ID列表
        
        Returns:
            {"deleted": 删除数量}
        """
        # 先获取要删除的照片SHA1（用于删除缩略图）
        photos_to_delete = self.db.query(Photo.sha1).filter(Photo.id.in_(photo_ids)).all()
        sha1_list = [p.sha1 for p in photos_to_delete]
        
        # 删除数据库记录
        deleted_count = self.db.query(Photo).filter(Photo.id.in_(photo_ids)).delete(
            synchronize_session=False
        )
        self.db.commit()
        
        return {"deleted": deleted_count, "sha1_list": sha1_list}
    
    def batch_update_photos(self, photo_ids: List[int], updates: Dict[str, Any]) -> int:
        """
        批量更新照片信息
        
        Args:
            photo_ids: 照片ID列表
            updates: 要更新的字段
        
        Returns:
            更新的数量
        """
        if not updates:
            return 0
        
        result = self.db.query(Photo).filter(Photo.id.in_(photo_ids)).update(
            updates, synchronize_session=False
        )
        self.db.commit()
        return result
    
    def get_photos_by_ids(self, photo_ids: List[int]) -> List[Photo]:
        """根据ID列表获取照片"""
        return self.db.query(Photo).filter(Photo.id.in_(photo_ids)).all()
