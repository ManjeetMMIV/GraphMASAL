# GraphMASAL — Graph-Based Multi-Agent System for Adaptive Student Learning
deployed link : https://graphmasal-3.onrender.com/
An intelligent tutoring system that combines **multi-agent LangGraph orchestration**, **Neo4j knowledge graphs**, and **adaptive learning paths** to personalize Operating Systems education.

> Built as part of an academic project exploring how graph-based AI agents can detect misconceptions, plan learning sequences, and deliver personalized tutoring at scale.

---
<img width="1535" height="786" alt="image" src="https://github.com/user-attachments/assets/8cc381d1-7df9-4e79-94d2-43270ba3486a" />
<img width="1362" height="603" alt="image" src="https://github.com/user-attachments/assets/65d2540b-65b6-4456-aa7b-8457cd89872d" />




## ✨ Features

### 🤖 Multi-Agent Workflow (LangGraph)
- **Router Agent** — Classifies student queries into `diagnose` or `retrieve` pathways using LLM analysis and long-term memory recall
- **Diagnoser Agent** — Detects misconceptions via LLM reasoning, resets affected concept mastery to 0.0
- **Planner Agent** — Generates mathematically optimal learning paths using the Multi-Source Multi-Sink (MSMS) graph algorithm
- **Tutor Agent** — Synthesizes context-aware responses adapted to the student's route (gentle correction vs. direct answer)

### 🧠 Knowledge Graph (Neo4j)
- **Concept nodes** with descriptions, embeddings, and prerequisite relationships
- **Student nodes** tracking per-concept mastery scores (0.0–1.0)
- **Long-term memory** storing and recalling previous interactions per student
- **Vector similarity index** for semantic search over concept embeddings

### 🔍 Hybrid Retrieval Pipeline
- **Semantic search** using `all-MiniLM-L6-v2` sentence embeddings
- **Graph neighborhood expansion** pulling in prerequisite and downstream concepts
- **Structure-aware reranking** with optional cross-encoder (`ms-marco-MiniLM-L-6-v2`)

### 📄 PDF Ingestion Pipeline
- Upload OS textbook PDFs and automatically chunk, embed, and store them in Neo4j
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

### 🧪 Evaluation Suite
- **PathSim** — Evaluates AI-generated learning paths against expert-defined ground truth (node overlap, edge overlap, sequence similarity)
- **RAGAS Evaluation** — Measures RAG pipeline quality: faithfulness, answer relevancy, context precision, context recall, answer correctness
- **Router Metrics** — Routing accuracy and latency-per-route benchmarks against ground-truth labeled test cases

### 🔍 LangSmith Tracing
- Automatic tracing of every LLM call and tool invocation
- Per-session metadata tags and dashboard visualization
- Traces all agent state transitions and data flow

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

### 3. Verify Setup

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

The FastAPI server (`src/api/server.py`) exposes the following endpoints:

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
├── test_startup.py                    # Quick import smoke test
├── test_openAI.py                     # OpenAI connectivity test
├── .env                               # Credentials (gitignored)
│
├── public/                            # Static web UI
│   ├── index.html                     # Main SPA (Tailwind + vanilla JS)
│   ├── app.js                         # Chat, sessions, roadmap, teacher logic
│   └── styles.css                     # Custom CSS (blobs, animations)
│
├── data/
│   ├── qa_sessions.db                 # Legacy SQLite (unused, kept for reference)
│   ├── ragas_eval_report.json         # RAGAS evaluation results
│   └── router_eval_report.json        # Router accuracy evaluation results
│
├── data_md/                           # Pre-parsed textbook chapters (markdown)
│
├── src/
│   ├── agents/                        # LangGraph multi-agent workflow
│   │   ├── workflow.py                # Graph builder + CLI entry point
│   │   ├── state.py                   # AgentState TypedDict
│   │   ├── router_agent.py            # Route classification (diagnose | retrieve)
│   │   ├── diagnoser_agent.py         # Misconception detection & mastery reset
│   │   ├── planner_agent.py           # MSMS-based learning path generation
│   │   ├── tutor_agent.py             # Context-aware response synthesis
│   │   ├── tools.py                   # LangChain tools (retrieval, memory)
│   │   └── llm.py                     # OpenAI model configuration
│   │
│   ├── api/
│   │   └── server.py                  # FastAPI server (REST + SSE streaming)
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
│   │   ├── hybrid.py                  # Hybrid retrieval pipeline
│   │   ├── search.py                  # Semantic vector search
│   │   ├── embedder.py                # Concept embedding with SentenceTransformers
│   │   └── reranker.py                # Structure-aware reranker (+ cross-encoder)
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
    ├── data/
    │   ├── ragas_eval_dataset.json     # Ground truth Q&A for RAGAS
    │   └── router_eval_dataset.json    # Ground truth for router classification
    ├── test_pathsim.py                # PathSim evaluation against expert paths
    ├── test_ragas_eval.py             # RAGAS RAG quality metrics
    ├── test_router_metrics.py         # Router accuracy & latency benchmarks
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

### Run All Tests

```bash
uv run pytest tests/
```

### PathSim — Learning Path Quality

Evaluates AI-generated learning paths against expert-defined ground truth using a weighted combination of node overlap, edge overlap, and sequence similarity:

```bash
uv run python tests/test_pathsim.py
```

### RAGAS — RAG Pipeline Quality

Measures faithfulness, answer relevancy, context precision, context recall, and answer correctness:

```bash
uv run python tests/test_ragas_eval.py
uv run python tests/test_ragas_eval.py --max 5    # Quick run (5 questions)
```

Results are saved to `data/ragas_eval_report.json`.

### Router Metrics — Routing Accuracy & Latency

Benchmarks the router agent against labeled test cases:

```bash
uv run python tests/test_router_metrics.py
```

Results are saved to `data/router_eval_report.json`.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Failed to connect to Neo4j instance"** | Check Neo4j credentials in `.env`. Ensure your Aura instance is running. |
| **OpenAI API errors** | Verify `OPENAI_API_KEY` is set and has available quota. |
| **MongoDB connection failed** | Verify `MONGO_URI` in `.env`. For Atlas, whitelist your IP address. |
| **"No relevant concepts found"** | Upload PDFs and run concept extraction to populate the knowledge graph. |
| **LangSmith not capturing traces** | Ensure `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` is set. |
| **Streamlit won't start** | Run from the project root: `uv run streamlit run src/ui/streamlit_app.py` |

---

## 🤝 Contributing

1. Fork and create a feature branch
2. Follow the [ARCHITECTURE.md](ARCHITECTURE.md) naming conventions (`*_agent.py`, `*_node`, PascalCase logging)
3. Add tests in `tests/`
4. Submit a PR with example traces or screenshots

---

## 📄 License

MIT License

---

**Last Updated**: August 2026
**Version**: 0.1.0
