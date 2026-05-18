from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import json
import asyncio
import sqlite3
import datetime

# Path hack to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from core.gemma import agent_chat
from core.agent import run_agent_loop
from result_manager import get_categories_by_status, set_category_status

# GLOBAL AGENT IMPORTS
from app.core.parser import scan_dna, scan_medicine_safety
from app.agents.pharma_agent import PharmaAgent
from app.agents.nutri_agent import NutriAgent
from app.agents.fitness_agent import FitnessAgent
from app.agents.neuro_agent import NeuroAgent
from app.agents.immu_agent import ImmuAgent
from app.agents.cardio_agent import CardioAgent
from app.agents.dermo_agent import DermoAgent
from app.agents.endo_agent import EndoAgent
from app.agents.osteo_agent import OsteoAgent
from app.agents.bio_agent import BioAgent
from app.agents.gastro_agent import GastroAgent
from app.agents.pulmo_agent import PulmoAgent
from app.agents.renal_agent import RenalAgent
from app.agents.onco_agent import OncoAgent
from app.agents.sensory_agent import SensoryAgent

# Initialize the 15-Agent Swarm Globally
swarm = {
    "Pharma": PharmaAgent(),
    "Nutri": NutriAgent(),
    "Fitness": FitnessAgent(),
    "Neuro": NeuroAgent(),
    "Immu": ImmuAgent(),
    "Cardio": CardioAgent(),
    "Dermo": DermoAgent(),
    "Endo": EndoAgent(),
    "Osteo": OsteoAgent(),
    "Bio": BioAgent(),
    "Gastro": GastroAgent(),
    "Pulmo": PulmoAgent(),
    "Renal": RenalAgent(),
    "Onco": OncoAgent(),
    "Sensory": SensoryAgent()
}

from app.core.helix import BeejaHelix
helix = BeejaHelix(swarm)

app = FastAPI()

DB_PATH = os.path.join(os.path.dirname(__file__), 'registry', 'clinical_vault.db')

@app.on_event("startup")
def startup_event():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            name TEXT,
            results_json TEXT
        )
    """)
    conn.commit()
    conn.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    categories: list
    file_path: str = "D:\\Building\\beeja\\Beeja_Genetic\\James_Jones_v5_Full.txt"
    analysis_mode: str = "fast"
    patient_context: dict = {"age": 35, "gender": "male", "diet": "standard"}

class SaveScanRequest(BaseModel):
    name: str
    results: list

@app.post("/save_scan")
def save_scan(request: SaveScanRequest):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scan_history (timestamp, name, results_json) VALUES (?, ?, ?)", 
                   (timestamp, request.name, json.dumps(request.results)))
    conn.commit()
    conn.close()
    return {"message": "Scan saved successfully"}

@app.get("/categories/tree")
def get_categories_tree():
    master_db = os.path.join(os.path.dirname(__file__), 'registry', 'master_traits.db')
    if not os.path.exists(master_db): return {"masters": []}
    conn = sqlite3.connect(master_db)
    cursor = conn.cursor()
    # Only select traits that have a professional Master Category (Excluding the 45k mass)
    cursor.execute("""
        SELECT major_category, master_category, sub_category, trait 
        FROM traits 
        WHERE master_category IS NOT NULL 
        AND master_category != '' 
        AND master_category != 'BEEJA_SYSTEM_CORE' 
        ORDER BY major_category, master_category, sub_category
    """)
    rows = cursor.fetchall()
    conn.close()
    
    tree = {}
    for r in rows:
        major, master, sub, trait = r
        major = str(major) if major else "BioGenomics"
        master = str(master) if master else "Clinical Foundations"
        sub = str(sub) if sub else "General Markers"
        trait = str(trait) if trait else "Unknown Trait"
        
        if major not in tree: tree[major] = {}
        if master not in tree[major]: tree[major][master] = {}
        if sub not in tree[major][master]: tree[major][master][sub] = []
        tree[major][master][sub].append(trait)
        
    formatted_tree = []
    # Sorting keys for consistent UI
    for major in sorted(tree.keys()):
        master_dict = tree[major]
        major_data = []
        for master in sorted(master_dict.keys()):
            sub_dict = master_dict[master]
            subs = [{"name": sub, "traits": sorted(traits)} for sub, traits in sub_dict.items()]
            major_data.append({"name": master, "subs": subs})
        
        icon = "🧬"
        if "Neuro" in major: icon = "🧠"
        elif "Immu" in major: icon = "🛡️"
        elif "Cardio" in major: icon = "❤️"
        elif "Pharma" in major: icon = "💊"
        elif "Nutri" in major: icon = "🍎"
        elif "Fitness" in major: icon = "🏃‍♂️"
        elif "Dermo" in major: icon = "✨"
        elif "Endo" in major: icon = "⚖️"
        elif "Osteo" in major: icon = "🦴"
            
        formatted_tree.append({
            "id": major.lower().replace(" ", "_"),
            "name": f"{icon} {major}",
            "data": major_data
        })
        
    return {"masters": formatted_tree}

async def gemma_rewrite_card(trait: str, risk_tier: str, category: str = ""):
    import httpx, json

    is_pharma = "pharma" in category.lower()

    if is_pharma:
        prompt = f"""Clinical pharmacogenomics specialist report for: '{trait}'.
Return strictly a valid JSON object with:
- "gene": primary pharmacogene (e.g. CYP2D6, CYP2C19, SLCO1B1)
- "genotype": clinically relevant allele pair (e.g. *4/*4, *1/*1)
- "phenotype": metabolizer status
- "activity_score": e.g. '0.0 / 2.0'
- "summary": 2-sentence clinical finding
- "dosing_recommendation": precise dosing action
- "metabolic_capacity": percentage string
- "interaction_risk": drug interaction warning
- "phenotype_implication": what the phenotype means clinically
- "alternatives": safer alternative medications
- "risk_tier": HIGH, MODERATE, or LOW"""
    else:
        prompt = f"Professional genetic analysis for {trait} with {risk_tier} risk. Return JSON with 'finding', 'advice', 'phenotype', 'efficiency', 'target'."

    payload = {"model": "gemma4:e2b", "prompt": prompt, "stream": False}
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            res = await client.post("http://localhost:11434/api/generate", json=payload)
            raw_text = res.json().get("response", "")
            
            # Clean markdown if present
            clean_text = raw_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            try:
                return json.loads(clean_text), 0
            except json.JSONDecodeError as je:
                print(f"[Gemma JSON Error] Failed to parse: {clean_text}")
                return None, 0
    except Exception as e: 
        print(f"[Gemma Network Error] {repr(e)}")
        return None, 0

@app.post("/analyze")
async def analyze_dna(request: AnalyzeRequest):
    f_path = "D:\\Building\\beeja\\Beeja_Genetic\\raw_data\\genome_James_Jones_v5_Full_20230726173828\\genome_James_Jones_v5_Full_20230726173828.txt"
    
    print(f"\n[ANALYSIS START] Orchestrating 10-Agent Swarm...")
    
    try:
        raw_results = scan_dna(f_path)
        filtered_results = []
        
        for item in request.categories:
            if isinstance(item, str):
                trait_name = item
                hierarchy = {"major": "Genetics", "master": "Clinical", "sub": "Analysis"}
            else:
                trait_name = str(item.get("name", "Unknown Trait"))
                hierarchy = {
                    "major": str(item.get("major", "Genetics")),
                    "master": str(item.get("master", "Clinical")),
                    "sub": str(item.get("sub", "Analysis"))
                }

            trait_lower = trait_name.lower()
            major_lower = hierarchy["major"].lower()
            master_lower = hierarchy["master"].lower()
            
            # THE CLINICAL ROUTING TABLE
            target_agent = None
            
            if "pharma" in major_lower: target_agent = swarm["Pharma"]
            elif "onco" in major_lower or "cancer" in trait_lower: target_agent = swarm["Onco"]
            elif "sensory" in major_lower or any(k in trait_lower for k in ["eye", "vision", "ear", "hearing"]): target_agent = swarm["Sensory"]
            elif "gastro" in major_lower or "digestive" in trait_lower: target_agent = swarm["Gastro"]
            elif "pulmo" in major_lower or "respiratory" in master_lower: target_agent = swarm["Pulmo"]
            elif "renal" in major_lower or "kidney" in trait_lower: target_agent = swarm["Renal"]
            elif master_lower in ["metabolism", "metabolic", "nutrition", "biochemistry"]: target_agent = swarm["Nutri"]
            elif master_lower in ["psychiatry", "cognitive", "behavior", "sleep"]: target_agent = swarm["Neuro"]
            elif master_lower in ["immunology", "hematology", "oncology", "disease", "medical", "health"]: target_agent = swarm["Immu"]
            elif master_lower in ["cardiology", "cardiovascular"]: target_agent = swarm["Cardio"]
            elif master_lower in ["morphology", "physical", "sensory"]: target_agent = swarm["Dermo"]
            elif master_lower in ["endocrine"]: target_agent = swarm["Endo"]
            elif master_lower in ["skeletal system", "musculoskeletal"]: target_agent = swarm["Osteo"]
            elif master_lower in ["physiology", "physiological", "fitness"]: target_agent = swarm["Fitness"]
            elif master_lower in ["genetics", "quantitative genetics", "biology", "biological", "anthropometry", "anatomy"]: target_agent = swarm["Bio"]
            else: target_agent = swarm["Bio"] # Default fallback

            print(f"  > Routing: {trait_name} -> {type(target_agent).__name__}")
            
            # Execute analysis via Specialist
            ctx = dict(request.patient_context) if request.patient_context else {}
            ctx.update(hierarchy)
            agent_data = await target_agent.analyze(trait_name, context=ctx)
            res = dict(agent_data)
            
            # ANCHOR TO USER HIERARCHY
            res.update(hierarchy)
            res["ui_category"] = hierarchy["major"] # Use the Pillar chosen by the user
            res["specialist"] = type(target_agent).__name__ # Track the actual agent used
            
            filtered_results.append(res)

        print(f"[ANALYSIS COMPLETE] Returning {len(filtered_results)} results.\n")
        return {"results": filtered_results}
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    mode: str = "supportive"
    file_path: str = "James_Jones_v5_Full.txt"
    patient_context: dict = None

@app.post("/chat")
async def chat_with_helix(request: ChatRequest):
    """
    CONVERSATIONAL ANALYST: Beeja Helix.
    """
    print(f"[CHAT] Message: {request.message} (Mode: {request.mode})")
    response = await helix.generate_response(
        query=request.message,
        mode=request.mode,
        patient_context=request.patient_context,
        file_path=request.file_path
    )
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
