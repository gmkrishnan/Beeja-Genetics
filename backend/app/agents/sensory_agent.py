from app.agents.base_agent import BaseAgent

class SensoryAgent(BaseAgent):
    """SPECIALIST: SENSORYGENOMICS (Vision, Hearing, Senses)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "SensoryGenomics")
        master = context.get("master", "Vision, Hearing, Senses")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: SENSORY] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Sensory Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas like kidney or cardio.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for longevity),
- "vision_longevity_plan" (Advice on retinal/nerve health related to {sub}),
- "sensory_processing_score" (0-100 score for functional sensitivity in {sub})"""
        
        data = await self._call_llm(prompt, "SensoryAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "SensoryGenomics")
        res.update({"sensory_profile": "Standard", "sensory_care_plan": "Regular sensory testing"})
        return res
