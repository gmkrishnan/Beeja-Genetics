from app.agents.base_agent import BaseAgent

class CardioAgent(BaseAgent):
    """SPECIALIST: CARDIOGENOMICS (Heart & Lungs)"""
    def __init__(self, **kwargs):
        super().__init__(timeout_standard=240.0, **kwargs)
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "CardioGenomics")
        master = context.get("master", "Heart & Lungs")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: CARDIO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Cardiovascular Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other cardiovascular areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a physician),
- "arterial_health_focus" (Advice on plaque risk or arterial stiffness related to {sub}),
- "cardio_recovery_zone" (Ideal heart rate or recovery protocol for {sub})"""
        
        data = await self._call_llm(prompt, "CardioAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "CardioGenomics")
        res.update({"heart_profile": "Standard", "cardio_protocols": "Zone 2 Training"})
        return res
