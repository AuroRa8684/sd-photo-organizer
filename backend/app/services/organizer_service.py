"""
整理服务模块
负责将照片按规则复制到本地图库
"""
from pathlib import Path
from shutil import copy2
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.photos_repo import PhotosRepository
from ..db.models import Photo


class OrganizerService:
    """照片整理服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PhotosRepository(db)
    
    def organize_to_library(
        self, 
        library_root: str,
        photo_ids: Optional[List[int]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        将照片整理到本地图库
        目录规则: Library/YYYY-MM-DD/类别/
        
        Args:
            library_root: 图库根目录
            photo_ids: 指定要整理的照片ID列表（可选）
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）
        
        Returns:
            整理结果统计
        """
        library_path = Path(library_root)
        library_path.mkdir(parents=True, exist_ok=True)
        
        # 获取待整理的照片
        if photo_ids:
            photos = [self.repo.get_by_id(pid) for pid in photo_ids]
            photos = [p for p in photos if p is not None]
        else:
            photos, _ = self.repo.list_photos(
                page=1, 
                page_size=10000,  # 一次性获取所有
                date_from=date_from,
                date_to=date_to,
            )
        
        # 只整理尚未整理的照片
        photos_to_organize = [p for p in photos if not p.library_path]
        
        results = {
            "total": len(photos_to_organize),
            "success": 0,
            "failed": 0,
            "jpg_copied": 0,
            "raw_copied": 0,
            "errors": [],
        }
        
        for photo in photos_to_organize:
            try:
                self._organize_single_photo(photo, library_path)
                results["success"] += 1
                results["jpg_copied"] += 1
                if photo.raw_path:
                    results["raw_copied"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "photo_id": photo.id,
                    "file": photo.file_name,
                    "error": str(e)
                })
        
        results["message"] = f"整理完成：成功{results['success']}张，失败{results['failed']}张"
        
        return results
    
    def _organize_single_photo(self, photo: Photo, library_root: Path) -> None:
        """
        整理单张照片到图库
        """
        # 确定日期目录
        if photo.taken_at:
            date_str = photo.taken_at.strftime("%Y-%m-%d")
        else:
            date_str = "未知日期"
        
        # 确定类别目录
        category = photo.category or "未分类"
        
        # 创建目标目录
        dest_dir = library_root / date_str / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制JPG
        src_jpg = Path(photo.file_path)
        if not src_jpg.exists():
            raise FileNotFoundError(f"源文件不存在: {photo.file_path}")
        
        dest_jpg = dest_dir / src_jpg.name
        
        # 处理同名文件冲突
        if dest_jpg.exists():
            dest_jpg = self._get_unique_path(dest_jpg)
        
        copy2(src_jpg, dest_jpg)
        
        # 复制RAW（如果存在）
        if photo.raw_path:
            src_raw = Path(photo.raw_path)
            if src_raw.exists():
                dest_raw = dest_dir / src_raw.name
                if dest_raw.exists():
                    dest_raw = self._get_unique_path(dest_raw)
                copy2(src_raw, dest_raw)
        
        # 更新数据库中的library_path
        self.repo.update_photo(photo.id, {"library_path": str(dest_jpg)})
    
    def _get_unique_path(self, path: Path) -> Path:
        """
        生成唯一文件路径（避免覆盖）
        例如: IMG_001.jpg -> IMG_001_1.jpg
        """
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    def get_library_stats(self, library_root: str) -> Dict[str, Any]:
        """
        获取图库统计信息
        """
        library_path = Path(library_root)
        
        if not library_path.exists():
            return {
                "exists": False,
                "message": "图库目录不存在"
            }
        
        # 统计日期目录和照片数量
        date_dirs = [d for d in library_path.iterdir() if d.is_dir()]
        
        total_photos = 0
        categories = set()
        
        for date_dir in date_dirs:
            for cat_dir in date_dir.iterdir():
                if cat_dir.is_dir():
                    categories.add(cat_dir.name)
                    # 统计JPG文件
                    total_photos += len(list(cat_dir.glob("*.jpg")) + list(cat_dir.glob("*.JPG")))
        
        return {
            "exists": True,
            "path": str(library_path),
            "date_folders": len(date_dirs),
            "categories": list(categories),
            "total_photos": total_photos,
        }
