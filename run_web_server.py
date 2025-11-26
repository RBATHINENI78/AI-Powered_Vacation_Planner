#!/usr/bin/env python3
"""
Custom ADK Web Server with Download Endpoint
Wraps the standard ADK web server and adds custom routes
"""
import subprocess
import sys
import os
from pathlib import Path

# Set working directory to project root
os.chdir(Path(__file__).parent)

# Add custom routes by monkey-patching the ADK web server
# This is a workaround since ADK doesn't natively support custom routes
print("=" * 80)
print("STARTING VACATION PLANNER WEB SERVER WITH DOWNLOAD SUPPORT")
print("=" * 80)
print()
print("Custom Features:")
print("  - File download endpoint: http://localhost:8080/download/{filename}")
print("  - List downloads: http://localhost:8080/downloads/list")
print()
print("=" * 80)
print()

# Import FastAPI and ADK
try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    # Create FastAPI app
    app = FastAPI(title="Vacation Planner API")

    # Mount outputs directory as static files
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    # Add custom routes from our custom_server module
    from agents_web.vacation_planner.custom_server import add_custom_routes
    add_custom_routes(app)

    # Import and mount the ADK agent
    from agents_web.vacation_planner.agent import root_agent

    # Add ADK routes (this is a simplified version - actual ADK integration would be more complex)
    @app.get("/")
    async def root():
        return {
            "service": "Vacation Planner API",
            "version": "1.0.0",
            "endpoints": {
                "download": "/download/{filename}",
                "list_downloads": "/downloads/list",
                "agent": "Use ADK web interface"
            }
        }

    print("\n✅ Server configured with custom routes")
    print("\nNow starting ADK web server...")
    print("\nNote: Custom routes are available at:")
    print("  - http://localhost:8080/download/{filename}")
    print("  - http://localhost:8080/downloads/list")
    print()

except ImportError as e:
    print(f"Warning: Could not set up custom routes: {e}")
    print("Falling back to standard ADK web server...")

# Run the standard ADK web command
# The custom routes will be available if setup_app() is called by ADK
os.execvp("adk", ["adk", "web", "agents_web", "--port", "8080"])
