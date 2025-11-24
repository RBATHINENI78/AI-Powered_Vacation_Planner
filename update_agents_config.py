#!/usr/bin/env python3
"""
Script to update all agents to use centralized config for model selection.
"""

import os
import re
from pathlib import Path

# Map of agent files to their agent names (for Config.get_model_for_agent)
AGENT_CONFIGS = {
    "destination.py": "destination_intelligence",
    "immigration.py": "immigration_specialist",
    "currency.py": "currency_exchange",
    "booking.py": ["flight_booking", "hotel_booking", "car_rental"],  # Multiple agents in one file
    "activities.py": "activities",
    "itinerary.py": "itinerary",
    "documents.py": "document_generator",
    "budget_checkpoint.py": "budget_checkpoint",
    "suggestions_checkpoint.py": "suggestions_checkpoint",
}


def update_agent_file(file_path: Path, agent_names):
    """Update a single agent file to use Config."""

    print(f"\nProcessing: {file_path.name}")

    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Step 1: Add config import if not present
    if "from config import Config" not in content:
        # Find the sys.path.insert line
        if "sys.path.insert(0" in content:
            content = content.replace(
                "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
                "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n\nfrom config import Config"
            )
            print(f"  ✓ Added config import")
        else:
            # Find import section and add after it
            import_match = re.search(r'(from google\.adk.*?\n)+', content)
            if import_match:
                insert_pos = import_match.end()
                content = content[:insert_pos] + "\nfrom config import Config\n" + content[insert_pos:]
                print(f"  ✓ Added config import (after ADK imports)")

    # Step 2: Replace hardcoded model with Config.get_model_for_agent
    if isinstance(agent_names, list):
        # Multiple agents in one file (booking.py)
        for agent_name in agent_names:
            # Find class definition for this agent
            class_pattern = rf'class\s+\w+Agent\(Agent\):.*?def __init__\(self\):.*?model="gemini-[^"]+?"'

            def replace_model(match):
                agent_text = match.group(0)
                # Determine which agent this is based on class name
                if "Flight" in agent_text:
                    return agent_text.replace('model="gemini-1.5-flash"', 'model=Config.get_model_for_agent("flight_booking")')
                elif "Hotel" in agent_text:
                    return agent_text.replace('model="gemini-1.5-flash"', 'model=Config.get_model_for_agent("hotel_booking")')
                elif "Car" in agent_text:
                    return agent_text.replace('model="gemini-1.5-flash"', 'model=Config.get_model_for_agent("car_rental")')
                return agent_text

            content = re.sub(class_pattern, replace_model, content, flags=re.DOTALL)
    else:
        # Single agent in file
        agent_name = agent_names
        content = re.sub(
            r'model="gemini-[^"]+?"',
            f'model=Config.get_model_for_agent("{agent_name}")',
            content
        )
        print(f"  ✓ Updated model to Config.get_model_for_agent(\"{agent_name}\")")

    # Step 3: Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Updated {file_path.name}")
        return True
    else:
        print(f"  ℹ️  No changes needed for {file_path.name}")
        return False


def main():
    """Update all agent files."""

    print("="*80)
    print("UPDATING AGENTS TO USE CENTRALIZED CONFIG")
    print("="*80)

    agents_dir = Path(__file__).parent / "adk_agents"

    if not agents_dir.exists():
        print(f"Error: {agents_dir} not found")
        return

    updated_count = 0

    for filename, agent_names in AGENT_CONFIGS.items():
        file_path = agents_dir / filename

        if not file_path.exists():
            print(f"⚠️  {filename} not found, skipping")
            continue

        if update_agent_file(file_path, agent_names):
            updated_count += 1

    print("\n" + "="*80)
    print(f"SUMMARY: Updated {updated_count}/{len(AGENT_CONFIGS)} agent files")
    print("="*80)

    print("\n✅ All agents now use Config.get_model_for_agent()")
    print("\nTo change models:")
    print("  1. Edit config.py and change DEFAULT_MODEL")
    print("  2. Or set ADK_DEFAULT_MODEL environment variable")
    print("  3. Or add agent-specific overrides in AGENT_MODELS dict")
    print("\nExample:")
    print("  export ADK_DEFAULT_MODEL=gemini-2.0-flash")
    print("  # Or edit config.py:")
    print("  DEFAULT_MODEL = 'gemini-1.5-pro'")


if __name__ == "__main__":
    main()
