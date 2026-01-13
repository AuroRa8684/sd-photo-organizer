"""
通用工具函数模块
包含：SHA1计算、缩略图生成、EXIF解析等
"""
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from PIL import Image
import piexif
from .config import get_settings


# 支持的RAW格式扩展名
RAW_EXTENSIONS = [".arw", ".cr2", ".cr3", ".nef", ".dng", ".raf", ".rw2", ".orf", ".pef"]

# 支持的JPG格式扩展名
JPG_EXTENSIONS = [".jpg", ".jpeg", ".JPG", ".JPEG"]


def calculate_sha1(file_path: Path, chunk_size: int = 65536) -> str:
    """
    分块计算文件SHA1哈希值
    用于去重检测，避免重复导入同一张照片
    
    Args:
        file_path: 文件路径
        chunk_size: 分块大小（默认64KB）
    
    Returns:
        40位SHA1哈希字符串
    """
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha1.update(chunk)
    return sha1.hexdigest()


def generate_thumbnail(jpg_path: Path, sha1: str, width: int = 512) -> Optional[Path]:
    """
    生成缩略图并保存
    
    Args:
        jpg_path: 原始JPG文件路径
        sha1: 文件SHA1（用作缩略图文件名）
        width: 缩略图宽度（默认512px）
    
    Returns:
        缩略图保存路径，失败返回None
    """
    settings = get_settings()
    thumbs_dir = settings.thumbs_path
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    
    thumb_path = thumbs_dir / f"{sha1}.jpg"
    
    # 如果缩略图已存在，直接返回
    if thumb_path.exists():
        return thumb_path
    
    try:
        with Image.open(jpg_path) as img:
            # 保持宽高比缩放
            ratio = width / img.width
            new_height = int(img.height * ratio)
            
            # 使用高质量缩放
            img_resized = img.resize((width, new_height), Image.Resampling.LANCZOS)
            
            # 转换为RGB（处理RGBA等格式）
            if img_resized.mode in ("RGBA", "P"):
                img_resized = img_resized.convert("RGB")
            
            # 保存缩略图
            img_resized.save(thumb_path, "JPEG", quality=85, optimize=True)
            return thumb_path
            
    except Exception as e:
        print(f"生成缩略图失败 {jpg_path}: {e}")
        return None


def parse_exif(jpg_path: Path) -> Dict[str, Any]:
    """
    解析JPG文件的EXIF信息
    
    Args:
        jpg_path: JPG文件路径
    
    Returns:
        包含EXIF信息的字典，缺失字段为None
    """
    result = {
        "taken_at": None,
        "camera_model": None,
        "lens": None,
        "focal_length": None,
        "iso": None,
        "aperture": None,
        "shutter": None,
    }
    
    try:
        exif_dict = piexif.load(str(jpg_path))
        
        # 拍摄时间
        if piexif.ExifIFD.DateTimeOriginal in exif_dict.get("Exif", {}):
            date_str = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
            if isinstance(date_str, bytes):
                date_str = date_str.decode("utf-8")
            try:
                result["taken_at"] = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                pass
        
        # 相机型号
        if piexif.ImageIFD.Model in exif_dict.get("0th", {}):
            model = exif_dict["0th"][piexif.ImageIFD.Model]
            if isinstance(model, bytes):
                model = model.decode("utf-8", errors="ignore")
            result["camera_model"] = model.strip()
        
        # 镜头信息
        if piexif.ExifIFD.LensModel in exif_dict.get("Exif", {}):
            lens = exif_dict["Exif"][piexif.ExifIFD.LensModel]
            if isinstance(lens, bytes):
                lens = lens.decode("utf-8", errors="ignore")
            result["lens"] = lens.strip()
        
        # 焦距
        if piexif.ExifIFD.FocalLength in exif_dict.get("Exif", {}):
            focal = exif_dict["Exif"][piexif.ExifIFD.FocalLength]
            if isinstance(focal, tuple) and len(focal) == 2 and focal[1] != 0:
                result["focal_length"] = focal[0] / focal[1]
        
        # ISO
        if piexif.ExifIFD.ISOSpeedRatings in exif_dict.get("Exif", {}):
            iso = exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings]
            result["iso"] = int(iso) if iso else None
        
        # 光圈值
        if piexif.ExifIFD.FNumber in exif_dict.get("Exif", {}):
            fnumber = exif_dict["Exif"][piexif.ExifIFD.FNumber]
            if isinstance(fnumber, tuple) and len(fnumber) == 2 and fnumber[1] != 0:
                result["aperture"] = fnumber[0] / fnumber[1]
        
        # 快门速度
        if piexif.ExifIFD.ExposureTime in exif_dict.get("Exif", {}):
            exposure = exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
            if isinstance(exposure, tuple) and len(exposure) == 2 and exposure[1] != 0:
                result["shutter"] = exposure[0] / exposure[1]
    
    except Exception as e:
        print(f"解析EXIF失败 {jpg_path}: {e}")
    
    # 如果没有EXIF时间，降级使用文件修改时间
    if result["taken_at"] is None:
        try:
            mtime = jpg_path.stat().st_mtime
            result["taken_at"] = datetime.fromtimestamp(mtime)
        except Exception:
            pass
    
    return result


def find_matching_raw(jpg_path: Path) -> Optional[Path]:
    """
    查找与JPG同名的RAW文件
    
    Args:
        jpg_path: JPG文件路径
    
    Returns:
        RAW文件路径，不存在返回None
    """
    stem = jpg_path.stem  # 不含扩展名的文件名
    parent = jpg_path.parent
    
    for ext in RAW_EXTENSIONS:
        # 尝试大小写变体
        for case_ext in [ext, ext.upper()]:
            raw_path = parent / f"{stem}{case_ext}"
            if raw_path.exists():
                return raw_path
    
    return None


def format_shutter_speed(shutter: Optional[float]) -> str:
    """
    格式化快门速度为可读字符串
    例如: 0.004 -> "1/250", 2.0 -> "2s"
    """
    if shutter is None:
        return "未知"
    
    if shutter >= 1:
        return f"{shutter:.1f}s"
    else:
        denominator = round(1 / shutter)
        return f"1/{denominator}"


def format_aperture(aperture: Optional[float]) -> str:
    """格式化光圈值"""
    if aperture is None:
        return "未知"
    return f"f/{aperture:.1f}"
