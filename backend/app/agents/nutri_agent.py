from app.agents.base_agent import BaseAgent

class NutriAgent(BaseAgent):
    """SPECIALIST: NUTRIGENOMICS (Metabolism & Food)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        diet = context.get("diet", "Standard")
        age = context.get("age", 35)
        major = context.get("major", "NutriGenomics")
        master = context.get("master", "Metabolism & Food")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: NUTRI] {sub} Analysis for {trait} (Diet: {diet})...")
        prompt = f"""You are a Metabolic Genomics Expert. Analyze: '{trait}'.
PATIENT: Age {age}, Diet: {diet}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. If Vegan/Vegetarian, EXCLUDE animal sources.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "absorption_efficiency" (How well the patient processes this specific nutrient related to {sub}),
- "dietary_priority" (The #1 food change or supplement logic needed for {sub})"""
        
        data = await self._call_llm(prompt, "NutriAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "NutriGenomics")
        res.update({"efficiency": "Pending", "target": "Verify with labs", "recommended_sources": "Whole Foods"})
        return res
