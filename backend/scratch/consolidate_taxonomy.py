import sqlite3

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def consolidate_taxonomy():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- CONSOLIDATING TAXONOMY: REMOVING DUPLICATES ---")

    # 1. Merge Redundant Masters
    cursor.execute("UPDATE traits SET master_category = 'Biology' WHERE master_category = 'Biological'")
    cursor.execute("UPDATE traits SET master_category = 'Physiology' WHERE master_category = 'Physiological'")
    print(f"Merged Biology & Physiology: {cursor.rowcount} rows")

    # 2. Specialize 'Clinical Physiology'
    label_map = {
        "CardioGenomics": "Cardiovascular Physiology",
        "RenalGenomics": "Renal Physiology",
        "GastroGenomics": "Gastrointestinal Physiology",
        "OncoGenomics": "Oncogenic Physiology",
        "SensoryGenomics": "Sensory Physiology",
        "NeuroGenomics": "Neurological Physiology",
        "EndoGenomics": "Endocrine Physiology",
        "OsteoGenomics": "Skeletal Physiology",
        "FitnessGenomics": "Sports Physiology",
        "DermoGenomics": "Dermatological Physiology",
        "ImmuGenomics": "Immunological Physiology"
    }

    for major, master_name in label_map.items():
        cursor.execute("""
            UPDATE traits 
            SET master_category = ? 
            WHERE master_category = 'Clinical Physiology' 
            AND major_category = ?
        """, (master_name, major))
        if cursor.rowcount > 0:
            print(f"  - Specialized {major} Physiology")

    # 3. Handle leftover generic labels
    cursor.execute("UPDATE traits SET master_category = 'Clinical Foundations' WHERE master_category = 'BEEJA_SYSTEM_CORE'")

    conn.commit()
    print("\nSUCCESS: Taxonomy is now neat and consolidated.")
    conn.close()

if __name__ == "__main__":
    consolidate_taxonomy()
