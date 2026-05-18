import httpx
import json

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma4:e2b" # Updated to match local installation

async def generate_dietary_report(user_profile, analysis_results, config=None, evidence_vault=None, medicine_alerts=None):
    """
    Sends the genetic analysis and user profile to local Gemma 4 via Ollama.
    Config allows toggling sections like 'explanation', 'meals', etc.
    Evidence vault provides scientific citations for markers.
    """
    if config is None:
        config = {"show_explanations": True, "show_meals": True}
    if evidence_vault is None:
        evidence_vault = {}
    
    medicine_str = ""
    if medicine_alerts:
        medicine_str = "\n### 🛡️ CRITICAL MEDICINE SAFETY ALERTS (PGx)\n"
        medicine_str += "The DNA shows significant metabolism issues for these medications:\n"
        for m in medicine_alerts:
            mitigation_info = ""
            if m.get("mitigation"):
                mitigation_info = f" (MITIGATION [{m['mitigation_type']}]: {m['mitigation']}"
                if m.get("mitigation_link") and m["mitigation_link"] != "None":
                    mitigation_info += f" PROOF: {m['mitigation_link']}"
                mitigation_info += ")"
            medicine_str += f"- {m['drug_name']} ({m['risk_level']}): {m['recommendation']} (REASON: {m['why']}){mitigation_info}\n"
        medicine_str += "\n"

    # 1. Build the Findings string by Tier
    findings_str = ""
    for tier, items in analysis_results.items():
        if not items: continue
        findings_str += f"\n### TIER: {tier.replace('_', ' ')}\n"
        for item in items:
            rsid = item['rsid']
            evidence_str = ""
            if rsid in evidence_vault:
                papers = evidence_vault[rsid]
                if isinstance(papers, list):
                    evidence_str = " | RESEARCH CITATIONS: " + "; ".join([f"{p['title']} - Summary: {p.get('ai_summary', 'View link for details.')} - Link: {p['link']}" for p in papers])
            
            mitigation_str = ""
            if item.get("mitigation"):
                mitigation_str = f" | MITIGATION ({item['mitigation_type']}): {item['mitigation']}"
                if item.get("mitigation_link") and item["mitigation_link"] != "None":
                    mitigation_str += f" | MITIGATION PROOF: {item['mitigation_link']}"
            
            findings_str += f"- {item['trait'].upper()} ({item['gene']}): Risk Level: {item['risk_tier']} | Predisposition: {item['predisposition_pct']}% | Multiplier: {item['multiplier']}x higher than average. Status: {item['door_status']}. Protocol: {item['protocol']}{mitigation_str}{evidence_str}\n"

    # 2. Construct Dynamic Prompt based on Config
    explanation_instruction = ""
    if config.get("show_explanations"):
        explanation_instruction = """
- PROVIDE BIOLOGICAL REASONING: For every finding, explain the scientific mechanism of the gene. 
- NUTRIENT LOGIC: Explain exactly WHY a food is suggested or avoided.
- MITIGATION STRATEGY: For every risk, include a separate bullet point titled '🔄 Mitigation Strategy (Plan B)' that explains what the user can do if the primary avoidance protocol is not possible.
- 🏋️ FITNESS GENOMICS: Provide the 5 Strategic Pillars, Dynamic Workout Split, and a 7-day Genetic Calendar (English/Sanskrit).
- 🛡️ ENVIRONMENTAL SURVIVAL SHIELD: For the Environmental markers, provide a section titled '🛡️ THE ENVIRONMENTAL SURVIVAL SHIELD'. For every risk, explain 'The Why (Science)', 'Plan A (Avoid)', 'Plan B (Protective Shield)', and a 'Survival Tip' with the PubMed link.
- PRENATAL GUARDIAN: If is_pregnant is True, provide a safety warning first, then focus on 'Mother & Baby' development and 'Shanti' (calming) activities.
- CITATIONS: You MUST include the Research Citations provided in the findings string.
"""
    else:
        explanation_instruction = "- BE CONCISE: Provide only the lists of risks, foods to take/avoid, and plans. Do not provide scientific explanations or paragraphs."

    system_prompt = f"""
You are GeneGuardian, a world-class clinical geneticist, performance coach, and environmental health specialist. 
Your goal is to provide safe, actionable, and hyper-personalized advice based on the user's genetic "Open Doors" across Nutrition, Medicine, Fitness, and Environmental Resilience.

USER PROFILE:
- Age: {user_profile['age']}
- Gender: {user_profile['gender']}
- Location: {user_profile['country']}
- Diet Preference: {user_profile['diet_type']}
- Health Goal: {user_profile['goal']}
- Pregnancy Status: {user_profile.get('is_pregnant', False)} (Only relevant for females 18+)

GENETIC REALITY (The Open Doors):
{findings_str}

{medicine_str}

STRICT OUTPUT GUIDELINES:
{explanation_instruction}

STRICT OUTPUT FORMAT:
You MUST format your response into these sections:
1. ### THE GENETIC RISK PROFILE (THE WHY)
2. ### THE NUTRITIONAL PROTOCOL (WHAT TO TAKE / AVOID)
3. ### THE ACTIONABLE FOOD PLAN
4. ### SCIENTIFIC REFERENCES (List all research links here)

Do not include any introductory fluff. Start directly with Section 1.
"""

    # 3. Prepare the Ollama Request
    payload = {
        "model": MODEL_NAME,
        "prompt": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 8192,  # Substantially increased to support full, multi-pillar reports
            "num_ctx": 16384      # Increased context window for comprehensive analysis
        }
    }

    # 4. Communicate with Ollama
    try:
        async with httpx.AsyncClient(timeout=3600.0) as client:
            response = await client.post(OLLAMA_API_URL, json=payload)
            print(f"DEBUG: Ollama Status: {response.status_code}")
            if response.status_code != 200:
                print(f"DEBUG: Response Text: {response.text}")
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "Error: No response from Gemma.")
            
    except httpx.ConnectError:
        return "Error: Could not connect to Ollama. Ensure Ollama is running locally at http://localhost:11434"
    except Exception as e:
        print(f"DEBUG ERROR: {type(e).__name__}: {str(e)}")
        return f"Error: An unexpected error occurred: {str(e)}"

async def summarize_research(abstract_text):
    """
    Uses Gemma 4 to extract 'Hard Numbers' (Participants, % risk reduction, etc.) 
    and a one-sentence summary from a scientific abstract.
    """
    if not abstract_text or len(abstract_text) < 50:
        return "Significance: Study confirms genetic association. (Full abstract unavailable for analysis)."

    prompt = f"""
Analyze this research abstract and give me:
1. Number of participants (if mentioned).
2. The primary statistical finding (e.g. 20% risk increase).
3. The main recommendation for diet.

ABSTRACT:
{abstract_text}

Provide the answer in 2 short sentences.
"""
    # 3. Call local Ollama API
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 300,
            "temperature": 0.1
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(OLLAMA_API_URL, json=payload)
            if response.status_code == 200:
                summary = response.json().get("response", "").strip()
                if summary:
                    return summary
    except Exception as e:
        print(f"DEBUG SUMMARY ERROR: {str(e)}")
    
    # Fallback: Just return a snippet of the abstract if AI fails
    return f"Data Insight: {abstract_text[:200]}..."

async def agent_chat(messages, tools=None):
    """
    Sends a chat history and optional tools to local Gemma 4 via Ollama /api/chat.
    Supports Native Function Calling.
    """
    url = "http://127.0.0.1:11434/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low temperature for precise tool calling
            "num_predict": 2048,
            "num_ctx": 8192
        }
    }
    if tools:
        payload["tools"] = tools
        
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                print(f"DEBUG: Agent Chat Status: {response.status_code}")
                print(f"DEBUG: Response Text: {response.text}")
            response.raise_for_status()
            
            return response.json()
            
    except Exception as e:
        print(f"DEBUG AGENT CHAT ERROR: {str(e)}")
        return {"error": str(e)}

