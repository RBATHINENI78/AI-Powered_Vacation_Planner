"""
Simple Execution Test - Tests agents with real ADK execution
Requires GOOGLE_API_KEY or GEMINI_API_KEY to be set
"""

import os
import sys
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk_agents.travel_advisory import TravelAdvisoryAgent
from adk_agents.destination import DestinationIntelligenceAgent


async def test_travel_advisory_simple():
    """Test TravelAdvisoryAgent with a simple query."""
    print("\n" + "="*80)
    print("TEST 1: TravelAdvisoryAgent - Simple Execution")
    print("="*80)

    agent = TravelAdvisoryAgent()

    # Simple input data
    input_data = {
        "origin_country": "United States",
        "destination_country": "France",
        "start_date": "2025-12-01",
        "end_date": "2025-12-07"
    }

    print(f"\n[INPUT]")
    print(f"  Origin: {input_data['origin_country']}")
    print(f"  Destination: {input_data['destination_country']}")
    print(f"  Dates: {input_data['start_date']} to {input_data['end_date']}")

    print(f"\n[AGENT] Executing {agent.name}...")

    try:
        # Execute the agent using the ADK pattern
        result = await agent.execute(input_data)

        print(f"\n[RESULT]")
        print(f"  Status: {result.get('status', 'unknown')}")

        if result.get('can_proceed') is not None:
            print(f"  Can Proceed: {result.get('can_proceed')}")

        if result.get('advisories'):
            print(f"  Advisories: {len(result.get('advisories'))} found")

        if result.get('recommendation'):
            print(f"  Recommendation: {result.get('recommendation')}")

        print("\n✓ Test passed: TravelAdvisoryAgent executed successfully")
        return result

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_destination_intelligence_simple():
    """Test DestinationIntelligenceAgent with a simple query."""
    print("\n" + "="*80)
    print("TEST 2: DestinationIntelligenceAgent - Simple Execution")
    print("="*80)

    agent = DestinationIntelligenceAgent()

    # Simple input data
    input_data = {
        "city": "Paris",
        "country": "France",
        "dates": {
            "start": "2025-12-01",
            "end": "2025-12-07"
        }
    }

    print(f"\n[INPUT]")
    print(f"  City: {input_data['city']}")
    print(f"  Country: {input_data['country']}")
    print(f"  Dates: {input_data['dates']['start']} to {input_data['dates']['end']}")

    print(f"\n[AGENT] Executing {agent.name}...")

    try:
        # Execute the agent
        result = await agent.execute(input_data)

        print(f"\n[RESULT]")
        print(f"  Status: {result.get('status', 'unknown')}")

        if result.get('current_weather'):
            weather = result['current_weather']
            print(f"  Temperature: {weather.get('temperature')}°C")
            print(f"  Conditions: {weather.get('conditions')}")

        if result.get('analysis'):
            analysis = result['analysis']
            print(f"  Travel Rating: {analysis.get('travel_conditions')}")

        print("\n✓ Test passed: DestinationIntelligenceAgent executed successfully")
        return result

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all tests."""
    print("ADK-Native Simple Execution Tests")
    print("="*80)

    # Check for API keys
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY or GEMINI_API_KEY not set")
        print("   Tests will fail without API key")
        print("   Set via: export GOOGLE_API_KEY=your_key")
        return

    print(f"\n✓ API key found ({api_key[:10]}...)")

    # Run tests
    result1 = await test_travel_advisory_simple()
    result2 = await test_destination_intelligence_simple()

    # Summary
    print("\n" + "="*80)
    if result1 and result2:
        print("✅ ALL TESTS PASSED")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
