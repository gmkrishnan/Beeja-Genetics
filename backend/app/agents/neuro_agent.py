from app.agents.base_agent import BaseAgent

class NeuroAgent(BaseAgent):
    """SPECIALIST: NEUROGENOMICS (Brain, Focus, Sleep)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "NeuroGenomics")
        master = context.get("master", "Brain, Focus, Sleep")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: NEURO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a NeuroGenetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for cognitive health),
- "cognitive_focus" (Advice on memory or focus related to {sub}),
- "sleep_architecture_impact" (Specific sleep logic related to {sub})"""
        
        data = await self._call_llm(prompt, "NeuroAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "NeuroGenomics")
        res.update({"cognitive_profile": "Standard", "focus_drills": "Mindfulness"})
        return res
