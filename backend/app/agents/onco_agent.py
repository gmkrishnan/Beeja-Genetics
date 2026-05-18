from app.agents.base_agent import BaseAgent

class OncoAgent(BaseAgent):
    """SPECIALIST: ONCOGENOMICS (Cancer Risk & Cell Integrity)"""
    def __init__(self, **kwargs):
        super().__init__(timeout_standard=240.0, **kwargs)
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "OncoGenomics")
        master = context.get("master", "Cancer Risk & Cell Integrity")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: ONCO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are an Oncology Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other oncology or medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a physician),
- "screening_advice" (Specific medical tests and frequency related to {sub}),
- "prevention_protocol" (Lifestyle changes to protect cell integrity in {sub})"""
        
        data = await self._call_llm(prompt, "OncoAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "OncoGenomics")
        res.update({"risk_status": "Standard", "prevention_protocol": "Annual clinical screening"})
        return res
