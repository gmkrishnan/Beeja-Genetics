import sqlite3
import json

def analyze_taxonomy(db_path="registry/master_traits.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get Major Categories
    cursor.execute("SELECT DISTINCT major_category FROM traits")
    majors = [row[0] for row in cursor.fetchall() if row[0]]
    
    report = {}
    for major in majors:
        cursor.execute("SELECT DISTINCT master_category FROM traits WHERE major_category = ?", (major,))
        masters = [row[0] for row in cursor.fetchall() if row[0]]
        
        report[major] = {}
        for master in masters:
            cursor.execute("SELECT DISTINCT sub_category FROM traits WHERE major_category = ? AND master_category = ?", (major, master))
            subs = [row[0] for row in cursor.fetchall() if row[0]]
            report[major][master] = subs
            
    # Count traits
    cursor.execute("SELECT COUNT(*) FROM traits")
    total_traits = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Total Traits in DB: {total_traits}")
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    analyze_taxonomy()
