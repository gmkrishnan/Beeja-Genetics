import sqlite3
import os
from snps import SNPs

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'registry', 'clinical_vault.db')

def scan_dna(file_path):
    """
    Scans a raw DNA file and classifies findings into High, Moderate, and Typical risk levels.
    """
    results = []
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DNA file not found at {file_path}")

    # 1. Initialize the robust SNPs parser
    s = SNPs(file_path)
    print(f"Detected Source: {s.source}, Build: {s.build}")

    # 2. Connect to the Clinical Vault
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 3. Get all markers to scan
    c.execute("""
        SELECT m.*, c.name as category_name 
        FROM markers m 
        JOIN categories c ON m.category_id = c.id
    """)
    all_markers = c.fetchall()

    # 4. Filter DNA file
    for marker in all_markers:
        rsid = marker["rsid"]
        
        if rsid in s.snps.index:
            snp_match = s.snps.loc[rsid]
            genotype = snp_match['genotype']
            
            if not isinstance(genotype, str) or not genotype:
                continue
                
            high_risk_geno = str(marker["risk_genotype"])
            mod_risk_geno = str(marker["moderate_genotype"])
            
            risk_tier = "TYPICAL"
            predisposition_pct = 20 # Baseline
            multiplier = 1.0

            # Check for High Risk (Homozygous)
            if high_risk_geno in genotype or genotype in high_risk_geno:
                risk_tier = "HIGH"
                predisposition_pct = marker["high_risk_pct"]
                multiplier = marker["multiplier_high"]
            # Check for Moderate Risk (Heterozygous)
            elif mod_risk_geno in genotype or genotype in mod_risk_geno:
                risk_tier = "MODERATE"
                predisposition_pct = marker["mod_risk_pct"]
                multiplier = marker["multiplier_mod"]
            
            # Always append if found, so we can filter by tier later
            results.append({
                "category": marker["category_name"],
                "gene": marker["gene"],
                "rsid": rsid,
                "trait": marker["trait"],
                "impact": marker["impact"],
                "priority": marker["priority"],
                "protocol": marker["dietary_protocol"],
                "mitigation": marker["mitigation_strategy"],
                "mitigation_type": marker["mitigation_type"],
                "mitigation_link": marker["mitigation_evidence_link"],
                "onset_age": marker["onset_age"],
                "user_genotype": genotype,
                "risk_tier": risk_tier,
                "predisposition_pct": predisposition_pct,
                "multiplier": multiplier
            })
    
    conn.close()
    return results

def apply_epigenetic_logic(scan_results, user_age):
    """
    Groups findings by Risk Tier and applies age-based 'Door' status.
    """
    # Grouping by tier for the UI/Report
    categorized = {
        "HIGH_PREDISPOSITION": [],
        "MODERATE_PREDISPOSITION": [],
        "TYPICAL_PREDISPOSITION": []
    }
    
    for result in scan_results:
        onset = result["onset_age"]
        tier = result["risk_tier"]
        
        # Age-based logic
        if user_age >= onset + 10:
            result["door_status"] = "WIDE OPEN"
        elif user_age >= onset - 5:
            result["door_status"] = "OPENING"
        else:
            result["door_status"] = "CLOSED"
            
        if tier == "HIGH":
            categorized["HIGH_PREDISPOSITION"].append(result)
        elif tier == "MODERATE":
            categorized["MODERATE_PREDISPOSITION"].append(result)
        else:
            categorized["TYPICAL_PREDISPOSITION"].append(result)
            
    return categorized

def scan_medicine_safety(file_path):
    """
    Scans DNA for pharmacogenomic markers and returns drug-gene safety alerts.
    """
    safety_alerts = []
    
    if not os.path.exists(file_path):
        return []

    s = SNPs(file_path)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get all PGx markers from the medicine vault
    c.execute("SELECT * FROM medicine_vault")
    pgx_markers = c.fetchall()

    for marker in pgx_markers:
        rsid = marker["rsid"]
        if rsid in s.snps.index:
            user_genotype = s.snps.loc[rsid]['genotype']
            risk_genotype = marker["genotype"]
            
            # Simple match (In PGx, specific genotypes define the phenotype)
            if risk_genotype in user_genotype or user_genotype in risk_genotype:
                safety_alerts.append({
                    "drug_name": marker["drug_name"],
                    "gene": marker["gene"],
                    "rsid": rsid,
                    "user_genotype": user_genotype,
                    "risk_level": marker["risk_level"],
                    "recommendation": marker["recommendation"],
                    "alternative": marker["alternative"],
                    "mitigation": marker["mitigation_strategy"],
                    "mitigation_type": marker["mitigation_type"],
                    "mitigation_link": marker["mitigation_evidence_link"],
                    "why": marker["biological_logic"],
                    "evidence": marker["evidence_link"]
                })
    
    conn.close()
    return safety_alerts
