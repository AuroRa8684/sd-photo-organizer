"""查看数据库内容"""
import sqlite3

conn = sqlite3.connect('data/photos.db')

# 查看表
print('=' * 50)
print('数据库表:')
print('=' * 50)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
for t in tables:
    print(f'  - {t[0]}')

# 照片统计
print('\n' + '=' * 50)
print('照片统计:')
print('=' * 50)
count = conn.execute('SELECT COUNT(*) FROM photos').fetchone()[0]
print(f'总照片数: {count}')

if count > 0:
    # 分类统计
    print('\n分类分布:')
    cats = conn.execute('SELECT category, COUNT(*) as cnt FROM photos GROUP BY category ORDER BY cnt DESC').fetchall()
    for c in cats:
        print(f'  {c[0]}: {c[1]} 张')

    # 精选统计
    selected = conn.execute('SELECT COUNT(*) FROM photos WHERE is_selected=1').fetchone()[0]
    print(f'\n精选照片: {selected} 张')

    # 显示最近10条记录
    print('\n' + '=' * 50)
    print('最近10张照片:')
    print('=' * 50)
    photos = conn.execute('''
        SELECT id, file_name, category, is_selected, taken_at 
        FROM photos 
        ORDER BY id DESC 
        LIMIT 10
    ''').fetchall()
    
    for p in photos:
        star = '⭐' if p[3] else '  '
        date = p[4][:10] if p[4] else '未知日期'
        print(f'{star} [{p[0]:3}] {p[1][:30]:<30} | {p[2]:<8} | {date}')

# 检查 summary_history 表
try:
    history_count = conn.execute('SELECT COUNT(*) FROM summary_history').fetchone()[0]
    print(f'\n总结历史记录: {history_count} 条')
except:
    pass

conn.close()
