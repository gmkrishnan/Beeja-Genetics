from Bio import Entrez
import os

# Entrez configuration (Requires an email for NCBI)
Entrez.email = "clinical.support@beeja.ai"

class ClinicalResearcher:
    """
    ENGINE: The Research Layer.
    Fetches the latest scientific papers from PubMed/Entrez.
    """
    
    @staticmethod
    def get_latest_papers(trait_name, gene_symbol, limit=2):
        """
        Searches PubMed for the latest research on a gene-trait link.
        """
        try:
            query = f'("{gene_symbol}"[Gene]) AND ("{trait_name}"[MeSH Terms] OR "{trait_name}"[All Fields])'
            handle = Entrez.esearch(db="pubmed", term=query, retmax=limit)
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record.get("IdList", [])
            papers = []
            
            if pmids:
                handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="medline", retmode="text")
                # For now, we just return the PMIDs and a placeholder link
                # In a full impl, we'd parse the titles and abstracts.
                for pmid in pmids:
                    papers.append({
                        "pmid": pmid,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "title": f"Scientific Study on {gene_symbol} and {trait_name}" # Placeholder
                    })
            return papers
        except Exception as e:
            print(f"Research Error: {e}")
            
        return []

# Singleton instance
clinical_researcher = ClinicalResearcher()
