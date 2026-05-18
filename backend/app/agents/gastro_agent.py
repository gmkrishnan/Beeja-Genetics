from app.agents.base_agent import BaseAgent

class GastroAgent(BaseAgent):
    """SPECIALIST: GASTROGENOMICS (Gut & Digestion)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "GastroGenomics")
        master = context.get("master", "Gut & Digestion")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: GASTRO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Gastroenterological Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "gut_barrier_strength" (Advice on intestinal integrity related to {sub}),
- "digestive_enzyme_logic" (Enzyme support or digestive tempo for {sub})"""
        
        data = await self._call_llm(prompt, "GastroAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "GastroGenomics")
        res.update({"digestive_efficiency": "Standard", "gut_protocol": "Increase fiber intake"})
        return res
