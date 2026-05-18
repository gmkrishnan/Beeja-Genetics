import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.parser import load_registry, scan_dna, apply_epigenetic_logic
from core.gemma import generate_dietary_report

async def run_full_demo():
    print("--- STARTING GENEGUARDIAN END-TO-END DEMO ---\n")
    
    registry_path = "registry/knowledge.json"
    dna_path = "../real_23andme_sample.txt"
    
    user_profile = {
        "age": 45,
        "diet_type": "Vegan",
        "goal": "Longevity and Energy"
    }

    print(f"Step 1: Loading Science Registry...")
    registry = load_registry(registry_path)

    print(f"Step 2: Scanning DNA file for {user_profile['age']}-year-old user...")
    scan_results = scan_dna(dna_path, registry)
    analysis = apply_epigenetic_logic(scan_results, user_profile['age'])

    print(f"Step 3: Found {len(scan_results)} risk factors. Generating Dietary Report via Gemma 4...")
    print("(This may take a few seconds as Gemma runs locally on your laptop...)\n")
    
    report = await generate_dietary_report(user_profile, analysis)

    print("-" * 50)
    print("FINAL NUTRIGENOMICS DIETARY REPORT")
    print("-" * 50)
    print(report)
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(run_full_demo())
