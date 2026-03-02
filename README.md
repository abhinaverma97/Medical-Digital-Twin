# DigitalTwin For Medical Devices

**Digital Twin** is a professional, deterministic medical device system design and compliance tool. It allows engineers to transition seamlessly from structured requirements to validated system architectures and digital twin simulations, ending with one-click code generation for embedded targets.

# Deployment Link
http://129.154.227.67/

## 🚀 Key Features

- **Multi-Device Support**: Optimized for Class I (Pulse Oximeter), Class II (Ventilator), and Class III (Hemodialysis) medical devices.
- **Authority-Based RAG System**: Intelligent knowledge base with 1900+ documents prioritizing ISO 60601-1 (electrical safety), ISO 62366-2 (usability), FDA guidance, and peer-reviewed medical literature over code templates.
- **IEC 62304 Compliant Design Hierarchy**:
  - **§5.3 System Architecture**: Top-level functional decomposition into subsystems
  - **§5.4 Subsystem Design**: Component-level specifications with software modules
  - **§5.5 Detailed Design**: BOM, PCB components, firmware architecture, verification plans
- **Design Verification Matrix**: FDA 21 CFR 820.30(g) compliant Requirements → Design → Verification mapping
- **Multi-Fidelity Digital Twins**: Supports L1 (Static), L2 (Dynamic), and L3 (Physics-based) simulation models for behavior validation.
- **Safety & Compliance**: Integrated ISO 14971 risk assessment, fault injection testing, automated compliance traceability with citations to authoritative sources.
- **Automated Scrapers**: Weekly updates from FDA OpenFDA API (device classifications, 510k summaries) and PubMed (medical literature).
- **One-Click Codegen**: Generates a standard, runnable Python repository structure based on the validated design.

---

## 🛠️ Local Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **GROQ API Key**: Required for LLM-powered requirements analysis and design generation.
  - Sign up at [console.groq.com](https://console.groq.com)
  - Create a `.env` file in the project root with your API key

### 1. Option A: Using Docker (Fastest)
1. Ensure Docker Desktop is running on your machine.
2. Build and run the containers from the project root:
   ```powershell
   docker-compose up --build
   ```
3. Open your browser and navigate to `http://localhost`.

### 2. Option B: Running Manually (Frontend + Backend)

**Terminal 1: Start the Backend (FastAPI)**
1. Navigate to the project root.
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # source venv/bin/activate   # Linux/Mac
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```powershell
   uvicorn backend.app.main:app --reload --port 8000
   ```

**Terminal 2: Start the Frontend (Vite/React)**
1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install dependencies:
   ```powershell
   npm install
   ```
3. Start the development server:
   ```powershell
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## 🧠 RAG Knowledge Base

The system uses an **authority-weighted retrieval-augmented generation (RAG)** architecture to ground all LLM outputs in regulatory standards and peer-reviewed sources.

### Authority Ranking (Retrieval Boost)

| Level | Source Type | Boost | Examples |
|-------|-------------|-------|----------|
| 5 | ISO Standards | **2.0x** | ISO 60601-1 (electrical safety), ISO 62366-2 (usability), ISO 14971 (risk) |
| 4 | FDA Guidance | 1.5x | Device classifications, 510(k) summaries |
| 3 | Component Datasheets | 1.2x | Sensor specs, MCU datasheets |
| 2 | Medical Literature | 1.0x | PubMed articles, clinical studies |
| 1 | Code Templates | 0.8x | Internal codebase examples |

### Knowledge Base Contents (1,014+ documents)

- **ISO Standard Chunks** - Electrical safety (60601-1), usability engineering (62366-2), risk management (14971)
- **FDA Device Records** - Classifications, regulatory requirements, 510(k) summaries  
- **PubMed Articles** - Medical device design research, safety studies
- **KiCad Footprints** - PCB component libraries with package specifications
- **Component Datasheets** - Sensor specs, MCU documentation (from caches)

### Generating and Updating the RAG Architecture (One-Time Setup)

To build the database, download the FDA logs, cache PubMed literature, and index ISO standards, run the setup script:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/setup_full_knowledge_base.py
```
This script will detect existing data and only update what's changed. Note that a full first-time rebuild will take 30-60 minutes to pull all PDF rules.

---

## ⚙️ Project Structure

- `backend/`: FastAPI application, core logic, and device models.
  - `app/core/retrieval/`: RAG indexer, retriever, and database schema.
  - `app/core/requirements/`: NLP analyzer with RAG grounding.
  - `app/api/design.py`: Design generation with ISO/FDA context injection.
- `frontend/`: React + Vite + Tailwind CSS application.
- `scripts/`: Database setup, scrapers, schedulers, ISO ingestion.
  - `scrapers/`: FDA OpenFDA and PubMed scrapers.
  - `scheduler.py`: Automated knowledge base updates.
  - `ingest_standards.py`: ISO PDF text extraction and indexing.
- `documents/`: Knowledge base directory structure.
  - `standards/`: ISO PDF files (user-provided).
  - `fda_cache/`: Cached FDA API responses.
  - `pubmed_cache/`: Cached PubMed search results.
  - `README.md`: Complete knowledge base documentation.
- `.samples/`: Pre-configured requirement sets for medical devices.
- `generated_repos/`: Output directory for the automated code generator.
- `rag_metadata.db`: SQLite database with 1955 indexed documents
- `rag_metadata.db`: SQLite database with 1955 indexed documents

---

## 📖 How to Use

1.  **Select Device**: Use the header dropdown to choose between Ventilator, Pulse Oximeter, or Hemodialysis.
2.  **Add Requirements**: 
    - Use the **Requirements** tab to manually add engineering specs.
    - Or click **"Autofill Sample"** to load pre-configured industrial requirements.
    - Requirements are automatically analyzed using RAG-grounded LLM, referencing ISO standards and FDA guidance.
3.  **Build Design**: Go to **Graph** and click **"Generate Design Graph"** to generate the complete design hierarchy:
    - **System Architecture (§5.3)**: High-level block diagram of major subsystems
    - **Subsystem Design (§5.4)**: Module-level decomposition with interfaces
    - **Detailed Design (§5.5)**: BOM with part numbers, PCB component specifications, firmware architecture (RTOS tasks, software modules, interrupts)
    - **Verification Matrix**: Requirements→Design→Verification mapping per FDA 21 CFR 820.30(g)
4.  **Simulate**: Once the AI finishes generating the Verification Matrix, click **"Simulate"** to map the design specifications directly into physics-based twins. You can inject faults to test safety mitigations.
5.  **Export & Codegen**: In the **Traceability** tab:
    - Review the Compliance Matrix.
    - Click **"Generate Code Repository"** to create a structured codebase in `generated_repos/`.

---

## ⚙️ Project Structure

- `backend/`: FastAPI application, core logic, and device models.
- `frontend/`: React + Vite + Tailwind CSS application.
- `.samples/`: Pre-configured requirement sets for medical devices.
- `generated_repos/`: Output directory for the automated code generator.

---

