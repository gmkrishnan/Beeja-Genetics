import json
import os
from typing import List, Dict
from app.core.gemma import agent_chat
from app.agents.base_agent import clinical_memory

class BeejaHelix:
    """
    ENGINE: Beeja Helix - Proactive Conversational Analyst.
    Connects the 15-Specialist Swarm to a RAG-based chat interface.
    """
    def __init__(self, swarm: Dict):
        self.swarm = swarm
        self.traits_db = self._load_traits()
        self.master_traits = self._load_master_traits()
        self._dna_cache = {}
        
    def _load_traits(self):
        try:
            with open("registry/clinical_vault.json", "r") as f:
                return json.load(f)
        except:
            return []

    def _load_master_traits(self):
        try:
            with open("registry/all_unique_traits.json", "r") as f:
                data = json.load(f)
                # Convert dict keys to a list of dicts for search compatibility
                return [{"name": k, "gene": v.get("representative_gene", "Unknown"), "major": "ResearchGenomics"} for k, v in data.items()]
        except:
            return []

    def _scan_gene_snps(self, gene_symbol: str, file_path: str):
        # Preset database of common high-value research genes and coordinates (GRCh37/hg19)
        boundaries = {
            "DPP4": {"chrom": "2", "start": 162842689, "end": 162925584},
            "VDR": {"chrom": "12", "start": 48228310, "end": 48298879},
            "COL1A1": {"chrom": "17", "start": 48261459, "end": 48284000},
            "APOE": {"chrom": "19", "start": 45409039, "end": 45412650},
            "MTHFR": {"chrom": "1", "start": 11847566, "end": 11867000},
            "COMT": {"chrom": "22", "start": 19929039, "end": 19956000},
            "BDNF": {"chrom": "11", "start": 27676039, "end": 27744000},
            "CLOCK": {"chrom": "4", "start": 85920000, "end": 86050000},
            "APOA5": {"chrom": "11", "start": 116650000, "end": 116670000}
        }
        
        boundary = boundaries.get(gene_symbol.upper())
        if not boundary: return None, None
        
        try:
            from snps import SNPs
            if file_path not in self._dna_cache:
                self._dna_cache[file_path] = SNPs(file_path)
            
            s = self._dna_cache[file_path]
            chrom = boundary["chrom"]
            start = boundary["start"]
            end = boundary["end"]
            
            # Filter SNPs
            chr_snps = s.snps[s.snps['chrom'] == chrom]
            matches = chr_snps[(chr_snps['pos'] >= start) & (chr_snps['pos'] <= end)]
            
            if not matches.empty:
                for rsid, row in matches.iterrows():
                    genotype = row['genotype']
                    if genotype and "N/A" not in str(genotype) and genotype != "--":
                        return f"{rsid} ({genotype})", rsid
        except Exception as e:
            print(f"Gene boundary scan failed: {e}")
            
        return None, None

    async def _map_query_to_trait(self, query: str) -> List[str]:
        """
        Uses Gemma to map a natural language question to a prioritized list of Direct and Surrogate traits.
        Falls back to instant local keyword matching to bypass LLM latency and avoid timeouts.
        """
        query_lower = query.lower()
        
        # 1. INSTANT LOCAL KEYWORD PRE-MAPPING (Fast Path & Robust Fallback)
        keywords = {
            "sleep": ["Sleep latency", "Sleep duration", "Sleep (number of episodes)"],
            "asleep": ["Sleep latency", "Sleep duration"],
            "insomnia": ["Sleep latency", "Sleep duration"],
            "learning": ["Cognitive processing speed", "Inhibitory control"],
            "style": ["Cognitive processing speed"],
            "cognitive": ["Cognitive processing speed", "Inhibitory control"],
            "brain": ["Cognitive processing speed", "Inhibitory control"],
            "heart": ["Coronary artery disease", "Resting heart rate", "Heart rate response to recovery post exercise"],
            "cardio": ["Coronary artery disease", "Resting heart rate"],
            "coronary": ["Coronary artery disease"],
            "bone": ["Bone mineral density change response to combined chemotherapy in acute lymphoblastic leukemia", "Femoral neck bone mineral density", "Lumbar spine bone mineral density"],
            "weak": ["Bone mineral density change response to combined chemotherapy in acute lymphoblastic leukemia", "Femoral neck bone mineral density"],
            "osteology": ["Femoral neck bone mineral density", "Lumbar spine bone mineral density"],
            "osteoporosis": ["Femoral neck bone mineral density", "Lumbar spine bone mineral density"],
            "vitamin d": ["Vitamin D levels", "Calcium metabolism"],
            "calcium": ["Calcium metabolism"],
            "pgx": ["Response to mepolizumab in severe asthma"],
            "medication": ["Response to mepolizumab in severe asthma"]
        }
        
        local_matches = []
        for kw, traits in keywords.items():
            if kw in query_lower:
                for t in traits:
                    if t not in local_matches:
                        local_matches.append(t)
                        
        if local_matches:
            return local_matches[:3]
            
        prompt = f"""You are a Genomic Mapping Specialist. The user asked: '{query}'.
Your task is to identify 3 potential genetic markers to investigate, following this hierarchy:
1. DIRECT: The exact trait mentioned.
2. SURROGATE A: The most direct biological proxy.
3. SURROGATE B: A secondary metabolic proxy.

Return ONLY a comma-separated list of the 3 most relevant trait names.
Final Answer format: Trait 1, Trait 2, Trait 3"""
        
        messages = [{"role": "user", "content": prompt}]
        data = await agent_chat(messages)
        content = data.get("message", {}).get("content", "")
        if not content: return ["Genetics | General"]
        
        return [t.strip() for t in content.split(",") if t.strip()]

    def _get_specialist_key(self, trait: dict) -> str:
        trait_name = trait.get("name", "").lower()
        major = trait.get("major", "BioGenomics").lower()
        master = trait.get("master", "Clinical").lower()
        
        if "pharma" in major: return "Pharma"
        elif "onco" in major or "cancer" in trait_name: return "Onco"
        elif "sensory" in major or any(k in trait_name for k in ["eye", "vision", "ear", "hearing"]): return "Sensory"
        elif "gastro" in major or "digestive" in trait_name: return "Gastro"
        elif "pulmo" in major or "respiratory" in master: return "Pulmo"
        elif "renal" in major or "kidney" in trait_name: return "Renal"
        elif master in ["metabolism", "metabolic", "nutrition", "biochemistry"]: return "Nutri"
        elif master in ["psychiatry", "cognitive", "behavior", "sleep"]: return "Neuro"
        elif master in ["immunology", "hematology", "oncology", "disease", "medical", "health"]: return "Immu"
        elif master in ["cardiology", "cardiovascular"]: return "Cardio"
        elif master in ["morphology", "physical", "sensory"]: return "Dermo"
        elif master in ["endocrine"]: return "Endo"
        elif master in ["skeletal system", "musculoskeletal"]: return "Osteo"
        elif master in ["physiology", "physiological", "fitness"]: return "Fitness"
        elif master in ["genetics", "quantitative genetics", "biology", "biological", "anthropometry", "anatomy"]: return "Bio"
        return "Bio"

    def find_relevant_traits(self, trait_name: str) -> List[Dict]:
        query_lower = trait_name.lower()
        results = []
        
        # 1. Search Clinical Vault (High Fidelity) - Fix trait vs name key mismatch
        for trait in self.traits_db:
            name = trait.get("trait", trait.get("name", ""))
            if name and query_lower in name.lower():
                results.append({
                    "name": name,
                    "gene": trait.get("gene", "Unknown"),
                    "major": trait.get("major", "BioGenomics"),
                    "master": trait.get("master", "Clinical"),
                    "sub": trait.get("sub", "Analysis")
                })
            if len(results) >= 1: break
            
        # 2. Search Master Traits (Research Grade - 47k list)
        if not results:
            for trait in self.master_traits:
                name = trait.get("name", "")
                if name and query_lower in name.lower():
                    results.append({
                        "name": name,
                        "gene": trait.get("gene", "Unknown"),
                        "major": trait.get("major", "ResearchGenomics"),
                        "master": trait.get("master", "Clinical"),
                        "sub": trait.get("sub", "Analysis")
                    })
                if len(results) >= 1: break
                
        return results

    async def generate_response(self, query: str, mode: str = "supportive", patient_context: dict = None, file_path: str = None):
        """
        The main chat logic with Dynamic Gene Boundary Scanning and Surrogate Fallback.
        """
        logs = ["📡 Analyzing your question with Beeja Helix..."]
        
        # Resolve path to absolute raw DNA data directory if standard path is missing
        if not file_path or not os.path.exists(file_path):
            file_path = "D:\\Building\\beeja\\Beeja_Genetic\\raw_data\\genome_James_Jones_v5_Full_20230726173828\\genome_James_Jones_v5_Full_20230726173828.txt"
        
        # 1. AI-DRIVEN MULTI-MAPPING
        suggested_traits = await self._map_query_to_trait(query)
        logs.append(f"🧠 Suggested Path: {', '.join(suggested_traits)}")
        
        # 2. SEARCH FOR DATA (Iterate through suggestions until we find one in the file)
        analysis_data = []
        found_marker = False
        final_relevant_traits = []

        for target in suggested_traits:
            relevant_traits = self.find_relevant_traits(target)
            if not relevant_traits: continue

            for trait in relevant_traits:
                trait_name = trait["name"]
                gene_symbol = trait.get("gene", "Unknown")
                
                # Check Memory or Analyze
                cached = clinical_memory.recall(trait_name, gene_symbol)
                if cached and cached.get("genotype") != "Unspecified" and "N/A" not in str(cached.get("genotype")):
                    logs.append(f"📦 Found cached DNA data for '{trait_name}'.")
                    analysis_data.append(cached)
                    found_marker = True
                    final_relevant_traits = relevant_traits
                    break
                else:
                    logs.append(f"🔍 Checking '{trait_name}' in your DNA file...")
                    
                    # Try to scan the physical DNA file dynamically for the target gene boundary
                    real_genotype = None
                    real_rsid = None
                    if file_path and os.path.exists(file_path) and gene_symbol != "Unknown":
                        real_genotype, real_rsid = self._scan_gene_snps(gene_symbol, file_path)
                        if real_genotype:
                            logs.append(f"🧬 Precision Match! Located variant {real_rsid} ({real_genotype}) on target gene {gene_symbol} in your file.")
                    
                    specialist_key = self._get_specialist_key(trait)
                    
                    agent = self.swarm.get(specialist_key, self.swarm.get("Bio"))
                    
                    # Assemble dynamic patient context
                    p_ctx = dict(patient_context) if patient_context else {}
                    p_ctx.update({
                        "age": p_ctx.get("age", 35),
                        "major": trait.get("major", "BioGenomics"),
                        "master": trait.get("master", "Clinical"),
                        "sub": trait.get("sub", "Analysis")
                    })
                    if real_genotype:
                        p_ctx["real_genotype"] = real_genotype
                        p_ctx["real_rsid"] = real_rsid
                    
                    data = await agent.analyze(trait_name, context=p_ctx)
                    
                    if data and "summary" in data:
                        if data.get("genotype") != "Unspecified" and "N/A" not in str(data.get("genotype")):
                            logs.append(f"✅ Hit! Found DNA evidence for '{trait_name}'.")
                        else:
                            logs.append(f"💡 Swarm Agent Inference: Utilizing surrogate clinical logic for '{trait_name}'.")
                        
                        analysis_data.append(data)
                        found_marker = True
                        final_relevant_traits = relevant_traits
                        break
            
            if found_marker: break # Stop once we have a solid finding

        if not found_marker:
            return {
                "answer": f"RESULT: DATA GAP. I searched for {', '.join(suggested_traits)} but found no markers in your file. Please upload a Whole Genome Sequencing (WGS) file.",
                "logs": logs + ["⚠️ No markers found in primary or surrogate search."]
            }

        # 3. ANALYZE (Hierarchy: Direct -> Surrogate -> Stop)
        analysis_data = []
        for trait in final_relevant_traits:
            trait_name = trait["name"]
            gene_symbol = trait.get("gene", "Unknown")
            
            # Check Memory
            cached = clinical_memory.recall(trait_name, gene_symbol)
            if cached and cached.get("genotype") != "Unspecified" and "N/A" not in str(cached.get("genotype")):
                logs.append(f"📦 Recalling validated DNA data for '{trait_name}'.")
                analysis_data.append(cached)
            else:
                logs.append(f"🧠 Scanning for Direct or Surrogate markers for '{trait_name}'...")
                
                real_genotype = None
                real_rsid = None
                if file_path and os.path.exists(file_path) and gene_symbol != "Unknown":
                    real_genotype, real_rsid = self._scan_gene_snps(gene_symbol, file_path)
                
                specialist_key = self._get_specialist_key(trait)
                
                agent = self.swarm.get(specialist_key, self.swarm.get("Bio"))
                
                p_ctx = dict(patient_context) if patient_context else {}
                p_ctx.update({
                    "age": p_ctx.get("age", 35),
                    "major": trait.get("major", "BioGenomics"),
                    "master": trait.get("master", "Clinical"),
                    "sub": trait.get("sub", "Analysis")
                })
                if real_genotype:
                    p_ctx["real_genotype"] = real_genotype
                    p_ctx["real_rsid"] = real_rsid
                
                data = await agent.analyze(trait_name, context=p_ctx)
                analysis_data.append(data)

        # 4. STRUCTURED CLINICAL SYNTHESIS (Non-Markdown)
        results_str = ""
        for d in analysis_data:
            results_str += f"\n[GENE: {d.get('gene', 'Unknown')}] | [TRAIT: {d.get('trait')}] | [RESULT: {d.get('genotype', 'Data Missing')}]\n"
            results_str += f"ANALYSIS: {d.get('genetic_mechanism', 'No genomic mechanism identified in current file.')}\n"
            results_str += f"PLAN: {d.get('clinical_plan', 'WGS recommended for further insight.')}\n"
            results_str += "-" * 50

        # Use Gemma to polish this into the strict Structured Format
        prompt = f"""You are 'Beeja Helix', a clinical DNA analyst. 
STRICT RULE: ONLY use the DNA data provided. Do NOT give general life advice.
If data is missing, state 'RESULT: DATA GAP'.

DNA DATA:
{results_str}

USER QUESTION: '{query}'

FORMAT YOUR ANSWER AS FOLLOWS (NO MARKDOWN):
GENOMIC ANCHOR: [Gene Name]
CLINICAL STATUS: [Specific DNA finding]
SURROGATE LOGIC: [Mention if surrogate was used or if direct marker was found]
ACTIONABLE STEP: [Specific DNA-tailored plan]
DATA COVERAGE: [SNP-level or WGS Recommendation]"""
        
        messages = [{"role": "user", "content": prompt}]
        data = await agent_chat(messages)
        final_answer = data.get("message", {}).get("content", "Error synthesizing results.")
        
        if "data gap" in final_answer.lower():
            final_answer = "RESULT: DATA GAP. Your DNA file does not contain the markers required for this analysis. Please upload a Whole Genome Sequencing (WGS) file."

        return {
            "answer": final_answer,
            "logs": logs + ["✅ Sovereign Analysis Complete."]
        }
