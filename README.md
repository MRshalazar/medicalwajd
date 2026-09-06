# Privacy-Preserving Clinical Decision Support System (CDSS)

A privacy-preserving Clinical Decision Support System that uses Zero-Knowledge Proofs (ZKP) and Retrieval-Augmented Generation (RAG) to provide clinical decisions without exposing sensitive patient data.

## Architecture

```
┌──────────┐
│ Doctor   │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Coordinator                          │
│  ┌────────┐  ┌────────┐  ┌───────┐  ┌─────────────────┐  │
│  │Patient │→ │Policy  │→ │Proof  │→ │   Decision      │  │
│  │  Node  │  │  Node  │  │  Node │  │     Node        │  │
│  └────────┘  └────────┘  └───────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
     │              │            │              │
     ▼              ▼            ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│Patient   │  │   Rule   │  │ Privacy  │  │   Decision   │
│   MCP    │  │  Engine  │  │   MCP    │  │   Engine     │
│ (Port    │  │ (Port    │  │ (Port    │  │  (Port       │
│  8005)   │  │  8004)   │  │  8003)   │  │   8002)      │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘
     │              │            │              │
     ▼              ▼            ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐
│PostgreSQL│  │Knowledge │  │   ZKP    │  │   Simple     │
│          │  │   MCP    │  │ Engine   │  │   Logic      │
│          │  │(Port     │  │(Rust +   │  │              │
│          │  │ 8010)    │  │ Bullet-  │  │              │
│          │  │          │  │ proofs)  │  │              │
│          │  │ChromaDB  │  │          │  │              │
│          │  │+ Ollama  │  │          │  │              │
└──────────┘  └──────────┘  └──────────┘  └──────────────┘
```

## Key Features

- **Privacy-Preserving**: Sensor values never leave the device; only ZKP proofs are shared
- **RAG-Based Guidelines**: Medical guidelines retrieved from PDFs using semantic search
- **LLM-Powered Decisions**: Uses Ollama LLaMA3 for policy generation and explanations
- **Zero-Knowledge Proofs**: Rust-based Bulletproofs for range verification
- **LangGraph Workflow**: Orchestrates the entire decision pipeline

## Prerequisites

- Docker and Docker Compose
- Git
- Optional: Python 3.11+ if you want to run the console locally outside Docker
- Optional: Ollama CLI if you want to manage local models manually

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/WajdAyed/Privacy-Preserving-CDSS.git
cd Privacy-Preserving-CDSS
```

### 2. Start the full stack with Docker

From the project root:

```bash
docker compose up --build -d
```

On Windows PowerShell, this is also valid:

```powershell
docker-compose up --build -d
```

This starts all required services from [docker-compose.yml](docker-compose.yml):

- Ollama
- PostgreSQL
- Patient MCP
- Rule Engine
- Privacy MCP
- Decision Engine
- Knowledge MCP
- LangGraph Coordinator
- Doctor Console

### 3. Check the running services

```bash
docker compose ps
```

You can verify the main API entrypoints:

```bash
curl http://localhost:8007/docs
curl http://localhost:8005/docs
curl http://localhost:8010/docs
```

### 4. Pull Ollama models (if not already available in the container)

The project expects LLM and embedding models. If needed, run:

```bash
docker exec -it cdss-ollama ollama pull llama3
docker exec -it cdss-ollama ollama pull nomic-embed-text
```

If you are running Ollama outside Docker instead of the containerized service, use:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 5. Build the vector database

The knowledge service uses ChromaDB and embeddings. If the vector database is not initialized yet, run:

```bash
python scripts/build_rag.py
```

This is often needed once on the host machine before using the RAG pipeline.

## Running the System

The Docker-based setup is the recommended way to run the project.

### Start everything

```bash
docker compose up --build -d
```

### Stop everything

```bash
docker compose down
```

### Restart a single service

```bash
docker compose restart langgraph-coordinator
```

### View logs

```bash
docker compose logs -f
```

### Run the doctor console locally against the Docker host

If you want to use the interactive terminal UI from your own machine while the services run in Docker on another host, set the coordinator URL:

```powershell
$env:LANGGRAPH_URL="http://<HOST_IP>:8007"
python doctor_console.py
```

For example:

```powershell
$env:LANGGRAPH_URL="http://192.168.1.50:8007"
python doctor_console.py
```

### Run a test case against the running services

```bash
python langgraph_coordinator/run_case.py
```

If the app is running remotely, set the environment variable first:

```powershell
$env:LANGGRAPH_URL="http://<HOST_IP>:8007"
python langgraph_coordinator/run_case.py
```

## Running from another machine

The Docker host is still the machine running the containers. Another machine cannot directly access the internal service names such as `patient-mcp` or `rule-engine`.

Use the host IP or public IP instead:

```text
http://<HOST_IP>:8007
```

Example:

```text
http://192.168.1.50:8007
```

You must also make sure the following ports are reachable from the network:

- 8002
- 8003
- 8004
- 8005
- 8007
- 8010
- 11434
- 5432

## Alternative local startup (without Docker)

If you prefer not to use Docker, the project also supports a local setup:

### Linux setup

Install the system packages used by the startup script and ZKP engine:

```bash
sudo apt update
sudo apt install -y curl build-essential rustc cargo python3 python3-venv
```

Create the Python virtual environment and install the Linux dependencies:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/python -m pip install -r requirements-linux.txt
```

Use `requirements-linux.txt` for this setup. Installing the generic `requirements.txt` on Linux can fail with `No matching distribution found for pywin32` because that package is Windows-only.

After cleaning the local workspace or cloning the repository again, recreate the Linux environment with:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r requirements-linux.txt
```

Install Ollama, then download the required models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

Build the optional Rust proof engine and start the complete local stack:

```bash
cargo build --release --manifest-path zkp_engine/Cargo.toml
./run.sh
```

The Linux requirements file excludes Windows-only packages. `run.sh` starts Ollama when needed, launches all services, waits for their ports, and opens the doctor console.

### Verify a Linux run

Enter one of the displayed patient IDs, for example:

```text
10011398
```

A successful run returns `HTTP 200` and includes:

```text
Personalized Range: 120 - 140 systolic_bp
Sensor Value: PRIVATE
TRUE
Final Decision: Patient requires medical attention.
```

In this output, `TRUE` means that the zero-knowledge proof was verified successfully. It does not mean that the patient is clinically stable. The final decision is the clinical result; `Patient requires medical attention` is an alert, even when proof verification succeeds. The complete workflow includes patient lookup, RAG retrieval, policy generation, proof generation and verification, and decision generation.

If `run.sh` is started while an earlier CDSS stack is running, it stops existing Uvicorn services on the CDSS ports and starts a fresh stack. Do not stop unrelated processes using those ports.

```powershell
# Windows PowerShell
.\run.ps1
```

Or start services individually:

```powershell
.\start.ps1
```

Then launch the console manually:

```bash
python doctor_console.py
```

## Notes

- The Docker Compose configuration is the recommended deployment method.
- Internal container communication uses Docker service names, while external clients must use the host IP and mapped ports.
- The Ollama service is required for both the LLM and embeddings used by the RAG and policy generation components.

## How It Works

### 1. Guidelines Loading and RAG

The system loads medical guidelines from PDFs and creates a vector database for semantic search.

**File**: `knowledge_mcp/build_vector_db.py`

```python
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Load PDFs from guidelines directory
PDF_DIR = Path("RAG/guidelines")
documents = []

for pdf in PDF_DIR.glob("*.pdf"):
    loader = PyPDFLoader(str(pdf))
    docs = loader.load()
    documents.extend(docs)

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

# Create embeddings and store in ChromaDB
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434"
)

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="knowledge_mcp/chroma_db"
)
```

### 2. Guideline Retrieval

When a patient arrives, the system retrieves relevant guidelines based on their condition.

**File**: `knowledge_mcp/app.py`

```python
from fastapi import FastAPI
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

app = FastAPI(title="Knowledge MCP - RAG")

DB_DIR = Path(__file__).parent / "chroma_db"
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://127.0.0.1:11434"
)

db = Chroma(
    persist_directory=str(DB_DIR),
    embedding_function=embeddings
)

@app.get("/guidelines/{condition}")
def search_guidelines(condition: str):
    # Semantic search for top 3 relevant chunks
    docs = db.similarity_search(condition, k=3)
    
    return {
        "guidelines": [d.page_content for d in docs]
    }
```

### 3. Policy Generation with LLM

The Rule Engine uses retrieved guidelines to generate personalized safe limits.

**File**: `rule_engine/policy_generator.py`

```python
import requests
import ollama
import json
import re

def generate_policy(patient):
    condition = patient["condition"]
    age = patient["age"]
    
    # Step 1: Retrieve guidelines from Knowledge MCP
    rag_url = f"http://127.0.0.1:8010/guidelines/{condition}"
    rag_response = requests.get(rag_url, timeout=30)
    data = rag_response.json()
    docs = data["guidelines"]
    
    # Step 2: Join guidelines into context
    context = "\n\n".join(docs)
    
    # Step 3: Create prompt for LLM
    prompt = f"""
Patient:
Age: {age}
Condition: {condition}

Medical Guidelines:

{context}

Based on the medical guidelines, generate personalized safe limits.
Return ONLY JSON.

Example:
{{
   "parameter":"systolic_bp",
   "min":110,
   "max":135
}}
"""
    
    # Step 4: Call Ollama LLM
    response = ollama.chat(
        model="llama3",
        format="json",
        messages=[{"role":"user", "content":prompt}]
    )
    
    # Step 5: Extract JSON from response
    text = response["message"]["content"]
    match = re.search(r"\{.*\}", text, re.S)
    policy = json.loads(match.group())
    
    return policy
```

### 4. Zero-Knowledge Proof Generation

The device generates a proof that its sensor value is within the allowed range without revealing the actual value.

**File**: `privacy_mcp/zkp_client.py`

```python
import json
import subprocess
from pathlib import Path

ENGINE = Path(__file__).parent.parent / "zkp_engine" / "target" / "release" / "zkp_engine.exe"

def generate_and_verify_proof(bounds):
    # Device reads sensor value LOCALLY (never exposed)
    device_value = 190  # Simulated sensor reading
    
    # Prepare proof request
    request = {
        "value": device_value,
        "min": bounds["min"],
        "max": bounds["max"]
    }
    
    # Call Rust ZKP engine
    result = subprocess.run(
        [str(ENGINE)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        check=True
    )
    
    proof = json.loads(result.stdout)
    return proof
```

**File**: `device_agent/app.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json
from .sensor import read_systolic_bp

app = FastAPI()

class Policy(BaseModel):
    min: int
    max: int

@app.post("/prove")
def prove(policy: Policy):
    # Read sensor value locally
    value = read_systolic_bp()
    
    payload = {
        "value": value,
        "min": policy.min,
        "max": policy.max
    }
    
    # Generate ZKP proof locally
    result = subprocess.run(
        [r"zkp_engine\target\release\zkp_engine.exe"],
        input=json.dumps(payload),
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)
```

### 5. LangGraph Workflow

The coordinator orchestrates the entire decision pipeline.

**File**: `langgraph_coordinator/graph.py`

```python
from typing import TypedDict
import requests

class State(TypedDict):
    patient_id: str
    patient: dict
    policy: dict
    proof: dict
    decision: dict

def get_patient(state):
    """Get patient data from Patient MCP"""
    url = f"http://127.0.0.1:8005/patient/{state['patient_id']}"
    response = requests.get(url, timeout=10)
    patient = response.json()
    return {"patient": patient}

def get_policy(state):
    """Generate personalized policy from Rule Engine"""
    response = requests.post(
        "http://127.0.0.1:8004/policy",
        json=state["patient"],
        timeout=60
    )
    policy = response.json()
    return {"policy": policy}

def get_proof(state):
    """Request ZKP proof from Privacy MCP"""
    bounds = {
        "min": state["policy"]["min"],
        "max": state["policy"]["max"]
    }
    
    response = requests.post(
        "http://127.0.0.1:8003/request-proof",
        json={"bounds": bounds},
        timeout=30
    )
    proof = response.json()
    return {"proof": proof}

def get_decision(state):
    """Get clinical decision from Decision Engine"""
    response = requests.post(
        "http://127.0.0.1:8002/decision",
        json={"status": state["proof"]["status"]},
        timeout=10
    )
    decision = response.json()
    return {"decision": decision}
```

**File**: `langgraph_coordinator/app.py`

```python
from fastapi import FastAPI
from langgraph.graph import StateGraph, END
from .graph import State, get_patient, get_policy, get_proof, get_decision

app = FastAPI(title="LangGraph Coordinator")

# Build workflow graph
builder = StateGraph(State)

builder.add_node("patient", get_patient)
builder.add_node("policy", get_policy)
builder.add_node("proof", get_proof)
builder.add_node("decision", get_decision)

# Define workflow: patient → policy → proof → decision → END
builder.set_entry_point("patient")
builder.add_edge("patient", "policy")
builder.add_edge("policy", "proof")
builder.add_edge("proof", "decision")
builder.add_edge("decision", END)

graph = builder.compile()

@app.get("/run/{patient_id}")
def run(patient_id: str):
    initial_state = {
        "patient_id": patient_id,
        "patient": {},
        "policy": {},
        "proof": {},
        "decision": {}
    }
    
    result = graph.invoke(initial_state)
    return result
```

## API Endpoints

### LangGraph Coordinator (Port 8001)

```
GET /run/{patient_id}
```
Executes the full workflow for a patient.

**Example**:
```bash
curl http://localhost:8001/run/10009628
```

### Knowledge MCP (Port 8010)

```
GET /guidelines/{condition}
```
Retrieves relevant medical guidelines for a condition.

**Example**:
```bash
curl http://localhost:8010/guidelines/Diabetes
```

### Rule Engine (Port 8004)

```
POST /policy
```
Generates personalized policy bounds.

**Example**:
```bash
curl -X POST http://localhost:8004/policy \
  -H "Content-Type: application/json" \
  -d '{"condition": "Diabetes", "age": 65}'
```

### Privacy MCP (Port 8003)

```
POST /request-proof
```
Requests ZKP proof from device.

**Example**:
```bash
curl -X POST http://localhost:8003/request-proof \
  -H "Content-Type: application/json" \
  -d '{"bounds": {"min": 110, "max": 135}}'
```

### Decision Engine (Port 8002)

```
POST /decision
```
Returns clinical decision based on proof status.

**Example**:
```bash
curl -X POST http://localhost:8002/decision \
  -H "Content-Type: application/json" \
  -d '{"status": "NORMAL"}'
```

## Project Structure

```
Privacy-Preserving-CDSS/
├── RAG/
│   ├── rag.py                      # Legacy RAG implementation (HuggingFace)
│   ├── chroma_db/                  # Vector database (legacy)
│   └── guidelines/                 # Medical guideline PDFs
│       ├── Diabetes guideline.pdf
│       ├── Hypertension guideline.pdf
│       └── Heart Failure guideline.pdf
├── knowledge_mcp/
│   ├── app.py                      # Knowledge MCP API (Ollama embeddings)
│   ├── build_vector_db.py          # Vector database builder
│   └── chroma_db/                  # Vector database (active)
├── rule_engine/
│   ├── app.py                      # Rule Engine API
│   ├── policy_generator.py         # LLM-based policy generation
│   └── rules.py                    # Legacy rule-based policy
├── privacy_mcp/
│   ├── app.py                      # Privacy MCP API
│   └── zkp_client.py               # ZKP proof generation/verification
├── device_agent/
│   ├── app.py                      # Device agent API
│   └── sensor.py                   # Sensor reading simulation
├── langgraph_coordinator/
│   ├── app.py                      # LangGraph workflow API
│   ├── graph.py                    # Workflow nodes and edges
│   └── run_case.py                 # Test script
├── decision_engine/
│   ├── app.py                      # Decision Engine API
│   └── engine.py                   # Decision logic
├── patient_mcp/
│   ├── app.py                      # Patient MCP API
│   └── database.py                 # PostgreSQL database access
├── zkp_engine/
│   ├── Cargo.toml                  # Rust dependencies
│   └── src/                        # Rust source code
│       └── main.rs                 # Bulletproof implementation
├── datasets/
│   ├── original/                   # Original patient data
│   └── processed/                  # Processed data and schemas
├── scripts/
│   ├── build_rag.py                # Build vector database
│   └── prepare_dataset.py          # Prepare patient dataset
├── requirements.txt                # Python dependencies
├── start.ps1                       # Windows startup script
└── README.md                       # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cdss_db
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### Port Configuration

Default ports (can be modified in each service's `app.py`):

| Service | Port |
|---------|------|
| LangGraph Coordinator | 8001 |
| Decision Engine | 8002 |
| Privacy MCP | 8003 |
| Rule Engine | 8004 |
| Patient MCP | 8005 |
| Knowledge MCP | 8010 |
| Ollama | 11434 |

## Workflow Example

```
1. Doctor asks: "Is Ahmed clinically stable?"

2. LangGraph Coordinator receives request with patient_id

3. Patient Node:
   - Fetches patient profile from PostgreSQL
   - Returns: {condition: "Diabetes", age: 65}

4. Policy Node:
   - Retrieves Diabetes guidelines via RAG
   - LLM generates: {parameter: "systolic_bp", min: 110, max: 135}

5. Proof Node:
   - Sends bounds (110-135) to Privacy MCP
   - Device reads BP locally: 190
   - Device generates ZKP proof (value stays hidden)
   - Proof shows: value is OUTSIDE range

6. Decision Node:
   - Receives proof status: "OUT_OF_RANGE"
   - Returns: {stable: false, message: "Patient requires attention"}

7. Final Response to Doctor:
   - Status: Not stable
   - Reason: Blood pressure outside safe range
   - Privacy: Sensor value never exposed
```

## Privacy Guarantees

1. **Sensor Data Never Leaves Device**: Raw sensor values are read locally and only used for ZKP generation
2. **Zero-Knowledge Proofs**: Mathematical proofs verify properties without revealing data
3. **Minimal Data Sharing**: Only bounds and proof status are transmitted
4. **Local Computation**: ZKP generation happens on the device itself

## Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **LLM**: Ollama (LLaMA3)
- **Embeddings**: Ollama (nomic-embed-text)
- **Vector Database**: ChromaDB
- **Workflow Orchestration**: LangGraph
- **ZKP**: Rust + Bulletproofs
- **Database**: PostgreSQL
- **PDF Processing**: LangChain PyPDFLoader

## Testing

```bash
# Test ChromaDB
python test_chroma.py

# Test embeddings
python test_embed.py

# Run test case
python langgraph_coordinator/run_case.py

# Backend tests
cd backend
pytest
```

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama service
ollama serve
```

### ZKP Engine Not Found

```bash
# Build the Rust engine
cd zkp_engine
cargo build --release
```

### ChromaDB Errors

```bash
# Rebuild vector database
python scripts/build_rag.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is part of a master's thesis on privacy-preserving clinical decision support systems.

## Contact

For questions or issues, please open an issue on GitHub.