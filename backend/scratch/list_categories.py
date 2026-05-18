import sqlite3
import os

db_path = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT master_category FROM traits")
    rows = cursor.fetchall()
    for row in rows:
        print(row[0])
    conn.close()
else:
    print("Database not found.")
