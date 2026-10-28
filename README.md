# GraphMASAL — Graph-Based Multi-Agent System for Adaptive Student Learning
<!-- This is a comment deployed link : https://graphmasal-3.onrender.com/-->

An intelligent tutoring system that combines **multi-agent LangGraph orchestration**, **Neo4j knowledge graphs**, and **adaptive learning paths** to personalize education across multiple curricula.

> Built as part of an academic project exploring how graph-based AI agents can detect misconceptions, plan learning sequences, and deliver personalized tutoring at scale.
> Evaluated across two independent curriculum domains: **Operating Systems (OSTEP)** and **REST API Design**.

---
<img width="1535" height="786" alt="image" src="https://github.com/user-attachments/assets/8cc381d1-7df9-4e79-94d2-43270ba3486a" />
<img width="1362" height="603" alt="image" src="https://github.com/user-attachments/assets/65d2540b-65b6-4456-aa7b-8457cd89872d" />




## ✨ Features

### 🤖 Multi-Agent Workflow (LangGraph)
- **Router Agent** — Classifies student queries into `diagnose` or `retrieve` pathways using structured Chain-of-Thought few-shot prompting with semantic intent analysis
- **Diagnoser Agent** — Detects misconceptions via LLM reasoning with dynamic Neo4j concept querying, canonical alias resolution, and mastery reset to 0.0
- **Planner Agent** — Generates mathematically optimal learning paths using the Multi-Source Multi-Sink (MSMS) graph algorithm
- **Tutor Agent** — Synthesizes context-aware responses adapted to the student's route (gentle correction vs. direct answer)

### 🧠 Knowledge Graph (Neo4j)
- **Concept nodes** with descriptions, embeddings, and prerequisite relationships
- **Student nodes** tracking per-concept mastery scores (0.0–1.0)
- **Long-term memory** storing and recalling previous interactions per student
- **Vector similarity index** for semantic search over concept embeddings
- **Multi-curriculum support** — seed scripts for OS and REST API Design knowledge graphs

### 🔍 Advanced Hybrid Retrieval Pipeline
- **Semantic search** using `all-MiniLM-L6-v2` sentence embeddings
- **Graph neighborhood expansion** pulling in prerequisite and downstream concepts
- **Structure-aware reranking** with calibrated similarity-first weights (0.75 semantic, 0.15 frontier, 0.10 structural)
- **Contextual compression** — LLM-powered context distillation with minimum chunk length protection (`min_chunk_len=250`)
- **CRAG (Corrective RAG)** — Self-correction loop that detects low-confidence retrievals and synthesizes authoritative fallback answers
- **Query transformation (HyDE)** — Hypothetical Document Embeddings for improved retrieval on ambiguous queries

### 📄 PDF Ingestion Pipeline
- Upload textbook PDFs and automatically chunk, embed, and store them in Neo4j
- LLM-powered concept extraction from PDF chunks
- Overlapping chunking strategy (900-char chunks, 150-char overlap)
- Duplicate detection via content hashing

### 🌐 Three Interface Options
1. **Web UI** — Polished HTML/JS/CSS frontend served by FastAPI (`public/`)
2. **Streamlit Dashboard** — Feature-rich dashboard with knowledge graph visualization, roadmap viewer, PDF upload, and teacher analytics
3. **CLI** — Interactive terminal-based tutoring loop

### 📊 Analytics & Persistence (MongoDB)
- **MongoDB Q&A Store** — Every query/answer turn is persisted with full agent state (route, misconceptions, learning paths, response time, model metadata)
- **Session management** — Create, list, resume, and delete sessions
- **Teacher dashboard** — Monitor student lists, track per-student mastery profiles, view misconception history, and review recent activity
- **Teacher collections** — Manage which students a teacher monitors

### 🎥 Video Recommendations
- Auto-generated YouTube search links for each concept in the student's active learning plan
- Categorized by type: Introduction, Full Tutorial, Visual/Animation, Examples & Practice

### 🧪 Comprehensive Evaluation Suite
- **Router Evaluation** — Accuracy, Weighted F1, Macro F1, Cohen's Kappa against 50 ground-truth test cases per domain
- **Diagnoser Evaluation** — Precision, Recall, F1, and Concept Attribution Accuracy against 30 ground-truth cases per domain
- **PathSim** — Evaluates AI-generated learning paths against expert-defined ground truth (node overlap, edge overlap, sequence similarity, prerequisite integrity)
- **RAGAS Ablation** — Measures RAG pipeline quality comparing Hybrid (Vector + KG + Reranker + CRAG) vs. Vector-Only: Faithfulness, Answer Relevancy, Context Precision, Context Recall, Answer Correctness
- **Cross-domain validation** — All evaluations run independently on OS and REST API Design curricula
- **Baseline preservation** — All `*_baseline.json` reports maintained for before/after comparison

### 🔍 LangSmith Tracing
- Automatic tracing of every LLM call and tool invocation
- Per-session metadata tags and dashboard visualization
- Traces all agent state transitions and data flow

---

## 📈 Evaluation Results

All metrics are evaluated across two independent curricula: **Operating Systems (OSTEP, 12 concepts)** and **REST API Design (11 concepts)**. Baseline values represent the initial system before optimization; Optimized values reflect the current architecture with all improvements applied.

### Layer 1: Router Agent

| Metric | OS Baseline | OS Optimized | API Baseline | API Optimized |
|:---|:---:|:---:|:---:|:---:|
| **Accuracy** | 78.00% | **98.00%** (+20.00%) | 70.00% | **88.00%** (+18.00%) |
| **Weighted F1** | 0.7790 | **0.9799** | 0.6950 | **0.8788** |
| **Cohen's Kappa** | 0.5378 (Moderate) | **0.9580** (Near-perfect) | 0.3590 (Fair) | **0.7458** (Substantial) |

### Layer 2: Diagnoser Agent

| Metric | OS Baseline | OS Optimized | API Baseline | API Optimized |
|:---|:---:|:---:|:---:|:---:|
| **Accuracy** | 83.33% | **93.33%** (+10.00%) | 70.00% | **83.33%** (+13.33%) |
| **Precision** | 0.7500 | **0.8824** | 0.7143 | **0.9167** |
| **Recall** | 1.0000 | **1.0000** | 0.6667 | **0.7333** |
| **F1 Score** | 0.8571 | **0.9375** | 0.6897 | **0.8148** |
| **Concept Attribution** | 26.67% | **80.00%** (+53.33%) | 20.00% | **81.82%** (+61.82%) |

### Layer 3: Planner Agent (MSMS vs BFS)

| Metric | OS (MSMS) | OS (BFS) | API (MSMS) |
|:---|:---:|:---:|:---:|
| **PathSim Score** | **1.0000** | 1.0000 | — |
| **Prerequisite Integrity** | **1.0000** | 1.0000 | **1.0000** |
| **Sink Coverage** | **1.0000** | 1.0000 | **1.0000** |
| **Path Efficiency** | — | — | **1.1667** |

### Layer 4: RAGAS Retrieval & Generation Ablation

| Metric | OS Hybrid | OS Vector-Only | API Hybrid | API Vector-Only |
|:---|:---:|:---:|:---:|:---:|
| **Context Precision** | **0.5917** | 0.5500 | **0.6250** | 0.6667 |
| **Context Recall** | **0.4333** | 0.4167 | **0.4417** | 0.4458 |
| **Answer Correctness** | **0.4867** | 0.4198 | **0.3917** | 0.3861 |
| **Answer Relevancy** | **0.9148** | 0.9214 | **0.7864** | 0.8534 |
| **Faithfulness** | **0.7604** | 0.8659 | **0.6936** | 0.7823 |

> **Key gains from baseline:** OS Faithfulness +30.5% (0.4554 → 0.7604), API Context Precision +30.0% (0.3250 → 0.6250), API Answer Relevancy +29.5% (0.4918 → 0.7864)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│  ┌──────────┐  ┌───────────────┐  ┌──────────────────┐ │
│  │ Web UI   │  │  Streamlit    │  │   CLI            │ │
│  │ (public/)│  │  Dashboard    │  │ (workflow.py)    │ │
│  └────┬─────┘  └───────┬───────┘  └────────┬─────────┘ │
└───────┼────────────────┼───────────────────┼───────────┘
        │                │                   │
        ▼                ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│               FastAPI Server (src/api/server.py)        │
│  /api/chat  /api/sessions  /api/roadmap  /api/videos    │
│  /api/upload_pdf  /api/compute_path  /api/mastery  ...  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            LangGraph Workflow (src/agents/)              │
│                                                         │
│  START ──▶ Router ──┬──▶ Diagnoser ──▶ Planner ──▶ Tutor│
│                     │                                   │
│                     └──────────────▶ Planner ──▶ Tutor  │
│                   (diagnose)         (retrieve)         │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌─────────┐   ┌───────────┐   ┌───────────┐
   │ Neo4j   │   │  MongoDB  │   │  OpenAI   │
   │ (Graph) │   │ (Sessions)│   │  (LLM)    │
   └─────────┘   └───────────┘   └───────────┘
```

### Retrieval Pipeline Detail

```
User Query
    │
    ▼
┌──────────────────┐
│ Query Transform  │ ← Optional HyDE (Hypothetical Document Embeddings)
│ (query_transform)│
└────────┬─────────┘
         ▼
┌──────────────────┐     ┌──────────────────┐
│ Semantic Search  │────▶│ Graph Expansion  │ ← Pull prerequisites & downstream
│ (search.py)      │     │ (hybrid.py)      │   concepts from Neo4j topology
└──────────────────┘     └────────┬─────────┘
                                  ▼
                    ┌──────────────────────┐
                    │ Structure-Aware      │ ← Weights: 0.75 semantic, 0.15
                    │ Reranker (reranker)  │   frontier, 0.10 structural
                    └────────┬─────────────┘
                             ▼
                    ┌──────────────────────┐
                    │ Contextual Compressor│ ← LLM distillation with
                    │ (compressor.py)      │   min_chunk_len=250 protection
                    └────────┬─────────────┘
                             ▼
                    ┌──────────────────────┐
                    │ CRAG Self-Correction │ ← Detects low-confidence results,
                    │ (crag.py)            │   synthesizes fallback answers
                    └──────────────────────┘
```

---

## 🚀 Setup

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.12+ | Runtime |
| [uv](https://docs.astral.sh/uv/) | latest | Package manager |
| Neo4j Aura | — | Cloud graph database |
| MongoDB Atlas (or local) | — | Session & Q&A persistence |
| OpenAI API key | — | LLM inference |

### 1. Clone & Install

```bash
git clone https://github.com/ManjeetMMIV/GraphMASAL.git
cd GraphMASAL
uv sync
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Required — Neo4j Aura
NEO4J_URI=neo4j+s://your-aura-instance.databases.neo4j.io
NEO4J_USERNAME=your-username
NEO4J_PASSWORD=your-password

# Required — MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=YourApp

# Required — OpenAI
OPENAI_API_KEY=sk-...

# Optional — Override the default OpenAI model (default: gpt-3.5-turbo)
GRAPHMASAL_OPENAI_MODEL=gpt-4o-mini

# Optional — LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=graphmasal
```

### 3. Seed the Knowledge Graph

Seed the Neo4j database with curriculum concepts, prerequisites, PDF chunks, and embeddings:

```bash
# Operating Systems curriculum (12 concepts, 12 prerequisite edges)
uv run python scripts/seed_os_knowledge.py

# REST API Design curriculum (11 concepts, 17 prerequisite edges)
uv run python scripts/seed_api_knowledge.py
```

### 4. Verify Setup

```bash
uv run python test_startup.py
```

This imports all core modules and confirms dependencies are working.

---

## 💻 Usage

### Option 1: Web UI (FastAPI + Static Frontend)

```bash
uv run uvicorn src.api.server:app --reload
```

Open [http://localhost:8000](http://localhost:8000) — the FastAPI server serves the polished web interface from `public/`.

**Features**: Onboarding flow, real-time SSE streaming chat, session management, learning plan generation, knowledge graph visualization, video recommendations, mastery tracking, PDF upload, and teacher dashboard.

### Option 2: Streamlit Dashboard

```bash
uv run streamlit run src/ui/streamlit_app.py
```

**Features**: Knowledge graph visualization (Graphviz), interactive roadmap, PDF ingestion, mastery overview, conversation history with agent step details, memory management.

### Option 3: Interactive CLI

```bash
cd src/agents
uv run workflow.py
```

**Example interaction**:
```
[Alice]: What is paging?
[System]: Analyzing your query and consulting knowledge base...
[Storage]: Turn saved (row 64a..., 1250 ms)
[AI Tutor]: Paging is a memory management technique that divides...
```

---

## 📡 API Reference

The FastAPI server (`src/api/server.py`) exposes the following endpoints via modular route files:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/sessions/new` | Create a new chat session |
| `GET` | `/api/sessions` | List all sessions for a student |
| `GET` | `/api/session/{id}` | Get session info + message history |
| `DELETE` | `/api/session/{id}` | Delete a specific session |
| `POST` | `/api/chat` | SSE-streamed chat with agent pipeline |
| `GET` | `/api/roadmap` | Get active learning plan for a session |
| `GET` | `/api/videos` | YouTube recommendations per concept |
| `GET` | `/api/knowledge_graph` | Concept nodes + edges for visualization |
| `GET` | `/api/concepts` | List extracted concepts for a student |
| `POST` | `/api/compute_path` | Run MSMS algorithm (sources → sinks) |
| `POST` | `/api/select_plan` | Store selected learning plan in session |
| `POST` | `/api/upload_pdf` | Upload and ingest a PDF textbook |
| `POST` | `/api/extract_concepts` | Re-extract concepts from stored PDFs |
| `GET` | `/api/documents` | List uploaded PDF documents |
| `DELETE` | `/api/documents` | Delete all PDFs for a student |
| `POST` | `/api/reset` | Clear all student data (Neo4j + MongoDB) |
| `GET` | `/api/teacher/{id}/students` | Get teacher's monitored students |
| `POST` | `/api/teacher/{id}/students` | Add student to teacher's list |
| `DELETE` | `/api/teacher/{id}/students/{sid}` | Remove student from teacher's list |
| `GET` | `/api/teacher/student/{id}/progress` | Full student progress report |

---

## 📂 Project Structure

```
.
├── README.md
├── ARCHITECTURE.md                    # Agent naming conventions
├── pyproject.toml                     # Dependencies (uv)
├── render.yaml                        # Render deployment config
├── test_startup.py                    # Quick import smoke test
├── test_openAI.py                     # OpenAI connectivity test
├── .env                               # Credentials (gitignored)
│
├── public/                            # Static web UI
│   ├── index.html                     # Main SPA (Tailwind + vanilla JS)
│   ├── js/
│   │   └── app.js                     # Chat, sessions, roadmap, teacher logic
│   └── css/
│       └── styles.css                 # Custom CSS (blobs, animations)
│
├── scripts/                           # Knowledge graph seed scripts
│   ├── seed_os_knowledge.py           # OS curriculum: 12 concepts, 12 edges, PDF chunks
│   └── seed_api_knowledge.py          # API curriculum: 11 concepts, 17 edges, PDF chunks
│
├── data/                              # Evaluation reports (JSON)
│   ├── eval_router_report.json        # Router eval (OS) — optimized
│   ├── eval_router_report_baseline.json
│   ├── eval_router_api_report.json    # Router eval (API) — optimized
│   ├── eval_router_api_report_baseline.json
│   ├── eval_diagnoser_report.json     # Diagnoser eval (OS) — optimized
│   ├── eval_diagnoser_report_baseline.json
│   ├── eval_diagnoser_api_report.json # Diagnoser eval (API) — optimized
│   ├── eval_diagnoser_api_report_baseline.json
│   ├── eval_pathsim_ablation_report.json  # PathSim MSMS vs BFS (OS)
│   ├── eval_pathsim_api_report.json       # PathSim (API)
│   ├── eval_ragas_ablation_report.json    # RAGAS Hybrid vs Vector (OS)
│   ├── eval_ragas_ablation_report_baseline.json
│   ├── eval_ragas_api_report.json         # RAGAS Hybrid vs Vector (API)
│   └── eval_ragas_api_report_baseline.json
│
├── data_md/                           # Pre-parsed textbook chapters (markdown)
│
├── src/
│   ├── agents/                        # LangGraph multi-agent workflow
│   │   ├── workflow.py                # Graph builder + CLI entry point
│   │   ├── state.py                   # AgentState TypedDict
│   │   ├── router_agent.py            # Few-shot CoT semantic routing (diagnose | retrieve)
│   │   ├── diagnoser_agent.py         # Misconception detection + dynamic KG concept resolution
│   │   ├── planner_agent.py           # MSMS-based learning path generation
│   │   ├── tutor_agent.py             # Context-aware response synthesis
│   │   ├── tools.py                   # LangChain tools (retrieval, memory, mastery)
│   │   └── llm.py                     # OpenAI model configuration
│   │
│   ├── api/
│   │   ├── server.py                  # FastAPI server (REST + SSE streaming)
│   │   ├── dependencies.py            # Shared FastAPI dependencies
│   │   ├── controllers/               # Business logic controllers
│   │   └── routes/                    # Modular route definitions
│   │       ├── auth_routes.py         # Authentication endpoints
│   │       ├── chat_routes.py         # Chat / SSE streaming
│   │       ├── sessions_routes.py     # Session CRUD
│   │       ├── graph_routes.py        # Knowledge graph & mastery
│   │       ├── documents_routes.py    # PDF upload & management
│   │       ├── teacher_routes.py      # Teacher dashboard
│   │       ├── media_routes.py        # Video recommendations
│   │       └── ui_routes.py           # Static file serving
│   │
│   ├── ui/
│   │   └── streamlit_app.py           # Streamlit dashboard
│   │
│   ├── graph/
│   │   ├── db.py                      # Neo4j connection wrapper
│   │   ├── student.py                 # StudentManager (mastery, memory, CRUD)
│   │   └── models.py                  # Domain models
│   │
│   ├── retrieval/
│   │   ├── hybrid.py                  # Hybrid retrieval pipeline (vector + graph topology)
│   │   ├── search.py                  # Semantic vector search (Neo4j vector index)
│   │   ├── embedder.py                # Concept embedding with SentenceTransformers
│   │   ├── reranker.py                # Structure-aware reranker (calibrated weights)
│   │   ├── compressor.py              # Contextual compression with min-length protection
│   │   ├── crag.py                    # Corrective RAG — self-correction loop
│   │   └── query_transform.py         # HyDE query transformation
│   │
│   ├── pathing/
│   │   ├── graph_adapter.py           # Neo4j → NetworkX adapter
│   │   ├── state.py                   # StateModeler (source/sink identification)
│   │   ├── msms.py                    # Multi-Source Multi-Sink optimizer
│   │   └── roadmap.py                 # High-level roadmap computation
│   │
│   ├── ingestion/
│   │   ├── pdf_pipeline.py            # PDF → chunked embeddings → Neo4j
│   │   ├── parser.py                  # Text extraction & parsing
│   │   └── builder.py                 # Graph construction from parsed data
│   │
│   ├── evaluation/
│   │   └── pathsim.py                 # PathSim evaluation metric
│   │
│   └── storage/
│       └── qa_store.py                # MongoDB persistence + session management
│
└── tests/
    ├── data/                          # Ground-truth evaluation datasets
    │   ├── router_eval_dataset.json       # 50 labeled queries (OS)
    │   ├── router_eval_dataset_api.json   # 50 labeled queries (API)
    │   ├── diagnoser_eval_dataset.json    # 30 cases: 15 misconceptions + 15 TNs (OS)
    │   ├── diagnoser_eval_dataset_api.json# 30 cases: 15 misconceptions + 15 TNs (API)
    │   ├── ragas_eval_dataset.json        # 15 multi-hop Q&A pairs (OS)
    │   └── ragas_eval_dataset_api.json    # 20 technical Q&A pairs (API)
    │
    ├── eval_router.py                 # Router accuracy, F1, Cohen's Kappa evaluation
    ├── eval_diagnoser.py              # Diagnoser precision, recall, F1, concept attribution
    ├── eval_pathsim_ablation.py       # PathSim MSMS vs BFS ablation (OS)
    ├── eval_pathsim_api.py            # PathSim evaluation (API)
    ├── eval_ragas_ablation.py         # RAGAS Hybrid vs Vector-Only ablation
    │
    ├── test_pathsim.py                # Legacy PathSim test
    ├── test_ragas_eval.py             # Legacy RAGAS test
    ├── test_router_metrics.py         # Legacy Router test
    └── test_scenario.py               # End-to-end scenario tests
```

---

## 🗄️ Data Model

### MongoDB — Q&A Sessions (database: `graphmasal`)

**Collections**:

#### `sessions`
| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | string | UUID primary key (unique index) |
| `student_id` | string | Student identifier |
| `topic` | string | Session topic |
| `created_at` | string | ISO 8601 timestamp |
| `updated_at` | string | ISO 8601 timestamp |
| `active_plan` | array | Ordered concept IDs for the learning plan |
| `plan_id` | string | Selected plan identifier |

#### `qa_sessions` (turns)
| Field | Type | Purpose |
|-------|------|---------|
| `session_id` | string | Links to parent session |
| `student_id` | string | Student identifier |
| `timestamp` | string | ISO 8601 timestamp |
| `user_input` | string | Student's question |
| `final_response` | string | Tutor's answer |
| `route` | string | `diagnose` or `retrieve` |
| `route_reason` | string | Router's justification |
| `misconception` | int | 1 if detected, 0 otherwise |
| `affected_concepts` | array | Affected concept IDs |
| `learning_paths` | array | Generated learning sequences |
| `retrieved_context` | string | Knowledge graph retrieval context |
| `response_time_ms` | int | Wall-clock latency |
| `model_used` | string | LLM model name |

#### `teachers`
| Field | Type | Purpose |
|-------|------|---------|
| `teacher_id` | string | Teacher identifier (unique index) |
| `student_ids` | array | List of monitored student IDs |

### Neo4j — Knowledge Graph

**Nodes**:
- `:Student` — `id`, `name`, proficiency metrics
- `:Concept` — `id`, `name`, `description`, `embedding` (384-dim vector)
- `:Memory` — historical interaction records
- `:PDFDocument` — uploaded textbook metadata
- `:PDFChunk` — embedded text chunks from ingested PDFs

**Relationships**:
- `(:Student)-[:HAS_MASTERY_OF]->(:Concept)` — mastery score (0.0–1.0)
- `(:Concept)-[:IS_PREREQUISITE_FOR]->(:Concept)` — prerequisite ordering
- `(:Student)-[:REMEMBERS]->(:Memory)` — long-term memory
- `(:Student)-[:HAS_UPLOADED]->(:PDFDocument)` — PDF ownership
- `(:Student)-[:HAS_EXTRACTED]->(:Concept)` — concept extraction link
- `(:PDFDocument)-[:HAS_CHUNK]->(:PDFChunk)` — document to chunk

---

## ⚙️ Configuration

### LLM Model

Default: `gpt-3.5-turbo` via OpenAI.

```env
GRAPHMASAL_OPENAI_MODEL=gpt-4o-mini
# or
OPENAI_CHAT_MODEL=gpt-4
```

### MongoDB

Default: `mongodb://localhost:27017` (database: `graphmasal`).

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=YourApp
```

### LangSmith Tracing

1. Sign up at [smith.langchain.com](https://smith.langchain.com/)
2. Set in `.env`:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_your_key_here
   LANGCHAIN_PROJECT=graphmasal
   ```
3. Run the application — all traces appear in your dashboard

---

## 🧪 Testing & Evaluation

### Seed & Run Full Evaluation Suite

```bash
# 1. Seed the knowledge graph (pick one or both)
uv run python scripts/seed_os_knowledge.py
uv run python scripts/seed_api_knowledge.py

# 2. Run evaluations
uv run python tests/eval_router.py              # OS Router (50 queries)
uv run python tests/eval_router.py --api         # API Router (50 queries)
uv run python tests/eval_diagnoser.py            # OS Diagnoser (30 cases)
uv run python tests/eval_diagnoser.py --api      # API Diagnoser (30 cases)
uv run python tests/eval_pathsim_ablation.py     # OS PathSim MSMS vs BFS
uv run python tests/eval_pathsim_api.py          # API PathSim
uv run python tests/eval_ragas_ablation.py       # OS RAGAS Hybrid vs Vector
uv run python tests/eval_ragas_ablation.py --api  # API RAGAS Hybrid vs Vector
```

All results are saved to `data/eval_*_report.json`. Baseline reports are preserved as `data/eval_*_baseline.json` for publication comparison.

### Quick Legacy Tests

```bash
uv run python tests/test_pathsim.py          # PathSim against expert paths
uv run python tests/test_ragas_eval.py       # RAGAS RAG quality metrics
uv run python tests/test_router_metrics.py   # Router accuracy & latency
uv run pytest tests/                         # Run all tests
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Failed to connect to Neo4j instance"** | Check Neo4j credentials in `.env`. Ensure your Aura instance is running. |
| **OpenAI API errors** | Verify `OPENAI_API_KEY` is set and has available quota. |
| **MongoDB connection failed** | Verify `MONGO_URI` in `.env`. For Atlas, whitelist your IP address. |
| **"No relevant concepts found"** | Run `scripts/seed_os_knowledge.py` or upload PDFs and run concept extraction. |
| **LangSmith not capturing traces** | Ensure `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` is set. |
| **Streamlit won't start** | Run from the project root: `uv run streamlit run src/ui/streamlit_app.py` |
| **Low evaluation metrics** | Ensure Neo4j is seeded with the correct curriculum before running domain-specific evals. |

---

## 🤝 Contributing

1. Fork and create a feature branch
2. Follow the [ARCHITECTURE.md](ARCHITECTURE.md) naming conventions (`*_agent.py`, `*_node`, PascalCase logging)
3. Add tests in `tests/` and ground-truth datasets in `tests/data/`
4. Submit a PR with example traces or evaluation results

---

## 📄 License

MIT License

---

**Last Updated**: October 2026
**Version**: 1.0.0
