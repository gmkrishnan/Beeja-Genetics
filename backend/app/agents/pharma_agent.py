from app.agents.base_agent import BaseAgent

class PharmaAgent(BaseAgent):
    """SPECIALIST: PHARMAGENOMICS (Medication Safety)"""
    def __init__(self, **kwargs):
        super().__init__(timeout_standard=240.0, **kwargs)
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "PharmaGenomics")
        master = context.get("master", "Medication Safety")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: PHARMA] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Clinical Pharmacogenomics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}, Gender {context.get('gender', 'N/A')}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Follow CPIC Level 1A guidelines.

Return JSON ONLY:
- "gene", "genotype", "phenotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} drug metabolism),
- "clinical_plan" (Professional next steps for a prescribing physician),
- "dosing_logic" (Dosing modifications specific to {sub}),
- "interaction_risk" (Metabolic interaction risks specific to {sub})"""
        
        data = await self._call_llm(prompt, "PharmaAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "PharmaGenomics")
        res.update({"phenotype": "Pending", "activity_score": "N/A", "dosing_recommendation": "Consult Specialist"})
        return res
