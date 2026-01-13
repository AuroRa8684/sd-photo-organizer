"""
扫描服务模块
负责扫描SD卡目录、解析照片信息
"""
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from ..core.utils import (
    calculate_sha1, 
    generate_thumbnail, 
    parse_exif, 
    find_matching_raw,
    JPG_EXTENSIONS,
)
from ..db.photos_repo import PhotosRepository


class ScannerService:
    """照片扫描服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PhotosRepository(db)
    
    def scan_directory(self, sd_path: str) -> Dict[str, Any]:
        """
        扫描指定目录下的所有照片
        
        Args:
            sd_path: SD卡或照片目录路径
        
        Returns:
            扫描结果统计
        """
        sd_root = Path(sd_path)
        
        if not sd_root.exists():
            raise ValueError(f"目录不存在: {sd_path}")
        
        if not sd_root.is_dir():
            raise ValueError(f"路径不是目录: {sd_path}")
        
        # 查找所有JPG文件
        jpg_files = self._find_all_jpg(sd_root)
        
        if not jpg_files:
            return {
                "total_found": 0,
                "new_imported": 0,
                "duplicates": 0,
                "with_raw": 0,
                "photos": [],
                "message": "未找到任何JPG照片"
            }
        
        # 处理每张照片
        results = {
            "total_found": len(jpg_files),
            "new_imported": 0,
            "duplicates": 0,
            "with_raw": 0,
            "photos": [],
            "errors": [],
        }
        
        for jpg_path in jpg_files:
            try:
                photo_data = self._process_single_photo(jpg_path)
                
                # 保存到数据库
                photo, is_new = self.repo.upsert_by_sha1(photo_data)
                
                if is_new:
                    results["new_imported"] += 1
                    if photo.raw_path:
                        results["with_raw"] += 1
                else:
                    results["duplicates"] += 1
                
                results["photos"].append(photo.to_dict())
                
            except Exception as e:
                results["errors"].append({
                    "file": str(jpg_path),
                    "error": str(e)
                })
        
        results["message"] = f"扫描完成：发现{results['total_found']}张照片，新导入{results['new_imported']}张，重复{results['duplicates']}张"
        
        return results
    
    def _find_all_jpg(self, root: Path) -> List[Path]:
        """
        递归查找目录下所有JPG文件
        """
        jpg_files = []
        
        for ext in JPG_EXTENSIONS:
            jpg_files.extend(root.rglob(f"*{ext}"))
        
        # 去重并排序
        jpg_files = list(set(jpg_files))
        jpg_files.sort()
        
        return jpg_files
    
    def _process_single_photo(self, jpg_path: Path) -> Dict[str, Any]:
        """
        处理单张照片：解析EXIF、计算SHA1、生成缩略图、查找RAW
        """
        # 计算SHA1
        sha1 = calculate_sha1(jpg_path)
        
        # 解析EXIF
        exif_data = parse_exif(jpg_path)
        
        # 生成缩略图
        generate_thumbnail(jpg_path, sha1)
        
        # 查找匹配的RAW文件
        raw_path = find_matching_raw(jpg_path)
        
        # 组装照片数据
        photo_data = {
            "file_name": jpg_path.name,
            "file_path": str(jpg_path),
            "raw_path": str(raw_path) if raw_path else None,
            "sha1": sha1,
            "taken_at": exif_data.get("taken_at"),
            "camera_model": exif_data.get("camera_model"),
            "lens": exif_data.get("lens"),
            "focal_length": exif_data.get("focal_length"),
            "iso": exif_data.get("iso"),
            "aperture": exif_data.get("aperture"),
            "shutter": exif_data.get("shutter"),
            "category": "未分类",
        }
        
        return photo_data
    
    def get_scan_preview(self, sd_path: str) -> Dict[str, Any]:
        """
        快速预览目录（不入库，只统计）
        """
        sd_root = Path(sd_path)
        
        if not sd_root.exists() or not sd_root.is_dir():
            return {"valid": False, "message": "目录无效"}
        
        jpg_files = self._find_all_jpg(sd_root)
        
        raw_count = 0
        for jpg_path in jpg_files:
            if find_matching_raw(jpg_path):
                raw_count += 1
        
        return {
            "valid": True,
            "path": str(sd_root),
            "jpg_count": len(jpg_files),
            "estimated_raw_count": raw_count,
        }
