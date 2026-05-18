import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def finalize_master_labels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- FINALIZING PROFESSIONAL MASTER LABELS ---")

    # Map of Major Category to its Professional Master Header
    label_map = {
        "OncoGenomics": "Clinical Oncology & Tumors",
        "GastroGenomics": "Gastrointestinal & Hepatic Health",
        "CardioGenomics": "Cardiovascular Physiology",
        "SensoryGenomics": "Senses & Ophthalmology",
        "NeuroGenomics": "Advanced Neurology",
        "RenalGenomics": "Urological & Renal Health",
        "EndoGenomics": "Endocrine & Glandular Systems",
        "OsteoGenomics": "Skeletal & Bone Integrity",
        "FitnessGenomics": "Sports & Muscle Physiology",
        "DermoGenomics": "Dermatology & Skin Science",
        "ImmuGenomics": "Immunology & Disease Defense",
        "NutriGenomics": "Nutritional & Metabolic Science",
        "PharmaGenomics": "Clinical Pharmacogenomics",
        "PulmoGenomics": "Pulmonary & Respiratory Science"
    }

    total_updated = 0
    for major, master_name in label_map.items():
        cursor.execute("""
            UPDATE traits 
            SET master_category = ? 
            WHERE (master_category IS NULL OR master_category = '' OR master_category = 'Unknown Master')
            AND major_category = ?
        """, (master_name, major))
        
        updated = cursor.rowcount
        total_updated += updated
        if updated > 0:
            print(f"  - {major}: Labeled {updated} traits as '{master_name}'")

    # Handle any remaining in BioGenomics that actually have data
    cursor.execute("""
        UPDATE traits 
        SET master_category = 'Biological Foundations' 
        WHERE (master_category IS NULL OR master_category = '' OR master_category = 'Unknown Master')
        AND major_category = 'BioGenomics'
        AND (sub_category IS NOT NULL AND sub_category != '')
    """)
    print(f"  - BioGenomics: Cleaned up {cursor.rowcount} labeled orphans.")

    conn.commit()
    print(f"\nSUCCESS: {total_updated} traits have been professionally shelf-labeled.")
    conn.close()

if __name__ == "__main__":
    finalize_master_labels()
