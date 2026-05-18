import sqlite3
import os

DB_PATH = r"D:\Building\beeja\Beeja_Genetic\backend\registry\master_traits.db"

def clinical_shatter():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- BEEJA CLINICAL SHATTER: 15-MAJOR ALIGNMENT ---")

    # 1. Create New Majors: OncoGenomics & SensoryGenomics
    onco_kws = ["Cancer", "Oncology", "Tumor", "Carcinoma", "Leukemia", "Lymphoma", "Melanoma", "Neoplasm"]
    sensory_kws = ["Eye", "Vision", "Retina", "Ear", "Hearing", "Ocular", "Auditory", "Smell", "Taste", "Olfactory"]

    for kw in onco_kws:
        cursor.execute("UPDATE traits SET major_category = 'OncoGenomics' WHERE (trait LIKE ? OR sub_category LIKE ?) AND major_category = 'BioGenomics'", (f"%{kw}%", f"%{kw}%"))
    print(f"Mapped Oncology: {cursor.rowcount} traits")

    for kw in sensory_kws:
        cursor.execute("UPDATE traits SET major_category = 'SensoryGenomics' WHERE (trait LIKE ? OR sub_category LIKE ?) AND major_category = 'BioGenomics'", (f"%{kw}%", f"%{kw}%"))
    print(f"Mapped Sensory: {cursor.rowcount} traits")

    # 2. Shatter Anatomy & Internal Organs
    shatter_map = {
        "OsteoGenomics": ["Bone", "Skeletal", "Joint", "Cartilage", "Fracture", "Density"],
        "FitnessGenomics": ["Muscle", "Tendon", "Ligament", "Strength", "Grip", "Fiber"],
        "DermoGenomics": ["Skin", "Hair", "Nail", "Collagen", "Elasticity", "Dermal"],
        "CardioGenomics": ["Heart", "Artery", "Vein", "Cardiac", "Vascular", "Valve"],
        "NeuroGenomics": ["Brain", "Neuron", "Nerve", "Cerebral", "Focus", "Cognitive"]
    }

    for major, kws in shatter_map.items():
        for kw in kws:
            cursor.execute("UPDATE traits SET major_category = ? WHERE (trait LIKE ? OR sub_category LIKE ?) AND (major_category = 'BioGenomics' OR master_category = 'Anatomy')", (major, f"%{kw}%", f"%{kw}%"))
        print(f"Shattered into {major}")

    # 3. Clean up Master/Sub Labels for Labeled Traits
    # Replace 'Anatomy' and 'Internal Organs' with specialist headers
    cursor.execute("UPDATE traits SET master_category = 'Clinical Physiology' WHERE master_category = 'Anatomy' AND major_category != 'BioGenomics'")
    cursor.execute("UPDATE traits SET sub_category = 'Organ Systems' WHERE sub_category = 'Internal Organs' AND major_category != 'BioGenomics'")

    # Final Check: Ensure every Gastro/Renal/Onco/Sensory trait has a professional Sub Category
    # If sub_category is empty or 'Internal Organs', try to infer it
    cursor.execute("SELECT rowid, trait, major_category FROM traits WHERE (sub_category IS NULL OR sub_category = '' OR sub_category = 'Internal Organs') AND major_category != 'BioGenomics'")
    orphans = cursor.fetchall()
    
    for rowid, trait, major in orphans:
        # Simple inference logic
        new_sub = "General Physiology"
        if "liver" in trait.lower(): new_sub = "Hepatic Health"
        elif "kidney" in trait.lower() or "renal" in trait.lower(): new_sub = "Renal Filtration"
        elif "cancer" in trait.lower(): new_sub = "Oncogenic Risk"
        elif "eye" in trait.lower(): new_sub = "Vision Care"
        elif "bone" in trait.lower(): new_sub = "Skeletal Integrity"
        
        cursor.execute("UPDATE traits SET sub_category = ? WHERE rowid = ?", (new_sub, rowid))

    conn.commit()
    print("Migration Complete! The 'Select Focus Area' is now clinical-grade.")
    conn.close()

if __name__ == "__main__":
    clinical_shatter()
