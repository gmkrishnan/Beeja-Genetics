import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = os.getenv("PUBMED_API_KEY")

async def get_evidence_for_marker(gene, trait):
    """
    Helper to fetch targeted evidence for a gene/trait combo.
    """
    # Use the trait directly for better accuracy
    query = f"{gene} {trait} genetic risk"
    return await search_pubmed(query, max_results=2)

async def search_pubmed(query, max_results=2):
    """
    Searches PubMed and fetches full abstracts for the Evidence Agent to summarize.
    """
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }
    if API_KEY and API_KEY != "your_api_key_here":
        params["api_key"] = API_KEY

    async with httpx.AsyncClient() as client:
        # 1. Search for IDs
        search_res = await client.get(f"{PUBMED_API_URL}/esearch.fcgi", params=params)
        id_list = search_res.json().get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return []

        # 2. Fetch Full Details (EFETCH) to get Abstracts
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(id_list),
            "retmode": "xml",
        }
        if API_KEY and API_KEY != "your_api_key_here":
            fetch_params["api_key"] = API_KEY

        fetch_res = await client.get(f"{PUBMED_API_URL}/efetch.fcgi", params=fetch_params)
        xml_data = fetch_res.text
        
        import xml.etree.ElementTree as ET
        formatted_evidence = []
        
        try:
            root = ET.fromstring(xml_data)
            for article in root.findall(".//PubmedArticle"):
                pmid = article.find(".//PMID").text
                
                # Extract Title
                title_node = article.find(".//ArticleTitle")
                title = "".join(title_node.itertext()).strip() if title_node is not None else "Research Study"
                
                # Extract Abstract
                abstract_nodes = article.findall(".//AbstractText")
                abstract = " ".join(["".join(node.itertext()) for node in abstract_nodes]).strip()
                if not abstract:
                    abstract = "No abstract available."

                if pmid in id_list:
                    formatted_evidence.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract[:2000],
                        "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
        except Exception as e:
            print(f"DEBUG XML ERROR: {str(e)}")
            # Fallback to empty list if XML is totally broken
            
        return formatted_evidence
