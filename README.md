# Enterprise Multi-Agent Conversational Sales Copilot using Hybrid Search (Qdrant + BM25)

Welcome to the **Multi-Agent Conversational Sales Copilot**! This is an enterprise-grade AI conversational sales copilot designed specifically for commercial truck and van product consulting and lead qualification.

The system features advanced conversational abilities, multi-turn context retention (Structured Memory), strict constraint verification (Hard Filters), automated missing parameter clarification, and a high-performance **Hybrid Search (Qdrant + BM25)** retrieval system. All orchestration is managed using **LangGraph**, and chat state is seamlessly synchronized in **Supabase (PostgreSQL)**.

---

## 🏗️ System Architecture

The application is structured as a highly modular, decoupled client-server architecture with Qdrant Cloud and a local high-performance BM25s index integrated into a multi-agent LangGraph workflow:

```mermaid
graph TD
    User([Customer]) <-->|Chat Interaction| UI[Streamlit UI - Dark Mode]
    UI <-->|FastAPI REST Client| API[FastAPI Backend]
    
    %% Databases & Search Index
    API <-->|SQLAlchemy ORM| Supabase[(Supabase PostgreSQL)]
    API <-->|Dense Vector Search| Qdrant[(Qdrant Cloud)]
    API <-->|Lexical Keyword Search| BM25[(Local BM25s Index)]
    
    %% LangGraph Flow
    subgraph Multi-Agent LangGraph Workflow
        Start([User Message]) --> ReqAgent[RequirementExtractionAgent]
        ReqAgent --> MemAgent[MemoryAgent]
        MemAgent --> CheckInfo{Info Sufficient?}
        
        CheckInfo -->|No| ClarifyAgent[ClarificationAgent]
        CheckInfo -->|Yes| HybridRetriever[HybridRetrieverAgent]
        
        ClarifyAgent --> EndResponse([Generate Clarification Question])
        HybridRetriever --> RecommendAgent[RecommendationAgent]
        RecommendAgent --> EndResponse([Generate Recommendation / Alternative Proposal])
    end
```

---

## 🚀 Key Features & Technology Stack

### 1. Multi-Agent Orchestration (LangGraph Workflow)
The conversational flow is managed via a compiled **LangGraph StateGraph** that directs user intent across specialized agents:
* **RequirementExtractionAgent**: Parses the user message to extract entities: `budget_min`, `budget_max`, `payload_min`, `payload_max`, `fuel_type`, `vehicle_type`, `use_case`, `location`, and `cargo_type`.
* **MemoryAgent**: Fetches historical session requirements from Supabase, merges them with newly extracted attributes (new values override old ones; old ones are preserved if new ones are empty), logs the transitions in the database, and saves the unified state back to the database.
* **ClarificationAgent**: Scans for missing critical parameters (such as budget range, payload range, fuel type, or vehicle type) and generates friendly, natural consultative questions in Vietnamese to clarify customer needs.
* **HybridRetrieverAgent**: Coordinates parallel queries on Qdrant and BM25s, applying strict constraints before merging results.
* **RecommendationAgent**: Selects top products, formats pricing, payload capacities, fuel types, and writes compelling sales copy explaining why the vehicles match the client's needs.

### 2. Structured Memory (Stateful & Traceable)
Instead of relying on unstructured text logs, the system maintains:
* **`CustomerProfile`**: A structured database state containing the latest known preferences of the customer (e.g. price range, payload range, preferred brand, urgency level).
* **`MemoryEvent`**: An event log capturing every change in the customer's requirements (e.g. initial, update, confirm, reject, conflict) along with confidence scores and reasons, letting you track how the customer changed their mind during the conversation.

### 3. Industry-Grade Retrieval (Hybrid Search + RRF)
* **Qdrant Cloud**: Performs dense vector semantic search on product manuals and descriptions to find contextually relevant trucks.
* **BM25s**: A high-performance, native Python implementation of the BM25 algorithm that searches product attributes using exact keyword matching, ensuring highly accurate queries on specific models, brands, or numeric payloads.
* **Reciprocal Rank Fusion (RRF)**: Merges ranked results from Qdrant and BM25s using the mathematical standard constant $k=60$ to produce a unified recommendation list.

### 4. Strict Hard Constraints Filtering
To eliminate mismatched recommendations (such as proposing a diesel truck when a petrol van is requested, or recommending a vehicle above budget):
* The system enforces **Strict Hard Filters** during retrieval *before* computing RRF scores: `Price` must fit within the specified budget range, `Payload` capacity must match the requested payload range, and exact matches on `Fuel Type` and `Vehicle Type`.

### 5. Consultative Alternative Recommendations
* If no exact match is found, instead of displaying an empty list, the agent **automatically relaxes** the vehicle type constraint (switching between `Van` $\leftrightarrow$ `Xe tải nhẹ`), recommending best-selling light trucks or vans as highly suitable alternatives, and politely explains the trade-offs to the customer.

---

## 🛠️ Installation & Running the Application

### 1. Configure Environment Variables (`.env`)
Create a `.env` file in the root directory:

```env
# OpenAI API Key (Leave empty to use Mock LLM Fallback Offline)
OPENAI_API_KEY=your-openai-api-key

# Database Connection (Supabase PostgreSQL Cloud)
# WARNING: If your Supabase password contains special characters like '@', they MUST be percent-encoded (e.g., '@' -> '%40')
DATABASE_URL=postgresql://postgres.your-supabase-username:%40your-password@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres

# Qdrant Config (Qdrant Cloud)
QDRANT_URL=https://your-qdrant-cluster.gcp.qdrant.io
QDRANT_API_KEY=your-qdrant-cloud-api-key
QDRANT_COLLECTION_NAME=truck_products
EMBEDDING_DIMENSION=1536

# Retriever Configs
VECTOR_TOP_K=5
GRAPH_TOP_K=5
TOP_K_HYBRID_RETRIEVER=3
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Activate your virtual environment
source .venv/bin/activate  # On Linux/macOS
# Or: .venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

### 3. Run Standalone Docker Compose (Optional)
Since all databases are hosted in the cloud or run locally in-memory, `docker-compose.yml` is pre-configured to run the FastAPI application standalone:
```bash
docker-compose up -d
```

### 4. Launch Backend API Server (FastAPI)
Run the FastAPI application from the project root:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```
*FastAPI automatically establishes connections and runs all necessary SQLAlchemy schema migrations to create `chat_sessions`, `chat_messages`, `customer_profiles`, `memory_events`, and `user_feedback` tables on Supabase Cloud on boot!*

### 5. Launch Frontend Application (Streamlit)
Open a new terminal and run:
```bash
streamlit run frontend/streamlit_app.py
```

---

## 📈 System Verification & Test Scenarios

### Step 1: Synchronize Database (CSV Ingestion)
On the Streamlit UI sidebar, click **"Nạp lại CSV (Qdrant & Neo4j)"**. The backend will parse the local `data/products.csv` containing 10 commercial vehicles and batch upsert them concurrently into Qdrant Cloud and rebuild the local BM25s index.

### Step 2: Test Parameter Clarification Flow
* **User Input**: *"Tôi cần mua xe chở hàng"* (I need to buy a cargo vehicle)
* **Copilot Response**: The `ClarificationAgent` triggers since budget, payload, and fuel are missing, consultative asking the user what cargo they carry, their budget, and whether they operate in the city or long-distance.

### Step 3: Test Conversational Memory
* **User Input**: *"Tôi cần xe dưới 500 triệu"* (I need a vehicle under 500M)
* **Copilot Response**: Proposes vehicles under 500M (Thaco TF2800, Towner 990, Tera 100).
* **User Input**: *"Chạy xăng thì sao"* (What about petrol models?)
* **Copilot Response**: The bot recalls the previous budget limitation ($<500M$) and proposes only the petrol-powered models under 500M (Thaco Towner 990, Tera 100).

### Step 4: Test Alternative Recommendations
* **User Input**: *"Tôi cần xe tải van dưới 500 triệu, chạy xăng, chở hàng nội thành, tải trên 900kg"* (I need a petrol van under 500M for city delivery carrying over 900kg)
* **Copilot Response**: The agent detects that the database has no petrol vans carrying $>900kg$ under $500M$ (since Suzuki Carry Van only carries 580kg). Rather than failing, the system relaxes the vehicle type, proposing the highly successful **Thaco Towner 990 (TRK-003)** and **Teraco Tera 100 (TRK-004)** **light trucks** as the optimal alternative, clearly explaining the payload trade-offs in Vietnamese!
