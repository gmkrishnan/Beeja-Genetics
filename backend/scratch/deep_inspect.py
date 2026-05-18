import sqlite3

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def deep_inspect():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- DEEP INSPECT: MASTER CATEGORIES ---")
    
    # 1. Any major that is NOT BioGenomics
    cursor.execute("""
        SELECT major_category, master_category, COUNT(*) 
        FROM traits 
        WHERE major_category != 'BioGenomics'
        GROUP BY major_category, master_category
    """)
    rows = cursor.fetchall()
    
    for major, master, count in rows:
        print(f"  - [{major}] Master: '{master}' ({count} traits)")
        
    conn.close()

if __name__ == "__main__":
    deep_inspect()
