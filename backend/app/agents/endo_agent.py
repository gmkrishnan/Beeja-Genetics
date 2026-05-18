from app.agents.base_agent import BaseAgent

class EndoAgent(BaseAgent):
    """SPECIALIST: ENDOGENOMICS (Hormones & Glands)"""
    def __init__(self, **kwargs):
        super().__init__(timeout_standard=240.0, **kwargs)
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "EndoGenomics")
        master = context.get("master", "Hormones & Glands")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: ENDO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are an Endocrine Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other endocrine areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a physician),
- "hormone_balance_logic" (Advice on hormone production related to {sub}),
- "glandular_support_plan" (Specific glandular support for {sub})"""
        
        data = await self._call_llm(prompt, "EndoAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "EndoGenomics")
        res.update({"hormone_profile": "Standard", "endo_protocol": "Verify with hormone panel"})
        return res
