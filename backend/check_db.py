import sqlite3

conn = sqlite3.connect('data/photos.db')
cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name='photos'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("Table not found")
conn.close()
