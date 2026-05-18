import sqlite3
import os
import json
import httpx

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:e2b"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'registry', 'clinical_vault.db')
CACHE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'registry', 'category_cache.json')

async def gemma_plan_category(category_name):
    """
    Acts as the Thinker. Asks Gemma 4 to select traits from the DB that belong to the category.
    Returns a list of trait names.
    """
    # 1. Load cache
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            try:
                cache = json.load(f)
            except:
                cache = {}
            if category_name.lower() in cache:
                print(f"[Planner] Cache hit for '{category_name}'")
                return cache[category_name.lower()]
                
    print(f"[Planner] Cache miss for '{category_name}'. Waking up Gemma 4...")
    
    # 2. Get all existing traits
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT trait FROM markers")
    all_traits = [r[0] for r in c.fetchall()]
    conn.close()
    
    prompt = f"""
You are GeneGuardian, a world-class clinical geneticist and performance planner.
The user wants to extract genetic traits relevant to the category: "{category_name}".

I am providing you with a list of all available traits currently indexed in our clinical database:
{json.dumps(all_traits)}

CRITICAL INSTRUCTIONS:
1. You MUST select traits from the provided list that are biologically relevant to "{category_name}".
2. Do NOT return generic words like "traits", "genes", "all", "result", or "output".
3. If you cannot find any relevant traits in the provided list, you MUST suggest 3 brand new, scientifically valid trait names that are highly relevant to "{category_name}" (e.g., if category is Fitness, suggest "Vascular Elasticity", "Mitochondrial Biogenesis", etc.).
4. Do not leave the list empty. Do not return anything other than the JSON array.

STRICT OUTPUT FORMAT:
You MUST return ONLY a valid JSON array of strings. Do not include any conversational filler, markdown formatting (no ```json blocks), or explanations.
Example output:
["Muscle Identity (Power vs Endurance)", "Aerobic Trainability", "Recovery Clock (Lactic Acid)"]
"""
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            result = response.json()["response"]
            
            try:
                selected_traits = json.loads(result)
                # Fallback check to prevent bad LLM outputs
                bad_words = ["result", "results", "output", "suggestions", "traits", "genes", "all", "here"]
                if not isinstance(selected_traits, list) or len(selected_traits) == 0:
                    selected_traits = [f"{category_name.title()} Sensitivity", f"{category_name.title()} Response"]
                else:
                    cleaned = []
                    for t in selected_traits:
                        if isinstance(t, str) and len(t) > 3 and t.lower() not in bad_words:
                            cleaned.append(t)
                    if len(cleaned) == 0:
                        selected_traits = [f"{category_name.title()} Sensitivity", f"{category_name.title()} Response"]
                    else:
                        selected_traits = cleaned
            except json.JSONDecodeError:
                print(f"[Planner] Failed to parse JSON from Gemma: {result}")
                selected_traits = [f"{category_name.title()} Sensitivity", f"{category_name.title()} Response"]
                
            # Save to cache
            cache = {}
            if os.path.exists(CACHE_PATH):
                with open(CACHE_PATH, 'r') as f:
                    try:
                        cache = json.load(f)
                    except:
                        pass
            cache[category_name.lower()] = selected_traits
            with open(CACHE_PATH, 'w') as f:
                json.dump(cache, f, indent=4)
                
            print(f"[Planner] Mapped '{category_name}' to {len(selected_traits)} traits.")
            return selected_traits
            
    except Exception as e:
        print(f"[Planner] Error connecting to Ollama: {e}")
        return []
