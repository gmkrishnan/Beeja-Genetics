import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.parser import load_registry, scan_dna, apply_epigenetic_logic
from core.gemma import generate_dietary_report

async def run_real_test():
    print("--- RUNNING REAL GENETIC TEST: JAMES JONES ---")
    
    registry_path = "registry/knowledge.json"
    # Using the real file provided by the user
    dna_path = "D:/Building/beeja/Beeja_Genetic/raw_data/genome_James_Jones_v5_Full_20230726173828/genome_James_Jones_v5_Full_20230726173828.txt"
    
    user_profile = {
        "age": 45,
        "diet_type": "Vegan",
        "goal": "Longevity and Energy"
    }

    print(f"Step 1: Loading Science Registry...")
    registry = load_registry(registry_path)

    print(f"Step 2: Scanning REAL DNA data...")
    try:
        scan_results = scan_dna(dna_path, registry)
        analysis = apply_epigenetic_logic(scan_results, user_profile['age'])

        print(f"Step 3: Found {len(scan_results)} real genetic matches. Generating Report...")
        
        report = await generate_dietary_report(user_profile, analysis)

        print("-" * 50)
        print("GENEGUARDIAN REAL TEST REPORT")
        print("-" * 50)
        print(report)
        print("-" * 50)
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_real_test())
