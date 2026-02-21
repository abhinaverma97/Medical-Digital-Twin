# VitaBlueprint

**VitaBlueprint** is a professional, deterministic medical device system design and compliance platform. It allows engineers to transition seamlessly from structured requirements to validated system architectures and digital twin simulations, ending with one-click code generation for embedded targets.

## 🚀 Key Features

- **Multi-Device Support**: Optimized for Class I (Pulse Oximeter), Class II (Ventilator), and Class III (Hemodialysis) medical devices.
- **Deterministic Design Graph**: Automatically infers subsystem architectures and interfaces from engineering requirements.
- **Hierarchical Visualization**: Generates High-Level (HLD) and Logical signal-flow diagrams using Graphviz.
- **Multi-Fidelity Digital Twins**: Supports L1 (Static), L2 (Dynamic), and L3 (Physics-based) simulation models for behavior validation.
- **Safety & Compliance**: Integrated ISO 14971 risk assessment, fault injection testing, and automated compliance traceability.
- **One-Click Codegen**: Generates a standard, runnable Python repository structure based on the validated design.

---

## 🛠️ Local Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Graphviz**: Required for diagram rendering.
  - **Windows**: [Download and Install](https://graphviz.org/download/) (Ensure you add it to the system **PATH** during installation).

### 1. Backend Setup
1.  Navigate to the project root.
2.  Create a virtual environment:
    ```powershell
    python -m venv venv
    ```
3.  Activate the environment:
    ```powershell
    # Windows
    .\venv\Scripts\Activate.ps1
    ```
4.  Install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```
5.  Start the FastAPI server:
    ```powershell
    python -m uvicorn backend.app.main:app --reload
    ```
    *The backend will be running at `http://127.0.0.1:8000`.*

### 2. Frontend Setup
1.  Navigate to the `frontend` directory:
    ```powershell
    cd frontend
    ```
2.  Install packages:
    ```powershell
    npm install
    ```
3.  Start the development server:
    ```powershell
    npm run dev
    ```
    *The application will be available at `http://localhost:5173`.*

---

## 📖 How to Use

1.  **Select Device**: Use the header dropdown to choose between Ventilator, Pulse Oximeter, or Hemodialysis.
2.  **Add Requirements**: 
    - Use the **Requirements** tab to manually add engineering specs.
    - Or click **"Autofill Sample"** to load pre-configured industrial requirements.
3.  **Build Design**: Go to **Design Graph** and click **"Build Design Graph"** to generate the block diagrams.
4.  **Simulate**: Use the **Digital Twin** tab to run simulations. You can inject faults to test safety mitigations.
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

© 2026 VitaBlueprint Engine — Industry-Grade System Engineering
