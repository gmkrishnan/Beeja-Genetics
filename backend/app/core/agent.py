import sqlite3
import time
import os
import sys
import json
import asyncio

# Path hack to ensure imports work when run directly or from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.gemma import agent_chat
from snps import SNPs


DNA_FILE_PATH = r"D:\Building\beeja\Beeja_Genetic\raw_data\genome_James_Jones_v5_Full_20230726173828\genome_James_Jones_v5_Full_20230726173828.txt"
if not os.path.exists(DNA_FILE_PATH):
    DNA_FILE_PATH = "simulated_james_jones_dna.txt"

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'registry', 'clinical_vault.db')
VAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'registry', 'organ_strength_vault.json')

# --- Tool Definitions for Gemma 4 ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_clinical_vault",
            "description": "Searches the existing clinical vault for genetic markers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The gene or trait to search for."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_pubmed",
            "description": "Searches PubMed for clinical evidence and abstracts. Use this to find Plan B and Survival Tips.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query (e.g., 'Liver detox genes')."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scan_dna_for_gene",
            "description": "Scans the user's DNA file for a specific gene to find the genotype.",
            "parameters": {
                "type": "object",
                "properties": {
                    "gene_name": {"type": "string", "description": "The name of the gene (e.g., 'CYP2D6')."}
                },
                "required": ["gene_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_discovery",
            "description": "Saves the newly discovered knowledge structure to the Organ Strength Vault.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "The category name (e.g., 'Organ Strength')."},
                    "marker_data": {
                        "type": "object",
                        "description": "The structured data following the Perfect Template.",
                        "properties": {
                            "organ": {"type": "string"},
                            "gene": {"type": "string"},
                            "risk": {"type": "string"},
                            "why": {"type": "string", "description": "The biological reasoning or science behind the risk."},
                            "plan_a": {"type": "string"},
                            "plan_b": {"type": "string"},
                            "survival_tip": {"type": "string"},
                            "power_up": {"type": "string", "description": "An elite boost or optimization strategy."},
                            "evidence_link": {"type": "string"}
                        },
                        "required": ["organ", "gene", "risk", "why", "plan_a", "plan_b", "survival_tip", "power_up", "evidence_link"]
                    }
                },
                "required": ["category", "marker_data"]
            }
        }
    }
]

# --- Tool Implementations ---
def search_clinical_vault(query):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM markers WHERE gene LIKE ? OR trait LIKE ?", (f'%{query}%', f'%{query}%'))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return json.dumps(results) if results else "No markers found in vault."

def search_pubmed(query):
    """
    Mock PubMed search for the Hackathon PoC.
    Returns realistic abstracts for Organ Strength (Liver & Kidney).
    """
    query_lower = query.lower()
    if "liver" in query_lower or "cyp" in query_lower:
        return json.dumps({
            "title": "CYP2D6 polymorphism and liver detoxification capacity",
            "abstract": "The cytochrome P450 2D6 (CYP2D6) gene is highly polymorphic. Individuals with the *4 allele have reduced liver detoxification capacity, leading to accumulation of toxins. Plan A is to avoid environmental toxins. Plan B involves using milk thistle (silymarin) to support phase II detox. Survival Tip: Limit alcohol and processed foods.",
            "link": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
        })
    elif "kidney" in query_lower or "umod" in query_lower:
        return json.dumps({
            "title": "UMOD gene variation and chronic kidney disease risk",
            "abstract": "The UMOD gene encodes uromodulin. Genetic variants in UMOD are associated with risk of chronic kidney disease. The risk allele leads to higher uromodulin levels. Plan A is to maintain a low-sodium diet. Plan B includes high hydration protocols to reduce stone risk. Survival Tip: Drink 3L of water daily.",
            "link": "https://pubmed.ncbi.nlm.nih.gov/87654321/"
        })
    return "No relevant studies found in mock PubMed."

def scan_dna_for_gene(gene_name):
    """
    Scans the user's real DNA file for a specific gene.
    Maps gene name to RSID (Mock mapping for PoC since we don't have a full map).
    """
    gene_upper = gene_name.upper()
    rsid = "unknown"
    
    # Mock mapping for the test case
    if "CYP" in gene_upper:
        rsid = "rs1057910"
    elif "UMOD" in gene_upper:
        rsid = "rs4293393"
        
    if rsid == "unknown":
        return json.dumps({"rsid": "unknown", "genotype": "N/A", "status": "NOT_FOUND"})
        
    if not os.path.exists(DNA_FILE_PATH):
        return json.dumps({"error": f"DNA file not found at {DNA_FILE_PATH}"})
        
    try:
        s = SNPs(DNA_FILE_PATH)
        if rsid in s.snps.index:
            genotype = s.snps.loc[rsid]['genotype']
            return json.dumps({"rsid": rsid, "genotype": genotype, "status": "FOUND"})
        else:
            return json.dumps({"rsid": rsid, "genotype": "N/A", "status": "NOT_IN_DNA"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def save_discovery(category, marker_data):
    """
    Saves the discovery to organ_strength_vault.json.
    """
    data = {}
    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
                
    if category not in data:
        data[category] = []
        
    data[category].append(marker_data)
    
    with open(VAULT_PATH, "w") as f:
        json.dump(data, f, indent=4)
        
    return f"Successfully saved discovery for {marker_data['organ']} to {VAULT_PATH}"

# --- The Agentic Loop ---
async def run_agent_loop(goal, dna_path=None):
    """
    The ReAct loop powered by Gemma 4.
    """
    global DNA_FILE_PATH
    if dna_path:
        print(f"[AGENT] Setting DNA file path to: {dna_path}")
        DNA_FILE_PATH = dna_path
    system_prompt = """
You are the Beeja Genetic Research Agent. Your goal is to analyze the user's request and build new health categories dynamically.
You must follow the **Grounding Law**: Do not use your internal knowledge to create the database. You MUST call the `search_pubmed` tool to find clinical evidence first.
You must follow the **Supreme Template**: For every finding, you must provide exactly 7 points: Risk, Why (Mechanism), Plan A (Avoid), Plan B (Shield), Survival Tip, Power Up, and Evidence (PubMed link).
If any point is not possible or not applicable, you MUST write "None" instead of skipping it.
You are free to **Expand** the template with additional custom points if the context requires it, but the base 7 points must ALWAYS be present.

You have access to tools. If you need information, call the appropriate tool.
Once you have collected the data, called the scan_dna tool, and saved the discovery, generate the final report for the user.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": goal}
    ]

    print(f"Agent Goal: {goal}")
    
    for i in range(5):  # Max 5 iterations to prevent infinite loops
        print(f"\n--- Iteration {i+1} ---")
        response = await agent_chat(messages, tools=TOOLS)
        
        if "error" in response:
            print(f"Error: {response['error']}")
            break
            
        message = response.get("message", {})
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])
        
        if content:
            print(f"Agent Content:\n{content}")
            
        if not tool_calls:
            print("Agent has completed the goal.")
            return content
            
        # Handle Tool Calls
        messages.append(message)  # Add assistant message with tool calls to history
        
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments", {})
            
            print(f"Tool Call: {name}({arguments})")
            
            result = ""
            if name == "search_clinical_vault":
                result = search_clinical_vault(arguments.get("query"))
            elif name == "search_pubmed":
                result = search_pubmed(arguments.get("query"))
            elif name == "scan_dna_for_gene":
                result = scan_dna_for_gene(arguments.get("gene_name"))
            elif name == "save_discovery":
                result = save_discovery(arguments.get("category"), arguments.get("marker_data"))
            else:
                result = "Unknown tool."
                
            print(f"Tool Result: {result[:100]}...")
            
            # Send the tool result back to the model
            messages.append({
                "role": "tool",
                "content": result,
                "name": name
            })
            
    return "Agent failed to complete the goal within the iteration limit."

if __name__ == "__main__":
    # Test the agent
    async def main():
        goal = "Analyze my genetic Organ Strength for Liver and Kidney. Research PubMed if needed, scan my DNA, and save the discovery."
        
        start_time = time.time()
        result = await run_agent_loop(goal)
        end_time = time.time()
        
        print("\n=== FINAL REPORT ===")
        print(result)
        print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
        
    asyncio.run(main())

