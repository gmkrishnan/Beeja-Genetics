import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add major_category column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE traits ADD COLUMN major_category TEXT DEFAULT 'BioGenomics'")
        print("Added 'major_category' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("'major_category' column already exists.")
        else:
            print(f"Error adding column: {e}")

    # 2. Define the Mapping
    mapping = {
        "PharmaGenomics": [], # Usually derived from medication safety, but we can assign if any match
        "NutriGenomics": ["Metabolism", "Metabolic", "Nutrition", "Biochemistry"],
        "NeuroGenomics": ["Psychiatry", "Cognitive", "Behavior", "Sleep"],
        "ImmuGenomics": ["Immunology", "Hematology", "Oncology", "Disease", "Medical", "Health"],
        "CardioGenomics": ["Cardiology", "Cardiovascular", "Respiratory"],
        "DermoGenomics": ["Morphology", "Physical", "Sensory"],
        "EndoGenomics": ["Endocrine"],
        "OsteoGenomics": ["Skeletal System", "Musculoskeletal"],
        "FitnessGenomics": ["Physiology", "Physiological", "Fitness"],
        "BioGenomics": ["Genetics", "Quantitative Genetics", "Biology", "Biological", "Anthropometry", "Anatomy"]
    }

    # 3. Update the records
    total_updated = 0
    for major, masters in mapping.items():
        if not masters: continue
        
        # Create a placeholder string like "?, ?, ?"
        placeholders = ', '.join(['?'] * len(masters))
        query = f"UPDATE traits SET major_category = ? WHERE master_category IN ({placeholders})"
        
        params = [major] + masters
        cursor.execute(query, params)
        updated_count = cursor.rowcount
        total_updated += updated_count
        print(f"Mapped {updated_count} traits to {major}")

    # Commit the changes
    conn.commit()
    print(f"\nMigration Complete! Total traits mapped: {total_updated}")
    conn.close()

if __name__ == "__main__":
    migrate_database()
