import sqlite3

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def final_count_check():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- FINAL DB AUDIT: SPECIALIST UNKNOWNS ---")
    
    cursor.execute("""
        SELECT major_category, master_category, COUNT(*) 
        FROM traits 
        WHERE (master_category IS NULL OR master_category = '' OR master_category = 'Unknown Master')
        AND major_category != 'BioGenomics'
        GROUP BY major_category, master_category
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("DATABASE IS CLEAN: No Specialist Unknowns.")
    else:
        for r in rows:
            print(f"!!! DB STILL HAS: {r}")
            
    conn.close()

if __name__ == "__main__":
    final_count_check()
