"""
AI服务模块
负责调用多模态大模型进行图片分类和标签生成
"""
import base64
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db.photos_repo import PhotosRepository


# 固定类别列表
CATEGORIES = ["人像", "风光", "街拍", "建筑", "美食", "夜景", "动物", "活动", "微距", "未分类"]

# 分类Prompt模板 - 简化版，兼容性更好
CLASSIFY_PROMPT = """Analyze this image. Return JSON with these fields:
- category: Choose from [人像, 风光, 街拍, 建筑, 美食, 夜景, 动物, 活动, 微距, 未分类]
- tags: 3-6 Chinese keywords describing the image
- caption: A brief Chinese description (max 25 chars)
- confidence: 0-1 score

Example: {"category":"风光","tags":["海边","日落"],"caption":"海边日落","confidence":0.8}
Return ONLY JSON, no other text."""


class AIService:
    """AI分类服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PhotosRepository(db)
        self.settings = get_settings()
    
    def classify_photos(
        self,
        photo_ids: List[int],
        max_workers: int = 4,
        skip_classified: bool = False,
    ) -> Dict[str, Any]:
        """
        批量对照片进行AI分类
        
        Args:
            photo_ids: 照片ID列表
            max_workers: 并发线程数
            skip_classified: 是否跳过已分类照片
        
        Returns:
            分类结果统计
        """
        if not self.settings.ai_api_key or self.settings.ai_api_key == "your_api_key_here":
            return {
                "success": False,
                "message": "AI API Key未配置，请在.env文件中设置AI_API_KEY",
                "classified": 0,
            }
        
        photos = [self.repo.get_by_id(pid) for pid in photo_ids]
        photos = [p for p in photos if p is not None]
        
        # 跳过已分类照片
        skipped = 0
        if skip_classified:
            original_count = len(photos)
            photos = [p for p in photos if p.category == "未分类"]
            skipped = original_count - len(photos)
        
        if not photos:
            msg = "没有需要分类的照片" if skipped > 0 else "未找到指定的照片"
            return {
                "success": True,
                "message": f"{msg}（跳过 {skipped} 张已分类）" if skipped else msg,
                "classified": 0,
                "skipped": skipped,
            }
        
        results = {
            "success": True,
            "total": len(photos),
            "classified": 0,
            "failed": 0,
            "details": [],
            "errors": [],
        }
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_photo = {
                executor.submit(self._classify_single_photo, photo): photo
                for photo in photos
            }
            
            for future in as_completed(future_to_photo):
                photo = future_to_photo[future]
                try:
                    result = future.result()
                    if result["success"]:
                        results["classified"] += 1
                        results["details"].append({
                            "photo_id": photo.id,
                            "category": result["category"],
                            "tags": result["tags"],
                        })
                    else:
                        results["failed"] += 1
                        results["errors"].append({
                            "photo_id": photo.id,
                            "error": result.get("error", "未知错误")
                        })
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "photo_id": photo.id,
                        "error": str(e)
                    })
        
        results["message"] = f"AI分类完成：成功{results['classified']}张，失败{results['failed']}张"
        
        return results
    
    def _classify_single_photo(self, photo, max_retries: int = 2) -> Dict[str, Any]:
        """
        对单张照片进行AI分类
        """
        # 获取缩略图路径
        thumb_path = self.settings.thumbs_path / f"{photo.sha1}.jpg"
        
        if not thumb_path.exists():
            return {"success": False, "error": "缩略图不存在"}
        
        # 读取并编码图片
        image_base64 = self._encode_image(thumb_path)
        
        # 调用AI API
        for attempt in range(max_retries + 1):
            try:
                result = self._call_vision_api(image_base64)
                
                if result:
                    # 更新数据库
                    self.repo.update_photo(photo.id, {
                        "category": result.get("category", "未分类"),
                        "tags_json": result.get("tags", []),
                        "caption": result.get("caption", ""),
                    })
                    
                    return {
                        "success": True,
                        "category": result.get("category"),
                        "tags": result.get("tags"),
                        "caption": result.get("caption"),
                    }
                    
            except Exception as e:
                if attempt == max_retries:
                    return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "分类失败"}
    
    def _encode_image(self, image_path: Path) -> str:
        """将图片编码为Base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _call_vision_api(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """
        调用多模态视觉API
        支持OpenAI兼容接口
        """
        settings = self.settings
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.ai_api_key}",
        }
        
        payload = {
            "model": settings.ai_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {"type": "text", "text": CLASSIFY_PROMPT},
                    ]
                }
            ],
            "max_tokens": 500,
        }
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{settings.ai_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # 解析JSON响应
            # 尝试提取JSON部分（处理可能的额外文字）
            try:
                # 直接解析
                return json.loads(content)
            except json.JSONDecodeError:
                # 尝试从内容中提取JSON
                import re
                json_match = re.search(r'\{[^{}]*\}', content)
                if json_match:
                    return json.loads(json_match.group())
                return None
    
    def get_categories(self) -> List[str]:
        """获取所有可用类别"""
        return CATEGORIES.copy()
