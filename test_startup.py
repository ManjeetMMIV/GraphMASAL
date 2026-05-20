import os
import sys

print("Setting up path...")
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

print("1. import llm")
from src.agents import llm
print("2. import state")
from src.agents import state
print("3. import router_agent")
from src.agents import router_agent
print("4. import diagnoser_agent")
from src.agents import diagnoser_agent
print("5. import planner_agent")
from src.agents import planner_agent
print("6. import tutor_agent")
from src.agents import tutor_agent
print("7. import qa_store")
from src.storage import qa_store
print("done")
