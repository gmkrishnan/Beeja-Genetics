import json
import os
import sqlite3

class ClinicalMemory:
    """
    ENGINE: The Sovereign Memory Layer.
    Caches full clinical results including scientific ledger.
    """
    def __init__(self, db_path="registry/clinical_memory.db"):
        self.db_path = db_path
        self._init_sqlite()
        self.chroma_collection = None
        
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path="registry/chroma_memory")
            self.chroma_collection = self.chroma_client.get_or_create_collection(name="clinical_cache")
        except:
            pass

    def _init_sqlite(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Full-Fidelity Schema with genotype, clinical_plan, and genetic_mechanism columns added
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id TEXT PRIMARY KEY,
                trait TEXT,
                gene TEXT,
                risk TEXT,
                summary TEXT,
                acmg TEXT,
                hgvs TEXT,
                hpo TEXT,
                evidence TEXT,
                scientific_truth TEXT,
                citations_json TEXT,
                genotype TEXT,
                clinical_plan TEXT,
                genetic_mechanism TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def remember(self, trait, gene, risk_tier, summary, genotype="N/A", acmg="VUS", hgvs="N/A", hpo="N/A", evidence="Lvl 3", truth="Inference", citations=[], clinical_plan="N/A", genetic_mechanism="N/A"):
        """
        Stores a full validated clinical result.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO memory (id, trait, gene, risk, summary, acmg, hgvs, hpo, evidence, scientific_truth, citations_json, genotype, clinical_plan, genetic_mechanism)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"{trait}_{gene}", trait, gene, risk_tier, summary, acmg, hgvs, hpo, evidence, truth, json.dumps(citations), genotype, clinical_plan, genetic_mechanism))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Memory Store Error: {e}")

    def recall(self, trait, gene):
        """
        Searches memory for a full result.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM memory WHERE id = ?', (f"{trait}_{gene}",))
            row = cursor.fetchone()
            conn.close()
            if row:
                # We need to map columns correctly.
                # PRAGMA info order: id, trait, gene, risk, summary, acmg, hgvs, hpo, evidence, scientific_truth, citations_json, genotype, clinical_plan, genetic_mechanism, timestamp
                return {
                    "trait": row[1],
                    "gene": row[2],
                    "risk_tier": row[3],
                    "summary": row[4],
                    "acmg_class": row[5],
                    "hgvs_id": row[6],
                    "hpo_term": row[7],
                    "evidence_level": row[8],
                    "scientific_truth": row[9],
                    "citations": json.loads(row[10]) if row[10] else [],
                    "genotype": row[11] if len(row) > 11 else "N/A",
                    "clinical_plan": row[12] if len(row) > 12 else "N/A",
                    "genetic_mechanism": row[13] if len(row) > 13 else "N/A"
                }
        except Exception as e:
            print(f"Memory Recall Error: {e}")
            
        return None

# Singleton instance
clinical_memory = ClinicalMemory()
