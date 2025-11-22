"""
Simple Agent Test Runner
Demonstrates how to run ADK agents with user queries
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adk_agents import (
    TravelAdvisoryAgent,
    DestinationIntelligenceAgent,
    ImmigrationSpecialistAgent,
    CurrencyExchangeAgent
)


async def test_travel_advisory():
    """Test TravelAdvisoryAgent with a simple query."""
    print("\n" + "="*80)
    print("TEST 1: TravelAdvisoryAgent")
    print("="*80)

    agent = TravelAdvisoryAgent()

    user_query = """
    I'm a US citizen planning to travel to Paris, France from December 1-7, 2025.
    Are there any travel advisories or restrictions I should know about?
    """

    print(f"\n[USER QUERY]")
    print(user_query.strip())

    print(f"\n[AGENT INFO]")
    print(f"  Name: {agent.name}")
    print(f"  Tools: {len(agent.tools)} available")
    for i, tool in enumerate(agent.tools, 1):
        print(f"    {i}. {tool._fn.__name__}")

    print(f"\n[NOTE]")
    print("  ADK agents are designed to be called by the ADK runtime/web interface.")
    print("  They don't have a simple execute() method like custom agents.")
    print("  To test properly, we need to integrate with ADK's web interface or")
    print("  create a workflow orchestrator in Phase 3.")

    return agent


async def test_destination_intelligence():
    """Test DestinationIntelligenceAgent."""
    print("\n" + "="*80)
    print("TEST 2: DestinationIntelligenceAgent")
    print("="*80)

    agent = DestinationIntelligenceAgent()

    user_query = """
    What's the weather like in Paris, France in early December?
    What should I pack for a trip from December 1-7?
    """

    print(f"\n[USER QUERY]")
    print(user_query.strip())

    print(f"\n[AGENT INFO]")
    print(f"  Name: {agent.name}")
    print(f"  Tools: {len(agent.tools)} available")
    for i, tool in enumerate(agent.tools, 1):
        print(f"    {i}. {tool._fn.__name__}")

    return agent


async def test_immigration():
    """Test ImmigrationSpecialistAgent."""
    print("\n" + "="*80)
    print("TEST 3: ImmigrationSpecialistAgent")
    print("="*80)

    agent = ImmigrationSpecialistAgent()

    user_query = """
    I'm a US citizen traveling to Paris, France for 7 days.
    Do I need a visa? What documents do I need?
    """

    print(f"\n[USER QUERY]")
    print(user_query.strip())

    print(f"\n[AGENT INFO]")
    print(f"  Name: {agent.name}")
    print(f"  Tools: {len(agent.tools)} available")
    for i, tool in enumerate(agent.tools, 1):
        print(f"    {i}. {tool._fn.__name__}")

    return agent


async def test_currency():
    """Test CurrencyExchangeAgent."""
    print("\n" + "="*80)
    print("TEST 4: CurrencyExchangeAgent")
    print("="*80)

    agent = CurrencyExchangeAgent()

    user_query = """
    I have a budget of $3000 for 2 people traveling to Paris for 7 days.
    What's the exchange rate? Is this budget sufficient?
    """

    print(f"\n[USER QUERY]")
    print(user_query.strip())

    print(f"\n[AGENT INFO]")
    print(f"  Name: {agent.name}")
    print(f"  Tools: {len(agent.tools)} available")
    for i, tool in enumerate(agent.tools, 1):
        print(f"    {i}. {tool._fn.__name__}")

    return agent


async def main():
    """Run all agent tests."""
    print("="*80)
    print("ADK-NATIVE AGENT TEST RUNNER")
    print("="*80)

    # Check API keys
    api_key = os.getenv("GOOGLE_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    exchange_key = os.getenv("EXCHANGERATE_API_KEY")

    print(f"\n[API KEYS]")
    print(f"  GOOGLE_API_KEY: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"  OPENWEATHER_API_KEY: {'✓ Set' if weather_key else '✗ Missing'}")
    print(f"  EXCHANGERATE_API_KEY: {'✓ Set' if exchange_key else '✗ Missing'}")

    if not api_key:
        print("\n⚠️  WARNING: GOOGLE_API_KEY not set!")
        print("   Agents will not work without this key.")
        return

    # Test agents
    await test_travel_advisory()
    await test_destination_intelligence()
    await test_immigration()
    await test_currency()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✅ All 4 agents created successfully!")
    print("\n📝 IMPORTANT NOTES:")
    print("\n1. ADK agents are configuration objects, not directly executable")
    print("   - They define: name, description, model, tools")
    print("   - They're designed to be called by ADK runtime")
    print("\n2. To actually TEST agents with queries, we need:")
    print("   - Option A: Use ADK's web interface (adk serve)")
    print("   - Option B: Create workflow orchestrator (Phase 3)")
    print("   - Option C: Wrap in tool functions (like original project)")
    print("\n3. RECOMMENDED NEXT STEP:")
    print("   Proceed to Phase 3 to create workflow orchestrator")
    print("   This will wire up all 10 agents and enable end-to-end testing")
    print("\n4. ALTERNATIVE - Quick Test Now:")
    print("   We can create a simple wrapper to test individual tools")
    print("   (not full agent, but verifies tools work)")

    print("\n" + "="*80)
    print("Would you like to:")
    print("  A) Create simple tool test wrapper (quick, validates tools work)")
    print("  B) Proceed to Phase 3 (workflow orchestrator for full testing)")
    print("  C) Both (test tools now, then build workflows)")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
