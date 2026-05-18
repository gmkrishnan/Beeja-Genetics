from app.agents.base_agent import BaseAgent

class BioAgent(BaseAgent):
    """SPECIALIST: BIOGENOMICS (Foundational DNA)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "BioGenomics")
        master = context.get("master", "Foundational DNA")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: BIO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Foundational Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into specific medical areas like heart or cancer unless relevant.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "biological_age_impact" (Advice on cellular aging related to {sub}),
- "core_vitality_summary" (Impact on general foundational health in {sub})"""
        
        data = await self._call_llm(prompt, "BioAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "BioGenomics")
        res.update({"genomic_foundation": "Standard", "biological_logic": "Core DNA marker"})
        return res
