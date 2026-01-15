"""检查照片状态"""
import sqlite3
import os

conn = sqlite3.connect('data/photos.db')
cur = conn.cursor()

# 查看照片列表
cur.execute('SELECT id, file_name, file_path, library_path FROM photos LIMIT 10')
rows = cur.fetchall()

print("=" * 60)
print("照片列表:")
print("=" * 60)

for r in rows:
    file_exists = os.path.exists(r[2]) if r[2] else False
    organized = "已整理" if r[3] else "待整理"
    exists_str = "存在" if file_exists else "不存在"
    print(f"  ID:{r[0]:3d} | {organized} | 源文件{exists_str} | {r[1]}")
    if not file_exists:
        print(f"         源路径: {r[2]}")

print()
cur.execute('SELECT COUNT(*) FROM photos WHERE library_path IS NULL')
print(f"待整理照片数: {cur.fetchone()[0]}")

cur.execute('SELECT COUNT(*) FROM photos WHERE library_path IS NOT NULL')
print(f"已整理照片数: {cur.fetchone()[0]}")

cur.execute('SELECT COUNT(*) FROM photos')
print(f"总照片数: {cur.fetchone()[0]}")

conn.close()
