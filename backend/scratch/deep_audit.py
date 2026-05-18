import sqlite3
import os
from collections import Counter

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def deep_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- BEEJA GENETIC DEEP AUDIT ---")
    
    # 1. Check Major Distribution
    cursor.execute("SELECT major_category, COUNT(*) FROM traits GROUP BY major_category ORDER BY COUNT(*) DESC")
    distribution = cursor.fetchall()
    print("\n[1] Major Category Distribution:")
    for major, count in distribution:
        print(f"  - {major}: {count} traits")

    # 2. Analyze the massive BioGenomics cluster
    print("\n[2] Top 30 Clusters in BioGenomics (Target for Migration):")
    cursor.execute("""
        SELECT master_category, sub_category, COUNT(*) 
        FROM traits 
        WHERE major_category = 'BioGenomics' 
        GROUP BY master_category, sub_category 
        ORDER BY COUNT(*) DESC 
        LIMIT 30
    """)
    clusters = cursor.fetchall()
    for master, sub, count in clusters:
        # Get a few sample traits for keyword analysis
        cursor.execute("SELECT trait FROM traits WHERE master_category = ? AND sub_category = ? LIMIT 5", (master, sub))
        samples = [r[0] for r in cursor.fetchall()]
        print(f"  - {master} > {sub} ({count} traits): {samples}")

    # 3. Search for specific medical keywords to find missing Majors
    keywords = {
        "HepaGenomics (Liver)": ["Liver", "Bilirubin", "Hepatic", "Biliary", "Hepatitis"],
        "RenalGenomics (Kidney)": ["Kidney", "Renal", "Creatinine", "Urine", "Bladder", "Nephro"],
        "PulmoGenomics (Lung)": ["Lung", "Pulmonary", "Respiratory", "Asthma", "Oxygen"],
        "SensoryGenomics (Eye/Ear)": ["Eye", "Vision", "Retina", "Ear", "Hearing", "Ocular", "Auditory"],
        "ReproGenomics (Fertility)": ["Fertility", "Sperm", "Ovary", "Uterus", "Menstrual", "Reproductive"],
        "GastroGenomics (Gut)": ["Stomach", "Intestine", "Gastric", "Colon", "Digest", "Gut", "Microbiome"],
        "OncoGenomics (Cancer)": ["Cancer", "Oncology", "Tumor", "Carcinoma", "Leukemia"],
        "NeuroGenomics (Brain)": ["Brain", "Neuron", "Nerve", "Cerebral", "Cognitive", "Focus"]
    }

    print("\n[3] Keyword Hit Analysis (Unmapped Traits):")
    for major, kw_list in keywords.items():
        total_hits = 0
        for kw in kw_list:
            cursor.execute("SELECT COUNT(*) FROM traits WHERE (trait LIKE ? OR sub_category LIKE ?) AND major_category = 'BioGenomics'", (f"%{kw}%", f"%{kw}%"))
            total_hits += cursor.fetchone()[0]
        print(f"  - {major}: {total_hits} potential traits found in BioGenomics")

    conn.close()

if __name__ == "__main__":
    deep_audit()
