# GraphMASAL — Graph-Based Multi-Agent Adaptive Student Learning

An intelligent tutoring system that combines **multi-agent LangGraph orchestration**, **Neo4j knowledge graphs**, and **adaptive learning paths** to personalize OS (Operating Systems) education.

## Features

### 🎯 Multi-Agent Workflow
- **Router**: Classifies student queries into diagnostic or retrieval pathways
- **Diagnoser**: Detects misconceptions and resets student mastery
- **Planner**: Generates mathematically optimal learning paths using graph algorithms
- **Tutor**: Synthesizes responses with retrieval context and memory

### 🧠 Knowledge Management
- **Neo4j Knowledge Graph**: Concepts, prerequisites, unlocks, and student mastery
- **Hybrid Retrieval**: Vector similarity + graph neighborhoods + reranking
- **Long-term Memory**: Stores and recalls previous interactions per student

### 💾 Q&A Persistence & Analytics
- **SQLite Q&A Store**: Every query/answer turn is persisted with full agent state
  - Route decisions (diagnose vs. retrieve)
  - Misconception flags and affected concepts
  - Generated learning paths and retrieval context
  - Response times and model metadata
- **Built-in Analytics**: Session summaries, misconception analysis, route distribution

### 🔍 LangSmith Tracing
- Automatic tracing of every LLM call and tool invocation
- Per-session tracing with metadata tags
- Dashboard visualization at [smith.langchain.com](https://smith.langchain.com/)
- Traces all agent state transitions and data flow

## Architecture

```
workflow.py (entry point)
  ├─ Router → classifies query
  ├─ Diagnoser → detects misconceptions  ───┐
  ├─ Planner → generates learning paths  ───┤
  └─ Tutor → synthesizes response ◄─────────┘

Backing Services:
  ├─ Neo4j (Graph)          [student mastery, concepts, prerequisites]
  ├─ SQLite (Q&A Store)     [query/answer history + agent analysis]
  ├─ Ollama (LLM)           [local inference, configurable model]
  └─ LangSmith (Tracing)    [debug + monitor agent behavior]
```

## Setup

### Prerequisites
- Python 3.12+
- Ollama (for local LLM inference)
- Neo4j Aura instance (cloud database)

### 1. Clone & Install

```bash
cd GraphMASAL
uv sync  # Install dependencies from pyproject.toml
```

### 2. Configure Environment

Copy the template and fill in credentials:

```bash
cp .env.example .env  # or create a new .env
```

Required variables (in `.env`):
```
NEO4J_URI=neo4j+s://your-aura-instance.databases.neo4j.io
NEO4J_USERNAME=your-username
NEO4J_PASSWORD=your-password

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=false       # Set to true to enable
LANGCHAIN_API_KEY=lsv2_pt_...    # Get from smith.langchain.com
LANGCHAIN_PROJECT=graphmasal
```

### 3. Start Ollama

Ensure Ollama is running with a model:
```bash
ollama serve
# In another terminal: ollama pull llama3.2:1b
```

Override the model via environment or code:
```bash
GRAPHMASAL_OLLAMA_MODEL=llama2  # Or any Ollama model
GRAPHMASAL_OLLAMA_NUM_CTX=4096
```

## Usage

### Interactive Tutoring CLI

```bash
cd src/agents
uv run workflow.py
```

The system will:
1. Pre-configure a student (Alice, student_123)
2. Initialize the SQLite Q&A database
3. Show the session ID (for grouping traces)
4. Prompt for user questions

Example interaction:
```
[Alice]: What is paging?
[System]: Thinking...
[Storage]: Turn saved (row 42, 1250 ms)
[AI Tutor]: Paging is a memory management technique that divides...
```

### Query Q&A Analytics

After running a session, analyze interactions in Python:

```python
from src.storage.qa_store import (
    get_student_summary,
    get_route_distribution,
    get_recent_turns,
    get_misconception_analysis
)

# Overall student statistics
summary = get_student_summary("student_123")
print(f"Total turns: {summary['total_turns']}")
print(f"Misconceptions detected: {summary['total_misconceptions']}")
print(f"Avg response time: {summary['avg_response_ms']:.0f} ms")

# Route breakdown (diagnose vs retrieve)
routes = get_route_distribution("student_123")
print(f"Routes: {routes}")

# Recent interactions
turns = get_recent_turns("student_123", limit=5)
for turn in turns:
    print(f"Q: {turn['user_input']}")
    print(f"Route: {turn['route']}, Time: {turn['response_time_ms']} ms\n")

# All misconceptions
misconceptions = get_misconception_analysis("student_123")
for m in misconceptions:
    print(f"Misconception at {m['timestamp']}")
    print(f"Affected: {m['affected_concepts']}")
    print(f"Learning path: {m['learning_paths']}\n")
```

## Database Schema

### Q&A Sessions Table (`data/qa_sessions.db`)

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER | Auto-increment row ID |
| `session_id` | TEXT | UUID grouping all turns in one CLI session |
| `student_id` | TEXT | Student identifier (e.g., "student_123") |
| `timestamp` | TEXT | ISO 8601 UTC timestamp |
| `user_input` | TEXT | Student's question or message |
| `final_response` | TEXT | Tutor's answer |
| `route` | TEXT | "diagnose" or "retrieve" |
| `route_reason` | TEXT | Why the router chose this path |
| `misconception` | INTEGER | 1 if detected, 0 otherwise |
| `affected_concepts` | TEXT | JSON array of affected concept IDs |
| `learning_paths` | TEXT | JSON array of generated learning sequences |
| `retrieved_context` | TEXT | Knowledge graph retrieval context |
| `response_time_ms` | INTEGER | Wall-clock latency |
| `model_used` | TEXT | LLM model name and context size |
| `langsmith_run_id` | TEXT | Link to LangSmith trace (if enabled) |

**Indexes**: `student_id`, `session_id`, `timestamp`

### Neo4j Graph (Student Knowledge)

**Nodes**:
- `:Student` — ID, name, proficiency metrics
- `:Concept` — concept ID, name, embedding vector
- `:Memory` — historical interaction records

**Relationships**:
- `Student -[HAS_MASTERY]-> Concept` (score: 0.0–1.0)
- `Concept -[PREREQUISITE]-> Concept`
- `Student -[REMEMBERS]-> Memory`

## Configuration

### Ollama Models

Default: `llama3.2:1b` with `num_ctx=2048`

Change via environment:
```bash
GRAPHMASAL_OLLAMA_MODEL=llama2
GRAPHMASAL_OLLAMA_NUM_CTX=4096
```

Or programmatically in `src/agents/llm.py`:
```python
DEFAULT_OLLAMA_MODEL = "your-model:tag"
DEFAULT_OLLAMA_CONTEXT = 4096
```

### LangSmith Tracing

1. Sign up at [smith.langchain.com](https://smith.langchain.com/) and get an API key
2. Set in `.env`:
   ```
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_your_key_here
   LANGCHAIN_PROJECT=graphmasal
   ```
3. Run the workflow — all traces appear in your dashboard

### Q&A Database Path

Default: `data/qa_sessions.db`

Override via:
```bash
GRAPHMASAL_QA_DB=/custom/path/qa_sessions.db
```

Or in code:
```python
import os
os.environ["GRAPHMASAL_QA_DB"] = "/path/to/db"

from src.storage.qa_store import init_db
init_db()
```

## Project Structure

```
.
├── README.md                          # This file
├── pyproject.toml                     # Dependencies (uv)
├── .env                               # Credentials (Neo4j, LangSmith)
├── data/
│   └── qa_sessions.db                 # SQLite Q&A store (auto-created)
└── src/
    ├── agents/                        # LangGraph workflow
    │   ├── workflow.py                # Main orchestrator + CLI entry
    │   ├── state.py                   # AgentState TypedDict
    │   ├── router.py                  # Route (diagnose|retrieve)
    │   ├── diagnoser.py               # Misconception detection
    │   ├── plannerpy                  # Learning path generation
    │   ├── tutor.py                   # Conversational response
    │   ├── tools.py                   # LangChain tools (retrieval, memory)
    │   └── llm.py                     # Ollama configuration
    ├── storage/
    │   └── qa_store.py                # SQLite persistence + analytics
    ├── graph/
    │   ├── db.py                      # Neo4j connection
    │   ├── student.py                 # StudentManager (mastery, memory)
    │   └── models.py                  # Domain models
    ├── retrieval/
    │   ├── hybrid.py                  # Hybrid retrieval pipeline
    │   └── search.py                  # Semantic search
    ├── pathing/
    │   ├── graph_adapter.py           # Neo4j → NetworkX
    │   ├── state.py                   # StateModeler (sources/sinks)
    │   └── msms.py                    # Multi-Source Multi-Sink optimizer
    ├── ingestion/
    │   └── ...                        # Knowledge graph ingestion
    └── evaluation/
        └── pathsim.py                 # Evaluation metrics
```

## Key Components

### Router (`src/agents/router.py`)
- Analyzes student input for diagnostic cues ("confused", "mistake", "help")
- Calls LLM to classify as `diagnose` or `retrieve`
- Recalls long-term memory for context

### Diagnoser (`src/agents/diagnoser.py`)
- Detects misconceptions via LLM analysis
- Resets affected concept mastery to 0.0
- Captures affected concepts and root cause

### Planner (`src/agents/planner.py`)
- Calls `MSMSOptimizer` to compute optimal learning path
- Uses graph structure and student mastery as inputs
- Outputs ordered concept sequence to learn

### Tutor (`src/agents/tutor.py`)
- Main conversational interface
- Adapts response based on route context:
  - **diagnose**: Gentle correction + learning path
  - **retrieve**: Direct answer + encouragement
- Stores interaction in long-term memory

### Q&A Store (`src/storage/qa_store.py`)
- Persists all turns to SQLite
- Provides analytics functions:
  - `get_student_summary()` — aggregate stats
  - `get_route_distribution()` — route breakdown
  - `get_recent_turns()` — recent interactions
  - `get_misconception_analysis()` — misconception history

## Extending the System

### Add a New Agent
1. Create `src/agents/my_agent.py` with a node function:
   ```python
   def my_agent_node(state: AgentState):
       # Process state, call LLM, return updated state
       return {"new_field": "value"}
   ```
2. Add to graph in `workflow.py`:
   ```python
   graph_builder.add_node("MyAgent", my_agent_node)
   ```

### Add Memory Types
Edit `src/graph/student.py` to expand `store_memory()` logic and define new `memory_type` strings.

### Customize Retrieval
Modify `src/retrieval/hybrid.py` to tweak ranking, add filters, or change reranking algorithms.

## Troubleshooting

### "Failed to create the driver"
- Check Neo4j credentials in `.env`
- Ensure your Aura instance is running
- Verify network connectivity to `neo4j+s://...`

### Ollama timeout
- Start Ollama: `ollama serve`
- Check model is loaded: `ollama list`
- Increase context: `GRAPHMASAL_OLLAMA_NUM_CTX=4096`

### "No relevant concepts found"
- Check knowledge graph is populated (run ingestion pipeline)
- Verify Neo4j indexes are created (run `db.initialize_schema()`)

### LangSmith not capturing traces
- Ensure `LANGCHAIN_TRACING_V2=true` in `.env`
- Verify `LANGCHAIN_API_KEY` is set correctly (not empty)
- Check [smith.langchain.com](https://smith.langchain.com/) dashboard for project `graphmasal`

## Testing & Evaluation

Run the evaluation suite:
```bash
cd src/evaluation
uv run pathsim.py
```

Analyze a student session:
```bash
python3 -c "
from src.storage.qa_store import get_student_summary, get_misconception_analysis
summary = get_student_summary('student_123')
print(summary)
misconceptions = get_misconception_analysis('student_123')
print(f'Misconceptions: {len(misconceptions)}')
"
```

## Contributing

1. Fork and branch
2. Add tests in `tests/`
3. Ensure all graph operations use proper constraints and indexes
4. Document new analytics functions in Q&A store
5. Submit PR with example traces from `smith.langchain.com`

## License

MIT License (replace with your license)

## Contact & Support

For issues or questions:
- GitHub Discussions
- Email: [contact info]

---

**Last Updated**: March 2026  
**Version**: 0.1.0
