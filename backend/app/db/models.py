"""
数据库ORM模型
定义photos表对应的Python类
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer, Float, JSON, Index
from .session import Base


class Photo(Base):
    """
    照片模型
    对应数据库中的photos表
    """
    __tablename__ = "photos"
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 文件信息
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(Text, nullable=False, comment="原始JPG路径（SD卡中）")
    raw_path = Column(Text, nullable=True, comment="匹配的RAW文件路径")
    library_path = Column(Text, nullable=True, comment="整理后在Library的JPG路径")
    
    # EXIF信息
    taken_at = Column(DateTime, nullable=True, comment="拍摄时间")
    camera_model = Column(String(255), nullable=True, comment="相机型号")
    lens = Column(String(255), nullable=True, comment="镜头型号")
    focal_length = Column(Float, nullable=True, comment="焦距(mm)")
    iso = Column(Integer, nullable=True, comment="ISO感光度")
    aperture = Column(Float, nullable=True, comment="光圈值")
    shutter = Column(Float, nullable=True, comment="快门速度(秒)")
    
    # AI分类
    category = Column(String(50), nullable=False, default="未分类", comment="照片类别")
    tags_json = Column(JSON, nullable=True, comment="标签数组")
    caption = Column(String(255), nullable=True, comment="AI生成的描述")
    
    # 精选标记
    is_selected = Column(Integer, nullable=False, default=0, comment="是否精选 0/1")
    
    # 去重
    sha1 = Column(String(40), nullable=False, unique=True, comment="JPG内容SHA1哈希")
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 索引
    __table_args__ = (
        Index("idx_photos_taken_at", "taken_at"),
        Index("idx_photos_category", "category"),
        Index("idx_photos_selected", "is_selected"),
    )
    
    def to_dict(self) -> dict:
        """转换为字典，用于API返回"""
        return {
            "id": self.id,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "raw_path": self.raw_path,
            "library_path": self.library_path,
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "camera_model": self.camera_model,
            "lens": self.lens,
            "focal_length": self.focal_length,
            "iso": self.iso,
            "aperture": self.aperture,
            "shutter": self.shutter,
            "category": self.category,
            "tags": self.tags_json or [],
            "caption": self.caption,
            "is_selected": bool(self.is_selected),
            "sha1": self.sha1,
            "thumb_url": f"/static/thumbs/{self.sha1}.jpg",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
