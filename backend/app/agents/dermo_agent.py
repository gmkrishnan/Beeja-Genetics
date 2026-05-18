from app.agents.base_agent import BaseAgent

class DermoAgent(BaseAgent):
    """SPECIALIST: DERMOGENOMICS (Skin & Aging)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "DermoGenomics")
        master = context.get("master", "Skin & Aging")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: DERMO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Dermatological Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other dermatology or medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a clinician),
- "collagen_integrity" (Advice on elasticity and structural aging related to {sub}),
- "photo_protection_need" (Specific UV and environmental protection for {sub})"""
        
        data = await self._call_llm(prompt, "DermoAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "DermoGenomics")
        res.update({"skin_type": "Standard", "dermo_routine": "Sun protection + Vitamin C"})
        return res
