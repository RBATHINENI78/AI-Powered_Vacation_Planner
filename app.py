"""
Vacation Planner ADK App
Entry point for ADK web interface and API server
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.apps import App
from workflows.vacation_workflow import vacation_planner
from callbacks.logging_callbacks import before_agent_callback, after_agent_callback

# Create the ADK app with the main vacation planner agent
app = App(
    name="vacation_planner",
    root_agent=vacation_planner,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)


if __name__ == "__main__":
    print("="*80)
    print("VACATION PLANNER - ADK APP")
    print("="*80)
    print("\n[AGENT]")
    print(f"  Name: {app.root_agent.name}")
    print(f"  Sub-agents: {len(app.root_agent.sub_agents)} phases")

    print("\n[TO RUN WEB UI]")
    print("  adk web")

    print("\n[TO RUN CLI]")
    print("  adk run")

    print("\n[TO RUN API SERVER]")
    print("  adk api_server")

    print("\n" + "="*80)
