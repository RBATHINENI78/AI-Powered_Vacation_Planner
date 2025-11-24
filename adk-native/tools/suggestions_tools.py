"""
Suggestions Checkpoint Tool
Returns a pause signal to stop workflow for user approval
"""

from typing import Dict, Any


def check_user_approval() -> Dict[str, Any]:
    """
    Signal that user approval is required before continuing.

    This function ALWAYS returns a status requiring user input,
    which should pause the workflow until the user approves.

    Returns:
        Dict with status="needs_user_input" to pause workflow
    """
    return {
        "status": "needs_user_input",
        "message": "⛔ User approval required before generating detailed itinerary",
        "instruction": """
Please review the trip overview above and respond with one of:

1. **"Proceed"** - Continue with detailed day-by-day itinerary
2. **"Change [specific aspect]"** - Modify something (e.g., "change hotels to mid-range", "extend to 3 weeks")
3. **"Questions"** - Ask about any unclear points

⛔ The workflow is PAUSED waiting for your response.
""",
        "pause_workflow": True
    }
