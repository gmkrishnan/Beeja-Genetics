import json
import difflib

class RAGEngine:
    """
    SOVEREIGN RAG ENGINE: The Source of Truth Anchor.
    Ensures agents are fed factual context before inference.
    """
    def __init__(self, vault_path="registry/clinical_vault.json"):
        with open(vault_path, "r") as f:
            self.vault = json.load(f)

    def get_context(self, trait_query):
        # Semantic Search: Find the most relevant clinical record
        traits = [v['trait'] for v in self.vault]
        matches = difflib.get_close_matches(trait_query, traits, n=1, cutoff=0.3)
        
        if matches:
            record = next(v for v in self.vault if v['trait'] == matches[0])
            return f"""
[CLINICAL CONTEXT - VERIFIED SOURCE]
Trait: {record['trait']}
Category: {record['major']} > {record['master']} > {record['sub']}
Gene Target: {record['gene']}
Mandate: Use this gene as the primary anchor for analysis.
"""
        return "[CLINICAL CONTEXT] No exact match found. Use general genomic principles."

# Singleton instance for the Swarm
rag_anchor = RAGEngine()
