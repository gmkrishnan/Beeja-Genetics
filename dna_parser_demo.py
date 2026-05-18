import csv
import json

# 1. This is our "Medical Knowledge Base" (The Dictionary)
# In a real app, this would be a larger database of known genetic markers.
DISEASE_DB = {
    "rs7903146": {
        "disease": "Type 2 Diabetes",
        "risk_alleles": ["T", "TT", "TC"],  # If they have T, risk is higher
        "safe_alleles": ["CC"]
    },
    "rs4988235": {
        "disease": "Lactose Intolerance",
        "risk_alleles": ["CC"], # CC means lactose intolerant
        "safe_alleles": ["GG", "AG"]
    }
}

def analyze_dna_file(filepath, user_age, user_diet):
    """Parses a 23andMe txt file and checks it against our Disease DB."""
    
    findings = []
    
    # 2. Open and parse the raw DNA file (It's just a TSV file!)
    with open(filepath, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        
        for row in reader:
            # Skip comments/headers
            if not row or row[0].startswith('#'):
                continue
                
            rsid = row[0]
            genotype = row[3]
            
            # 3. Check if this SNP is in our database
            if rsid in DISEASE_DB:
                db_entry = DISEASE_DB[rsid]
                
                # 4. Check if their genotype matches a risk
                if genotype in db_entry["risk_alleles"] or any(allele in genotype for allele in db_entry["risk_alleles"]):
                    
                    # 5. Apply the "Epigenetic Door" Logic based on Age
                    door_status = "Closed"
                    if user_age > 40:
                        door_status = "Wide Open (High Urgency)"
                    elif user_age > 20:
                        door_status = "Slightly Open (Prevention)"
                        
                    findings.append({
                        "disease": db_entry["disease"],
                        "risk_level": "HIGH",
                        "door_status": door_status,
                        "marker_found": f"{rsid} ({genotype})"
                    })
    
    # 6. Format the final output to send to Gemma 4 (Ollama)
    prompt_context = f"""
    You are GeneGuardian, a clinical dietitian. 
    User Profile: Age {user_age}, Diet Preference: {user_diet}.
    
    Genetic Analysis Results:
    """
    for finding in findings:
        prompt_context += f"- HIGH RISK: {finding['disease']}. Epigenetic Status: {finding['door_status']}\n"
        
    prompt_context += "\nTASK: Based ONLY on the open doors above, suggest 3 foods to consume and 3 foods to strictly avoid. Provide a 1-day meal plan."
    
    return prompt_context

# --- DEMO EXECUTION ---
if __name__ == "__main__":
    # Let's create a fake DNA file with real markers to test it
    test_file = "test_dna.txt"
    with open(test_file, 'w') as f:
        f.write("# rsid\tchromosome\tposition\tgenotype\n")
        f.write("rs7903146\t10\t114758349\tTT\n")  # High risk for Diabetes
        f.write("rs4988235\t2\t136608646\tCC\n")   # Lactose Intolerant
        f.write("rs123456\t1\t12345\tAA\n")     # Irrelevant marker
        
    # Run the parser for a 45-year-old Vegan
    final_gemma_prompt = analyze_dna_file(test_file, user_age=45, user_diet="Vegan")
    
    print("=== WHAT WE SEND TO GEMMA 4 (OLLAMA) ===\n")
    print(final_gemma_prompt)
