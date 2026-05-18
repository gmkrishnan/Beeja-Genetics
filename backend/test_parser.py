import sys
import os

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.parser import load_registry, scan_dna, apply_epigenetic_logic

def run_test():
    registry_path = "registry/knowledge.json"
    dna_path = "../real_23andme_sample.txt" # This is the file we downloaded earlier
    
    print(f"--- Testing Nutrigenomics Parser ---")
    
    # 1. Load Registry
    registry = load_registry(registry_path)
    print(f"Loaded registry with {len(registry['genetic_markers'])} markers.")
    
    # 2. Scan DNA
    # Note: Our sample file might not have the specific markers from our registry yet.
    # Let's ensure it has at least one for the demo.
    with open(dna_path, 'a') as f:
        f.write("\nrs7903146\t10\t114758349\tTT") # Diabetes risk
        f.write("\nrs4988235\t2\t136608646\tCC")  # Lactose intolerance
        f.write("\nrs1808593\t1\t1000000\tAA")   # Salt sensitivity
    
    results = scan_dna(dna_path, registry)
    print(f"Found {len(results)} matches in DNA file.")
    
    # 3. Apply Epigenetic Logic (Testing for a 45-year-old)
    final_analysis = apply_epigenetic_logic(results, user_age=45)
    
    print("\n--- RESULTS FOR AGE 45 ---")
    for category, items in final_analysis.items():
        print(f"\n[{category.upper()}]")
        for item in items:
            print(f" - {item['trait']}: {item['door_status']}")

if __name__ == "__main__":
    run_test()
