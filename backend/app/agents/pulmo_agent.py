from app.agents.base_agent import BaseAgent

class PulmoAgent(BaseAgent):
    """SPECIALIST: PULMOGENOMICS (Respiratory System)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "PulmoGenomics")
        master = context.get("master", "Respiratory System")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: PULMO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Pulmonary Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "lung_capacity_focus" (Advice on respiratory volume and health related to {sub}),
- "oxygen_exchange_efficiency" (Efficiency of O2/CO2 transfer in {sub})"""
        
        data = await self._call_llm(prompt, "PulmoAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "PulmoGenomics")
        res.update({"lung_profile": "Standard", "breathing_exercises": "Diaphragmatic breathing"})
        return res
