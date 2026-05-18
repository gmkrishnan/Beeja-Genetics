from app.agents.base_agent import BaseAgent

class ImmuAgent(BaseAgent):
    """SPECIALIST: IMMUGENOMICS (Immunity & Disease Defense)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "ImmuGenomics")
        master = context.get("master", "Immunity & Disease Defense")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: IMMU] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are an Immunogenetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "inflammatory_baseline" (Your genetic inflammation level related to {sub}),
- "autoimmune_watch_markers" (Specific markers to monitor for {sub})"""
        
        data = await self._call_llm(prompt, "ImmuAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "ImmuGenomics")
        res.update({"defense_status": "Standard", "protective_actions": "Anti-inflammatory diet"})
        return res
