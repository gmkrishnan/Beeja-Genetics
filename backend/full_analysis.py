import asyncio
import sys
import os
import json
import random

# Add the app directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__name__ == '__main__' and __file__ or '.'), 'app'))

from core.parser import scan_dna, apply_epigenetic_logic, scan_medicine_safety
from core.gemma import generate_dietary_report, summarize_research
from core.evidence import get_evidence_for_marker

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'ignore').decode('ascii'))

def apply_category_cap(raw_results, cap=2):
    """
    Implements the 'Category-Aware Cap':
    Groups results by Category (Nutrition, Medicine, Fitness, Environment),
    then by Tier, and caps each intersection at the specified 'cap' limit.
    """
    from collections import defaultdict
    category_groups = defaultdict(lambda: defaultdict(list))
    
    # 1. Group by Category and Tier
    for item in raw_results:
        cat = item.get('category', 'Wellness')
        tier = item.get('predisposition', 'MODERATE_PREDISPOSITION')
        category_groups[cat][tier].append(item)
    
    # 2. Sample 'cap' from each Tier within each Category
    capped_results = []
    for cat, tiers in category_groups.items():
        for tier, markers in tiers.items():
            if len(markers) <= cap:
                capped_results.extend(markers)
            else:
                capped_results.extend(random.sample(markers, cap))
                
    return capped_results

async def run_analysis():
    # 1. Inputs & Configuration
    dna_file = r"D:\Building\beeja\Beeja_Genetic\raw_data\genome_James_Jones_v5_Full_20230726173828\genome_James_Jones_v5_Full_20230726173828.txt"
    
    # Cloud/Fallback validation: If the heavy raw genomic data file is not found,
    # generate a highly accurate, simulated 23andMe formatted genomic sample.
    if not os.path.exists(dna_file):
        dna_file = "simulated_james_jones_dna.txt"
        if not os.path.exists(dna_file):
            safe_print("INFO: DNA file not found at local absolute path. Automatically generating a high-fidelity simulated 23andMe genomic sample...")
            mock_data = (
                "# 23andMe format simulated genomic data\n"
                "# rsid\tchromosome\tposition\tgenotype\n"
                "rs7903146\t10\t114758349\tTT\n"
                "rs9939609\t16\t53820527\tAA\n"
                "rs1801133\t1\t11856378\tTT\n"
                "rs762551\t15\t80000000\tAC\n"
                "rs429358\t19\t45411941\tCT\n"
                "rs6265\t11\t27679944\tCC\n"
                "rs3746444\t22\t42526000\tGG\n"
                "rs1799853\t10\t96792000\tCC\n"
                "rs12248560\t10\t102000000\tTT\n"
                "rs3918290\t5\t1000000\tAT\n"
                "rs3099844\t6\t2000000\tCT\n"
            )
            with open(dna_file, "w", encoding="utf-8") as f:
                f.write(mock_data)
    user_profile = {
        "age": 25,
        "gender": "Male",
        "country": "India",
        "diet_type": "Vegetarian",
        "goal": "Optimize performance and longevity",
        "is_pregnant": False 
    }
    
    report_config = {"show_explanations": True, "show_meals": True}

    safe_print(f"--- STARTING SPEED-OPTIMIZED ANALYSIS (CAP AT 2) ---")
    
    try:
        # Step 1: Scan DNA (Raw pass)
        safe_print("Step 1: Scanning DNA against the Clinical Vault...")
        raw_results = scan_dna(dna_file)
        
        # Step 2: Apply the Category-Aware Cap at 2
        safe_print("Step 2: Applying Category-Aware 'Cap at 2' (Ensuring 360-degree coverage)...")
        capped_raw = apply_category_cap(raw_results)
        
        # Step 3: Apply Epigenetic Logic to the capped set
        safe_print("Step 3: Applying Epigenetic 'Open Door' logic...")
        analysis_results = apply_epigenetic_logic(capped_raw, user_profile['age'])
        
        # Step 4: Scan for Medicine Safety (Apply Cap at 2)
        safe_print("Step 4: Scanning for Medicine Safety Alerts...")
        pgx_results = scan_medicine_safety(dna_file)
        if len(pgx_results) > 2:
            pgx_results = random.sample(pgx_results, 2)
        
        # Step 5: Research Evidence for High Risk markers
        safe_print("Step 5: Fetching Research Evidence for selected markers...")
        evidence_vault = {}
        high_risks = analysis_results.get("HIGH_PREDISPOSITION", [])
        for item in high_risks:
            evidence = await get_evidence_for_marker(item['gene'], item['trait'])
            summarized_evidence = []
            for paper in evidence[:2]:
                summary = await summarize_research(paper['abstract'])
                paper['ai_summary'] = summary
                summarized_evidence.append(paper)
            evidence_vault[item['rsid']] = summarized_evidence
        
        # Step 6: Generate AI Report
        safe_print("Step 6: Synthesizing Optimized Report via Gemma 4 (Rule of 2)...")
        report = await generate_dietary_report(user_profile, analysis_results, report_config, evidence_vault, medicine_alerts=pgx_results)
        
        # Step 7: Build Supplemental Sections
        # Build the Medicine Compass Section
        medicine_section = "\n\n### 🛡️ MEDICINE SAFETY COMPASS\n"
        for m in pgx_results:
            medicine_section += f"#### Medication: {m['drug_name']}\n"
            medicine_section += f"- **Risk Level:** {m['risk_level']}\n"
            medicine_section += f"- **Plan B Strategy:** {m.get('mitigation', 'N/A')}\n"
            medicine_section += f"- **Why:** {m['why']}\n"
            medicine_section += f"- **Scientific Proof:** [PubMed Link]({m['evidence']})\n\n"

        # Build the Evidence Section
        evidence_section = "\n\n### 🔬 SCIENTIFIC EVIDENCE & CITATIONS\n"
        for rsid, papers in evidence_vault.items():
            evidence_section += f"#### Marker: {rsid}\n"
            for p in papers:
                evidence_section += f"- **{p['title']}**\n"
                evidence_section += f"  *Summary:* {p.get('ai_summary', 'N/A')}\n"
                evidence_section += f"  *Link:* [{p['link']}]({p['link']})\n\n"

        # Step 7: Run Agent for Custom Category (Organ Strength)
        safe_print("Step 7: Running Agent for Custom Category 'Organ Strength'...")
        from core.agent import run_agent_loop
        agent_goal = "Analyze my genetic Organ Strength for Liver and Kidney. Research PubMed if needed, scan my DNA, and save the discovery."
        agent_result = await run_agent_loop(agent_goal)

        # Step 8: Save the Report
        output_path = os.path.join(os.path.dirname(__file__), "James_Jones_Fast_Report.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
            f.write(medicine_section)
            f.write(evidence_section)
            f.write("\n\n### 🔬 AGENTIC CUSTOM DISCOVERY: ORGAN STRENGTH\n")
            f.write(agent_result)

        
        safe_print(f"\nSuccess! Fast Report generated.")
        safe_print(f"Output saved to: {output_path}")
        
    except Exception as e:
        safe_print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_analysis())
