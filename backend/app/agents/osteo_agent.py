from app.agents.base_agent import BaseAgent

class OsteoAgent(BaseAgent):
    """SPECIALIST: OSTEOGENOMICS (Bones & Skeletal)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "OsteoGenomics")
        master = context.get("master", "Skeletal Physiology")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: OSTEO] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Skeletal Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps),
- "bone_density_support" (Advice on mineral density related to {sub}),
- "ligament_integrity" (Structural remodeling advice for {sub})"""
        
        data = await self._call_llm(prompt, "OsteoAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "OsteoGenomics")
        res.update({"bone_density": "Standard", "osteo_drills": "Resistance training"})
        return res
