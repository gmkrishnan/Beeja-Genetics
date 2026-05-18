from app.agents.base_agent import BaseAgent

class RenalAgent(BaseAgent):
    """SPECIALIST: RENALGENOMICS (Kidney & Filtration)"""
    
    async def analyze(self, trait: str, risk_tier: str = "MODERATE", context: dict = None):
        age = context.get("age", 35)
        major = context.get("major", "RenalGenomics")
        master = context.get("master", "Kidney & Filtration")
        sub = context.get("sub", "Analysis")
        
        print(f"    [AGENT: RENAL] {sub} Analysis for {trait} (Age: {age})...")
        prompt = f"""You are a Renal Genetics Specialist. Analyze: '{trait}'.
PATIENT: Age {age}.
HIERARCHY CONTEXT: Pillar: {major} -> Category: {master} -> Focus: {sub}.
STRICT RULE: Focus EXCLUSIVELY on the '{sub}' domain. Do not bleed into other medical areas like vision or skin.

Return JSON ONLY:
- "gene", "genotype", "summary", "risk_tier",
- "genetic_mechanism" (How this gene impacts {sub} at a cellular level),
- "clinical_plan" (Professional next steps for a physician),
- "filtration_efficiency" (Advice on glomerular health related to {sub}),
- "kidney_metabolic_load" (Specific renal protective protocol for {sub})"""
        
        data = await self._call_llm(prompt, "RenalAgent")
        return data if data else self._get_fallback(trait, risk_tier, context)

    def _get_fallback(self, trait, risk_tier, context):
        res = self._get_fallback_base(trait, risk_tier, context, "RenalGenomics")
        res.update({"renal_efficiency": "Standard", "hydration_protocol": "Monitor sodium-to-water ratio"})
        return res
