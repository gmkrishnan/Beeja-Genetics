import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\clinical_vault.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", [row[0] for row in cursor.fetchall()])

cursor.execute("SELECT drug_name FROM medicine_vault LIMIT 10")
print("Drug Names:", [row[0] for row in cursor.fetchall()])
conn.close()
