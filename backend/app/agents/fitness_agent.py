from app.agents.base_agent import BaseAgent

class FitnessAgent(BaseAgent):
    """SPECIALIST: FITNESSGENOMICS (Performance & Power)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "FitnessGenomics")
        master = context.get("master", "Performance")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: FITNESS] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Sports Genetics Expert. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other fitness areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a coach or physician),
- "training_protocol" (Zone/Resistance advice specific to {sub}),
- "athletic_recovery" (Rest requirements specific to {sub}),
- "power_score" (0-100)"""
        
        data = await self._call_llm(prompt, "FitnessAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "FitnessGenomics")
        res.update({"profile": "Standard", "power_score": 50, "training_protocol": "Balanced Training"})
        return res
