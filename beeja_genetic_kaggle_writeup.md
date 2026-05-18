# 🧬 Beeja Genetics (GeneGuardian)
## A Local-First, Sovereign, Multi-Agent DNA Intelligence & Lifestyle Orchestration Platform

### 📢 Tagline
> **"Decode your biological blueprint. Orchestrate your life with absolute precision."**

---

## 💻 Chapter 2: The Tech Stack (Unified & Simplified)

To make Beeja Genetics run completely offline, the technology stack is divided into a clean, standard two-tier setup:

### 1. 🎨 The Frontend (Visuals & Interface)
* **Vite + React (JavaScript)**: The engine that builds the visual interface, managing user inputs (age, diet, file uploads) and dynamic actions.
* **Vanilla CSS**: Custom styling that creates the premium dark mode look with glassmorphic cards, HSL gradients, and a scrolling terminal console.

### 2. ⚙️ The Backend & Local AI (Logic, Databases & Inference)
* **Python + FastAPI**: The asynchronous backend server that acts as the traffic controller, routing API requests from the frontend.
* **Uvicorn**: The local web server hosting the FastAPI application.
* **Ollama**: The local engine that hosts and executes AI models offline on your computer.
* **Google Gemma 4 (`gemma4:e2b`)**: The quantized LLM hosted via Ollama that acts as the clinical reasoning specialist.
* **SQLite Database**: Lightweight local files storing:
  * `clinical_vault.db`: Known genetic risk markers and protocols.
  * `master_traits.db`: The clinical category checklists.
  * `clinical_memory.db`: Previously computed results (caching) to eliminate redundant LLM processing.
* **ChromaDB**: An offline vector database that caches conversational memory for instant search retrieval.
* **`snps` Parser**: A Python library that parses and normalizes raw text files from vendors like 23andMe and AncestryDNA.
* **`myvariant` & HTTPX**: Integration tools to validate genes against ClinVar/dbSNP and retrieve clinical paper abstracts from PubMed asynchronously.


---

## 🏛️ Chapter 3: The Architecture Paradigm (Local-First MACH/MAD)

In modern web development, teams use **MACH** (Microservices, API-first, Cloud-native, Headless) and **MAD** (Modern Application Development) patterns to build flexible, high-scale applications. Beeja Genetics adapts these patterns into a **Local-First Sovereign Architecture**.

```
+--------------------------+               +--------------------------------------+
|  Vite + React Frontend   |  =========>   |       FastAPI Asynchronous Backend   |
| (UI State / Chat Panel)  |   (REST JSON) |  (Orchestrator Swarm / Parser / SQL) |
+--------------------------+               +--------------------------------------+
```

### 1. Decoupled API-First Design (MACH/MAD Style)
The frontend and backend are completely decoupled. The React client acts as a "headless" viewer that talks to the FastAPI server exclusively over standardized JSON REST endpoints:
* `/categories/tree`: Builds the category checklist.
* `/analyze`: Submits selected traits and returns structured genetics data.
* `/chat`: Standardized dialogue gateway for conversational queries.

### 2. The Sovereign Twist (No-Cloud SaaS)
Traditional MACH architectures depend entirely on external cloud SaaS APIs (like OpenAI, AWS, or Pinecone). 
Beeja Genetics **reverses this cloud dependence**:
* All micro-services (the 15-Agent Swarm), databases (SQLite, ChromaDB), and intelligence modules (Ollama + Gemma 4) run inside a secure sandbox **directly on the user's host machine**.
* This guarantees absolute privacy (Data Sovereignty) while maintaining a modern, decoupled architecture.

### 3. The DNA Ingestion Pipeline
We built a robust, standardized data flow to process raw DNA files reliably:
1. **Upload**: User drops their raw sequence text file.
2. **Ingestion**: The `snps` parser normalizes chromosome columns and detects the build.
3. **Vault Lookup**: Queries the SQLite database to identify matches for specific risk genotypes.
4. **Epigenetic Aging Logic**: Calculates "Door Status" (CLOSED, OPENING, WIDE OPEN) by comparing the user's age to the average onset age of the risk trait.
5. **Caching**: Saves parsed data locally, ensuring subsequent reloads take less than 2 seconds.

---

## 🧠 Chapter 5: How we use Google Gemma 4 & RAG

The core intelligence of the platform is driven by **Google Gemma 4 (`gemma4:e2b`)** running locally, combined with a custom **Retrieval-Augmented Generation (RAG)** context anchor and real-time validation layers.

```
                  +--------------------------------+
                  |  User Query / Selected Trait   |
                  +--------------------------------+
                                  |
                                  v
                  +--------------------------------+
                  |      Sovereign RAG Engine      |  <-- matches registry/clinical_vault.json
                  +--------------------------------+
                                  |
                   (Injects Verified Gene Target)
                                  v
                  +--------------------------------+
                  |  Local Gemma 4 via Ollama API  |  <-- low temp (0.1 - 0.3)
                  +--------------------------------+
                                  |
             (JSON Output: risk, mechanism, protocol)
                                  v
                  +--------------------------------+
                  |    Scientific Proof Validation |  <-- ClinVar (MyVariant) & PubMed (HTTPX)
                  +--------------------------------+
```

### 1. Local Gemma 4 Inference Configuration
We connect to local Gemma 4 via Ollama's HTTP API (`http://localhost:11434`). We configure the request options with strict parameters to ensure consistent, premium results:
* **Temperature (0.1 - 0.3)**: Low temperature to minimize creative writing and maximize logical, scientific accuracy.
* **Context Window (16,384)**: Generous context window to accommodate deep clinical inputs, memory cache histories, and PubMed paper abstracts.
* **Predict Token Count (8,192)**: High ceiling to support long, multi-pillar health and fitness schedule generation without truncation.

### 2. The Sovereign RAG Anchor (Hallucination Prevention)
To ensure the local LLM remains perfectly accurate, we build a local **RAGEngine**:
* When a user queries a trait, the RAGEngine searches a local catalog (`clinical_vault.json`) using Python's `difflib.get_close_matches`.
* It retrieves the verified clinical target gene and primary biological mandate.
* It injects this verified context directly into the system prompt: *"You must analyze the patient's actual genotype for SNP in the target gene. Do not estimate or analyze any other genotype."*
* This strictly anchors Gemma 4, **completely preventing hallucinations**.

### 3. Factual Proof Verification
Once Gemma 4 outputs a findings report, the backend automatically validates and backs it up with real-world scientific proof:
1. **ClinVar Validation**: The backend queries `MyVariant.info` to check if the proposed gene-trait association is verified in ClinVar, returning the verified ACMG classification (e.g. Pathogenic, VUS).
2. **HGVS Standardization**: dbSNP is checked to replace generic SNP labels with professional HGVS genomic nomenclatures (e.g. `NC_000001.10:g.11854476A>G`).
3. **PubMed Research Agent**: The NCBI PubMed API is queried via HTTPX. The abstracts of the top research papers are fetched, and a separate low-temperature Gemma 4 call extracts "Hard Numbers" (e.g., *"Study of 14,000 patients showed a 22% risk increase"*), outputting exact clickable PubMed reference links.
