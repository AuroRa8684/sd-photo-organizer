"""
导出服务模块
负责导出精选照片，支持ZIP打包
"""
import zipfile
from pathlib import Path
from shutil import copy2
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ..db.photos_repo import PhotosRepository
from ..core.config import get_settings


class ExportService:
    """照片导出服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PhotosRepository(db)
    
    def export_selected(
        self,
        export_dir: str,
        include_raw: bool = True,
        as_zip: bool = False,
        photo_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        导出精选照片
        
        Args:
            export_dir: 导出目录
            include_raw: 是否包含RAW文件
            as_zip: 是否打包为ZIP
            photo_ids: 指定导出的照片ID（可选，默认导出所有精选）
        
        Returns:
            导出结果统计
        """
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # 获取要导出的照片
        if photo_ids:
            photos = [self.repo.get_by_id(pid) for pid in photo_ids]
            photos = [p for p in photos if p is not None]
        else:
            photos = self.repo.get_selected_photos()
        
        if not photos:
            return {
                "success": False,
                "message": "没有可导出的照片",
                "exported_count": 0,
            }
        
        results = {
            "success": True,
            "exported_count": 0,
            "jpg_count": 0,
            "raw_count": 0,
            "errors": [],
            "export_path": str(export_path),
        }
        
        # 准备导出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if as_zip:
            # 导出到ZIP文件
            zip_name = f"photos_export_{timestamp}.zip"
            zip_path = export_path / zip_name
            results["zip_path"] = str(zip_path)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for photo in photos:
                    try:
                        self._add_photo_to_zip(zf, photo, include_raw)
                        results["exported_count"] += 1
                        results["jpg_count"] += 1
                        if include_raw and photo.raw_path:
                            results["raw_count"] += 1
                    except Exception as e:
                        results["errors"].append({
                            "photo_id": photo.id,
                            "error": str(e)
                        })
        else:
            # 直接复制到目录
            dest_dir = export_path / f"export_{timestamp}"
            dest_dir.mkdir(parents=True, exist_ok=True)
            results["export_path"] = str(dest_dir)
            
            for photo in photos:
                try:
                    self._copy_photo_to_dir(photo, dest_dir, include_raw)
                    results["exported_count"] += 1
                    results["jpg_count"] += 1
                    if include_raw and photo.raw_path:
                        results["raw_count"] += 1
                except Exception as e:
                    results["errors"].append({
                        "photo_id": photo.id,
                        "error": str(e)
                    })
        
        results["message"] = f"导出完成：{results['exported_count']}张JPG，{results['raw_count']}张RAW"
        
        return results
    
    def _copy_photo_to_dir(self, photo, dest_dir: Path, include_raw: bool) -> None:
        """复制照片到目标目录"""
        # 确定源文件路径（优先使用library_path）
        if photo.library_path and Path(photo.library_path).exists():
            src_jpg = Path(photo.library_path)
        else:
            src_jpg = Path(photo.file_path)
        
        if not src_jpg.exists():
            raise FileNotFoundError(f"源文件不存在: {src_jpg}")
        
        # 复制JPG
        dest_jpg = dest_dir / src_jpg.name
        if dest_jpg.exists():
            dest_jpg = self._get_unique_path(dest_jpg)
        copy2(src_jpg, dest_jpg)
        
        # 复制RAW
        if include_raw and photo.raw_path:
            src_raw = Path(photo.raw_path)
            if src_raw.exists():
                dest_raw = dest_dir / src_raw.name
                if dest_raw.exists():
                    dest_raw = self._get_unique_path(dest_raw)
                copy2(src_raw, dest_raw)
    
    def _add_photo_to_zip(self, zf: zipfile.ZipFile, photo, include_raw: bool) -> None:
        """将照片添加到ZIP文件"""
        # 确定源文件路径
        if photo.library_path and Path(photo.library_path).exists():
            src_jpg = Path(photo.library_path)
        else:
            src_jpg = Path(photo.file_path)
        
        if not src_jpg.exists():
            raise FileNotFoundError(f"源文件不存在: {src_jpg}")
        
        # 添加JPG到ZIP
        zf.write(src_jpg, src_jpg.name)
        
        # 添加RAW到ZIP
        if include_raw and photo.raw_path:
            src_raw = Path(photo.raw_path)
            if src_raw.exists():
                zf.write(src_raw, src_raw.name)
    
    def _get_unique_path(self, path: Path) -> Path:
        """生成唯一文件路径"""
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
