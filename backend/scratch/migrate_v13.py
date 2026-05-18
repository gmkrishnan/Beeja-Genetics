import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def inspect_and_migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Update Respiratory to PulmoGenomics
    cursor.execute("UPDATE traits SET major_category = 'PulmoGenomics' WHERE master_category = 'Respiratory'")
    print(f"Updated Respiratory: {cursor.rowcount} rows")

    # 2. Identify and move Gastro/Renal from Anatomy/Biology
    gastro_keywords = ["Liver", "Gut", "Stomach", "Intestine", "Digestion", "Gastro", "Colon", "Biliary"]
    renal_keywords = ["Kidney", "Bladder", "Urine", "Renal", "Urogenital"]

    # Check sub_categories
    cursor.execute("SELECT DISTINCT sub_category FROM traits WHERE major_category = 'BioGenomics'")
    subs = [r[0] for r in cursor.fetchall() if r[0]]
    
    for sub in subs:
        target_major = None
        if any(k.lower() in sub.lower() for k in gastro_keywords):
            target_major = "GastroGenomics"
        elif any(k.lower() in sub.lower() for k in renal_keywords):
            target_major = "RenalGenomics"
        
        if target_major:
            cursor.execute("UPDATE traits SET major_category = ? WHERE sub_category = ?", (target_major, sub))
            print(f"Moved Sub-category '{sub}' to {target_major}: {cursor.rowcount} rows")

    # Check traits directly for orphans
    for keyword in gastro_keywords:
        cursor.execute("UPDATE traits SET major_category = 'GastroGenomics' WHERE (trait LIKE ? OR sub_category LIKE ?) AND major_category = 'BioGenomics'", (f"%{keyword}%", f"%{keyword}%"))
    
    for keyword in renal_keywords:
        cursor.execute("UPDATE traits SET major_category = 'RenalGenomics' WHERE (trait LIKE ? OR sub_category LIKE ?) AND major_category = 'BioGenomics'", (f"%{keyword}%", f"%{keyword}%"))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    inspect_and_migrate()
