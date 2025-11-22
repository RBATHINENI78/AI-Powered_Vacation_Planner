"""
Vacation Planner Agent for ADK Web Interface
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=root_dir / '.env')

# Import the main vacation planner agent
from workflows.vacation_workflow import vacation_planner

# Export the agent for ADK web (must be named root_agent)
root_agent = vacation_planner
