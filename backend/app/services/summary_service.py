"""
总结服务模块
负责生成统计数据和AI拍摄总结
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from sqlalchemy.orm import Session

from ..core.config import get_settings
from ..db.photos_repo import PhotosRepository


# 总结生成Prompt模板
SUMMARY_PROMPT = """你是一名摄影教练。请基于以下统计数据生成"拍摄复盘"，输出为中文，结构如下：
- 今日主题概览（2-3 句）
- 数据解读（要点：焦段、ISO、快门、光圈的主要分布与结论）
- 3 条可执行建议
- 精选推荐（1 句）

统计数据（JSON）：
{stats_json}

请用通俗易懂的语言，让摄影新手也能理解。"""


class SummaryService:
    """拍摄总结服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = PhotosRepository(db)
        self.settings = get_settings()
    
    def generate_summary(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        生成拍摄总结
        
        Args:
            date_from: 开始日期
            date_to: 结束日期
        
        Returns:
            包含统计图表数据和AI生成文案的结果
        """
        # 获取统计数据
        stats = self.repo.get_statistics(date_from, date_to)
        
        if stats["total"] == 0:
            return {
                "success": False,
                "message": "没有照片数据可用于生成总结",
                "stats": stats,
            }
        
        # 准备图表数据（前端可直接使用）
        chart_data = self._prepare_chart_data(stats)
        
        # 生成AI总结文案
        ai_summary = None
        if self.settings.ai_api_key and self.settings.ai_api_key != "your_api_key_here":
            try:
                ai_summary = self._generate_ai_summary(stats)
            except Exception as e:
                ai_summary = f"AI总结生成失败: {str(e)}"
        else:
            ai_summary = "未配置AI API Key，无法生成AI总结。请在.env文件中配置AI_API_KEY。"
        
        return {
            "success": True,
            "message": "总结生成成功",
            "stats": stats,
            "charts": chart_data,
            "ai_summary": ai_summary,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            }
        }
    
    def _prepare_chart_data(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备前端图表数据
        格式为ECharts可直接使用的格式
        """
        return {
            # 类别分布（饼图）
            "category_pie": {
                "title": "照片类别分布",
                "data": [
                    {"name": k, "value": v}
                    for k, v in stats.get("categories", {}).items()
                ]
            },
            # 焦段分布（柱状图）
            "focal_bar": {
                "title": "焦段分布",
                "categories": list(stats.get("focal_lengths", {}).keys()),
                "values": list(stats.get("focal_lengths", {}).values()),
            },
            # ISO分布（柱状图）
            "iso_bar": {
                "title": "ISO分布",
                "categories": list(stats.get("isos", {}).keys()),
                "values": list(stats.get("isos", {}).values()),
            },
            # 光圈分布（柱状图）
            "aperture_bar": {
                "title": "光圈分布",
                "categories": list(stats.get("apertures", {}).keys()),
                "values": list(stats.get("apertures", {}).values()),
            },
            # 相机使用统计（饼图）
            "camera_pie": {
                "title": "相机使用统计",
                "data": [
                    {"name": k, "value": v}
                    for k, v in stats.get("cameras", {}).items()
                ]
            },
            # 概览数据
            "overview": {
                "total": stats.get("total", 0),
                "with_raw": stats.get("with_raw", 0),
                "selected": stats.get("selected", 0),
            }
        }
    
    def _generate_ai_summary(self, stats: Dict[str, Any]) -> str:
        """
        调用LLM生成总结文案
        """
        settings = self.settings
        
        # 准备统计数据JSON（简化版，避免token过多）
        stats_for_ai = {
            "总照片数": stats.get("total", 0),
            "含RAW数量": stats.get("with_raw", 0),
            "精选数量": stats.get("selected", 0),
            "类别分布": stats.get("categories", {}),
            "焦段分布": stats.get("focal_lengths", {}),
            "ISO分布": stats.get("isos", {}),
            "光圈分布": stats.get("apertures", {}),
            "相机统计": stats.get("cameras", {}),
        }
        
        prompt = SUMMARY_PROMPT.format(stats_json=json.dumps(stats_for_ai, ensure_ascii=False, indent=2))
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.ai_api_key}",
        }
        
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
        }
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{settings.ai_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """
        获取快速统计（首页展示用）
        """
        stats = self.repo.get_statistics()
        
        return {
            "total_photos": stats.get("total", 0),
            "with_raw": stats.get("with_raw", 0),
            "selected": stats.get("selected", 0),
            "categories_count": len(stats.get("categories", {})),
            "cameras_count": len(stats.get("cameras", {})),
        }
