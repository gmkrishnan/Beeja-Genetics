import myvariant
import json
import os

class ClinicalValidator:
    """
    ENGINE: The Source of Truth.
    Uses MyVariant.info to validate agent outputs against ClinVar/dbSNP.
    """
    
    @staticmethod
    def validate_trait_logic(trait_name, gene_symbol):
        """
        Cross-checks if the gene and trait are scientifically linked.
        """
        mv = myvariant.MyVariantInfo()
        try:
            # Search for the gene and trait in ClinVar via MyVariant
            query = f'clinvar.gene.symbol:"{gene_symbol}" AND "{trait_name}"'
            res = mv.query(q=query, fields="clinvar.clinical_significance")
            
            if res and res.get('hits'):
                # We found a verified link
                significance = res['hits'][0].get('clinvar', {}).get('clinical_significance', 'Likely Pathogenic')
                return {
                    "verified": True,
                    "clinical_significance": significance,
                    "source": "ClinVar via MyVariant.info"
                }
        except Exception as e:
            print(f"Validation Error: {e}")
            
        return {"verified": False, "clinical_significance": "VUS", "source": "Inference"}

    @staticmethod
    def get_professional_nomenclature(rsid):
        """
        Retrieves HGVS nomenclature for a given RSID.
        """
        if not rsid or rsid == "N/A":
            return "N/A"
            
        mv = myvariant.MyVariantInfo()
        try:
            res = mv.query(q=f'dbsnp.rsid:"{rsid}"', fields="clinvar.hgvs.genomic")
            if res and res.get('hits'):
                return res['hits'][0].get('clinvar', {}).get('hgvs', {}).get('genomic', rsid)
        except:
            pass
        return rsid

# Singleton instance
clinical_validator = ClinicalValidator()
