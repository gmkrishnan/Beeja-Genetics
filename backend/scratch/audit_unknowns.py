import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def audit_unknown_masters():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- AUDIT: UNKNOWN MASTER CATEGORIES ---")
    
    # Check all majors (except BioGenomics as we are ignoring unknowns there for now)
    cursor.execute("""
        SELECT major_category, COUNT(*) 
        FROM traits 
        WHERE (master_category IS NULL OR master_category = '' OR master_category = 'Unknown Master')
        AND major_category != 'BioGenomics'
        GROUP BY major_category
    """)
    results = cursor.fetchall()

    if not results:
        print("No 'Unknown Master' categories found in the 14 specialist majors.")
    else:
        for major, count in results:
            print(f"  - {major}: {count} traits have 'Unknown Master'")
            
            # Get sample traits to see what they are
            cursor.execute("SELECT trait FROM traits WHERE (master_category IS NULL OR master_category = '' OR master_category = 'Unknown Master') AND major_category = ? LIMIT 3", (major,))
            samples = [r[0] for r in cursor.fetchall()]
            print(f"    Sample Traits: {samples}")

    conn.close()

if __name__ == "__main__":
    audit_unknown_masters()
