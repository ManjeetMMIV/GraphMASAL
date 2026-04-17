# System Architecture & Conventions

This document outlines the core structural conventions established for the GraphMASAL project, specifically detailing the nomenclature and file structures for the AI agents driving the backend logic.

## 1. Agent Naming Convention

To ensure clarity, predictability, and maintainability across the codebase, a three-tier naming convention is strictly enforced for the routing, diagnostic, planning, and tutoring components.

### 1.1 File Naming (`snake_case`)
Files encapsulating agent logic are suffixed with `_agent.py` to clearly distinguish them from standard utility or tool files. 

- `router_agent.py`
- `diagnoser_agent.py`
- `planner_agent.py`
- `tutor_agent.py`

### 1.2 Function/Node Naming (`snake_case`)
The main entry point function for each module that participates in the LangGraph workflow is suffixed with `_node`. This visually indicates that the function signature adheres to the `StateGraph` node standard (i.e., taking an `AgentState` and returning a state delta).

- `def router_node(state: AgentState)`
- `def diagnoser_node(state: AgentState)`
- `def planner_node(state: AgentState)`
- `def tutor_node(state: AgentState)`

### 1.3 Conceptual & Logging Naming (`PascalCase`)
When referring to the agents contextually within documentation, system prompts, tracing, and user-facing logs, the formalized, capitalized noun is used. This distinguishes the overarching "Actor" abstraction from the technical implementation.

- **Router Agent** (or Router)
- **Diagnoser Agent** (or Diagnoser)
- **Planner Agent** (or Planner)
- **Tutor Agent** (or Tutor)

## 2. Rationale
Adhering to these conventions accomplishes several architectural goals:
1. **Discoverability**: Prefixing agent logic files allows developers to rapidly locate core execution boundaries across a growing repository.
2. **Predictability**: Uniform function signatures coupled with uniform naming (`*_node`) simplifies extending the underlying LangGraph pipeline.
3. **Traceability**: Consistent logging paradigms (`[Tutor Agent] Initiating...`) provide clear origin markers in the terminal and MongoDB databases when debugging dynamic conversations.
