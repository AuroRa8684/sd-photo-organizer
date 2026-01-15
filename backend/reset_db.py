"""
重置数据库脚本
用于演示前清空所有数据，恢复到初始状态
"""
import os
import shutil
from pathlib import Path

# 数据库和缩略图路径
DB_PATH = Path(__file__).parent / "data" / "photos.db"
THUMBS_PATH = Path(__file__).parent / "storage" / "thumbs"

def reset_database():
    """清空数据库和缩略图"""
    print("=" * 50)
    print("🗑️  SD Photo Organizer 数据库重置工具")
    print("=" * 50)
    
    # 1. 删除数据库文件
    if DB_PATH.exists():
        try:
            os.remove(DB_PATH)
            print(f"✅ 已删除数据库: {DB_PATH}")
        except PermissionError:
            print(f"❌ 无法删除数据库: 文件被占用")
            print(f"   请先停止后端服务 (Ctrl+C)，然后重新运行此脚本")
            return False
    else:
        print(f"ℹ️  数据库不存在: {DB_PATH}")
    
    # 2. 清空缩略图目录
    if THUMBS_PATH.exists():
        # 删除目录下所有文件
        count = 0
        for f in THUMBS_PATH.glob("*"):
            if f.is_file():
                f.unlink()
                count += 1
        print(f"✅ 已清空缩略图: {count} 个文件")
    else:
        print(f"ℹ️  缩略图目录不存在: {THUMBS_PATH}")
    
    print()
    print("🎉 重置完成！重启后端服务即可开始全新演示")
    print("   启动命令: python -m uvicorn app.main:app --reload")
    print()

if __name__ == "__main__":
    # 确认操作
    print()
    confirm = input("⚠️  此操作将清空所有照片数据，确定继续吗？(y/n): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("已取消操作")
