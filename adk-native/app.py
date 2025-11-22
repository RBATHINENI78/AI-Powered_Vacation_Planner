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

# Create the ADK app with the main vacation planner agent
app = App(
    name="Vacation Planner",
    agent=vacation_planner,
    description="""AI-Powered Vacation Planner

    Plan your perfect vacation with comprehensive research, booking estimates,
    and detailed itineraries.

    This planner includes:
    - Travel advisory checking (State Dept + travel bans)
    - Weather analysis and packing recommendations
    - Visa and immigration requirements
    - Budget planning and currency conversion
    - Flight, hotel, and car rental cost estimation
    - Activity and attraction recommendations
    - Daily itinerary generation
    - Complete travel document creation

    Just tell me where you want to go, when, and your budget!

    Example: "Plan a trip to Paris, France from December 1-7, 2025 for 2 people with a $3000 budget"
    """,
)


if __name__ == "__main__":
    print("="*80)
    print("VACATION PLANNER - ADK APP")
    print("="*80)
    print("\n[AGENT]")
    print(f"  Name: {app.agent.name}")
    print(f"  Description: {app.description[:100]}...")
    print(f"  Sub-agents: {len(app.agent.sub_agents)} phases")

    print("\n[TO RUN WEB UI]")
    print("  adk web")

    print("\n[TO RUN CLI]")
    print("  adk run")

    print("\n[TO RUN API SERVER]")
    print("  adk api_server")

    print("\n" + "="*80)
