import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.parser import load_registry, scan_dna, apply_epigenetic_logic
from core.gemma import generate_dietary_report

async def run_child_test():
    print("--- RUNNING REAL TEST: 13-YEAR-OLD MALE (INDIA, VEG) ---")
    
    registry_path = "registry/knowledge.json"
    dna_path = "D:/Building/beeja/Beeja_Genetic/raw_data/genome_James_Jones_v5_Full_20230726173828/genome_James_Jones_v5_Full_20230726173828.txt"
    
    user_profile = {
        "age": 13,
        "gender": "Male",
        "country": "India",
        "diet_type": "Vegetarian (Veg)",
        "goal": "Growth and Mental Focus"
    }

    print(f"Step 1: Loading Science Registry...")
    registry = load_registry(registry_path)

    print(f"Step 2: Scanning DNA data for adolescent markers...")
    scan_results = scan_dna(dna_path, registry)
    analysis = apply_epigenetic_logic(scan_results, user_profile['age'])

    print(f"Step 3: Generating Age & Location-specific Report...")
    
    report = await generate_dietary_report(user_profile, analysis)

    print("-" * 50)
    print("GENEGUARDIAN ADOLESCENT INDIA REPORT")
    print("-" * 50)
    print(report)
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_child_test())
