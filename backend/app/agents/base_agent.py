import httpx
import json
import asyncio
from app.core.rag import rag_anchor
from app.core.validator import clinical_validator
from app.core.research import clinical_researcher

# Optional Vector Memory (ChromaDB)
try:
    from app.core.memory import clinical_memory
except ImportError:
    clinical_memory = None

class BaseAgent:
    """
    GENEGUARDIAN NATIVE AGENT ENGINE
    Features: Gemma 4 Native Tool-Sim, RAG Context Anchoring, Self-Correction, Clinical Truth Bridge
    """
    def __init__(self, model="gemma4:e2b", timeout_standard=150.0):
        self.model = model
        self.timeout_standard = timeout_standard
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
        self.current_context = None
        
        # Monkeypatch analyze method to automatically capture the context dictionary
        original_analyze = getattr(self, "analyze", None)
        if original_analyze and not hasattr(original_analyze, "__wrapped_by_base__"):
            async def wrapped_analyze(trait, risk_tier="MODERATE", context=None):
                self.current_context = context
                return await original_analyze(trait, risk_tier, context)
            wrapped_analyze.__wrapped_by_base__ = True
            self.analyze = wrapped_analyze

    async def _call_llm(self, prompt, specialist_name="Agent"):
        # 1. RETRIEVE: Fetch RAG context for the trait
        trait_name = prompt.split("'")[1] if "'" in prompt else "DNA Trait"
        clinical_context = rag_anchor.get_context(trait_name)
        
        # Extract Gene Symbol for validation anchoring
        gene_symbol = "Pending"
        if "Gene Target:" in clinical_context:
            gene_symbol = clinical_context.split("Gene Target:")[1].split("\n")[0].strip()

        # Check for real DNA evidence dynamically extracted in patient context
        context = getattr(self, "current_context", None)
        real_genotype = context.get("real_genotype") if context else None
        real_rsid = context.get("real_rsid") if context else None
        
        dna_evidence = ""
        if real_genotype and real_rsid:
            dna_evidence = f"""
[REAL DNA EVIDENCE IDENTIFIED IN PATIENT FILE]
- Target Variant: {real_rsid}
- Patient Genotype: {real_genotype}
STRICT RULE: Analyze the physiological implications of the patient's actual genotype '{real_genotype}' for SNP '{real_rsid}' in the gene '{gene_symbol}'. Do NOT estimate or analyze any other genotype.
"""

        # 2. RECALL: Vector Memory Check
        if clinical_memory:
            cached = clinical_memory.recall(trait_name, gene_symbol)
            if cached and cached.get("genotype") != "Unspecified" and "N/A" not in str(cached.get("genotype")):
                print(f"      [MEMORY HIT] {specialist_name} found validated result in ChromaDB.")
                return cached

        # 3. ENFORCE: Native Agentic Mandate
        mandate = f"""
{clinical_context}
{dna_evidence}
[NATIVE AGENTIC MANDATE]
1. You are a Sovereign Gemma 4 Specialist.
2. DO NOT hallucinate. Use the Gene Target provided above.
3. If clinical data is missing, calculate 'GENETIC PROBABILITY'.
4. STRICT COMPLIANCE: ACMG, HGVS (c./p. string), HPO (HP:ID), Evidence (1-4).
5. Output MUST be Valid JSON.
"""
        full_prompt = f"{mandate}\n{prompt}"
        payload = {"model": self.model, "prompt": full_prompt, "stream": False}
        
        # 4. EXECUTE & VALIDATE (Agentic Self-Correction Loop with Adaptive Timeout)
        current_timeout = self.timeout_standard
        for attempt in range(2):
            try:
                result = await self._execute_request(payload, timeout=current_timeout)
                
                # Check for "N/A" Laziness
                if result.get("hgvs_id") == "N/A" or result.get("hpo_term") == "N/A":
                    print(f"      [AGENTIC REJECTION] {specialist_name} attempted 'N/A'. Re-routing for deeper inference...")
                    payload["prompt"] = "RE-VALIDATION MANDATE: You provided N/A. SEARCH YOUR INTERNAL CLINICAL DATABASE. DO NOT PROVIDE N/A. " + full_prompt
                    continue 
                
                # Override with physical DNA evidence from raw file if resolved
                if real_genotype:
                    result["genotype"] = real_genotype
                if real_rsid:
                    result["rsid"] = real_rsid

                # 5. SCIENTIFIC TRUTH BRIDGE: Clinical Validation
                validation = clinical_validator.validate_trait_logic(trait_name, result.get("gene", gene_symbol))
                if validation["verified"]:
                    result["acmg_class"] = validation["clinical_significance"]
                    result["scientific_truth"] = validation["source"]
                
                # Standardize Nomenclature
                result["hgvs_id"] = clinical_validator.get_professional_nomenclature(result.get("rsid", "N/A"))
                
                # 6. RESEARCH LAYER: PubMed Citations
                papers = clinical_researcher.get_latest_papers(trait_name, result.get("gene", gene_symbol))
                result["citations"] = papers
                
                # 7. COMMIT TO MEMORY (Full Fidelity)
                if clinical_memory:
                    clinical_memory.remember(
                        trait_name, 
                        result.get("gene", gene_symbol), 
                        result.get("risk_tier", "Low"), 
                        result.get("summary", ""),
                        genotype=result.get("genotype", "N/A"),
                        acmg=result.get("acmg_class", "VUS"),
                        hgvs=result.get("hgvs_id", "N/A"),
                        hpo=result.get("hpo_term", "N/A"),
                        evidence=result.get("evidence_level", "Lvl 3"),
                        truth=result.get("scientific_truth", "Inference"),
                        citations=result.get("citations", []),
                        clinical_plan=result.get("clinical_plan", "N/A"),
                        genetic_mechanism=result.get("genetic_mechanism", "N/A")
                    )
                
                return result
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as te:
                print(f"      [{specialist_name} Attempt {attempt+1} Timeout] Adaptive increase +120s...")
                current_timeout += 120.0 # Automatically add more time for deep specialists
                continue
            except Exception as e:
                print(f"      [{specialist_name} Attempt {attempt+1} Fail] {e}")
                if attempt == 1: return None
        return None

    async def _execute_request(self, payload, timeout):
        async with httpx.AsyncClient(timeout=timeout) as client:
            res = await client.post(self.ollama_url, json=payload)
            raw_text = res.json().get("response", "").strip()
            
            # Clinical-Grade JSON Cleaning
            if "```json" in raw_text: raw_text = raw_text.split("```json")[1].split("```")[0]
            elif "```" in raw_text: raw_text = raw_text.split("```")[1].split("```")[0]
            elif raw_text.startswith("JSON:"): raw_text = raw_text.replace("JSON:", "")
            
            return json.loads(raw_text.strip())

    def _get_fallback_base(self, trait, risk_tier, context, major_name):
        return {
            "trait": trait, "risk_tier": risk_tier, "gene": "Pending",
            "genotype": "N/A", "summary": f"Analyzing {major_name} markers for {trait}...",
            "risk_tier": risk_tier
        }
