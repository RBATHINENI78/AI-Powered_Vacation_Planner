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

# Add custom routes for file downloads
try:
    from fastapi import FastAPI
    from agents_web.vacation_planner.custom_server import add_custom_routes

    # This will be called by ADK web server if it supports custom route injection
    def setup_app(app: FastAPI):
        """Setup custom routes for the web app"""
        add_custom_routes(app)
except ImportError:
    pass  # FastAPI not available in this context
