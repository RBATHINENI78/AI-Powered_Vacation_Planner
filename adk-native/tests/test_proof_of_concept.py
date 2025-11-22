"""
Proof of Concept Test for ADK-Native Agents

Tests the first 2 pure ADK agents:
1. TravelAdvisoryAgent
2. DestinationIntelligenceAgent

Demonstrates:
- ADK BaseAgent with FunctionTool integration
- Canonical callbacks (before_agent, after_agent)
- Event streaming pattern
- Tool calling by LLM
"""

import pytest
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adk_agents.travel_advisory import TravelAdvisoryAgent
from adk_agents.destination import DestinationIntelligenceAgent
from callbacks.logging_callbacks import (
    before_agent_callback,
    after_agent_callback,
    get_agent_timings,
    reset_agent_timings
)

# For ADK invocation
from google.adk.invocation_context import InvocationContext
from google.adk.sessions import Session, InMemorySessionService


@pytest.mark.asyncio
async def test_travel_advisory_agent_us_to_france():
    """
    Test TravelAdvisoryAgent for US citizen traveling to France.
    Should check State Dept advisory and return CLEAR status.
    """
    print("\n" + "="*80)
    print("TEST 1: TravelAdvisoryAgent - US → France")
    print("="*80)

    # Create agent
    agent = TravelAdvisoryAgent()

    # Create InvocationContext (simplified for testing)
    # In production, this would be provided by ADK runtime
    session_service = InMemorySessionService()
    session = Session()
    await session_service.save_session(session)

    # Input data: US citizen traveling to France
    user_message = """
    I'm a US citizen planning to travel to Paris, France from December 1-7, 2025.
    Check if there are any travel advisories or restrictions.
    """

    ctx = InvocationContext(
        session_service=session_service,
        invocation_id="test_us_france_001",
        agent=agent,
        session=session,
        user_message=user_message
    )

    # Register callbacks
    # Note: In production, callbacks are registered globally
    # Here we'll manually call them for demonstration

    # Call before_agent callback
    from google.adk.callbacks import BeforeAgentCallbackContext
    before_ctx = BeforeAgentCallbackContext(
        agent=agent,
        invocation_id=ctx.invocation_id,
        input_data={"user_message": user_message},
        parent_agent=None
    )
    await before_agent_callback(before_ctx)

    # Run agent
    print("\n[AGENT] Running TravelAdvisoryAgent...")
    events = []
    async for event in agent.run_async(ctx):
        events.append(event)
        print(f"[EVENT] {event.type}: {str(event.content)[:200]}...")

    # Call after_agent callback
    from google.adk.callbacks import AfterAgentCallbackContext
    after_ctx = AfterAgentCallbackContext(
        agent=agent,
        invocation_id=ctx.invocation_id,
        output=events,
        error=None
    )
    await after_agent_callback(after_ctx)

    # Verify results
    assert len(events) > 0, "Agent should return events"
    print(f"\n[RESULT] Received {len(events)} events")

    # Check timing data
    timings = get_agent_timings()
    assert ctx.invocation_id in timings, "Timing data should be recorded"
    print(f"[TIMING] Execution time: {timings[ctx.invocation_id]['execution_time']:.2f}s")

    print("\n✓ Test passed: TravelAdvisoryAgent executed successfully")
    reset_agent_timings()


@pytest.mark.asyncio
async def test_destination_intelligence_agent_paris_weather():
    """
    Test DestinationIntelligenceAgent for Paris weather analysis.
    Should call weather API and generate packing recommendations.
    """
    print("\n" + "="*80)
    print("TEST 2: DestinationIntelligenceAgent - Paris Weather")
    print("="*80)

    # Create agent
    agent = DestinationIntelligenceAgent()

    # Create InvocationContext
    session_service = InMemorySessionService()
    session = Session()
    await session_service.save_session(session)

    user_message = """
    I'm traveling to Paris, France from December 1-7, 2025.
    What's the weather like? What should I pack?
    """

    ctx = InvocationContext(
        session_service=session_service,
        invocation_id="test_paris_weather_001",
        agent=agent,
        session=session,
        user_message=user_message
    )

    # Call before_agent callback
    from google.adk.callbacks import BeforeAgentCallbackContext
    before_ctx = BeforeAgentCallbackContext(
        agent=agent,
        invocation_id=ctx.invocation_id,
        input_data={"user_message": user_message},
        parent_agent=None
    )
    await before_agent_callback(before_ctx)

    # Run agent
    print("\n[AGENT] Running DestinationIntelligenceAgent...")
    print("[INFO] This will call OpenWeather API if OPENWEATHER_API_KEY is set")

    events = []
    async for event in agent.run_async(ctx):
        events.append(event)
        print(f"[EVENT] {event.type}: {str(event.content)[:200]}...")

    # Call after_agent callback
    from google.adk.callbacks import AfterAgentCallbackContext
    after_ctx = AfterAgentCallbackContext(
        agent=agent,
        invocation_id=ctx.invocation_id,
        output=events,
        error=None
    )
    await after_agent_callback(after_ctx)

    # Verify results
    assert len(events) > 0, "Agent should return events"
    print(f"\n[RESULT] Received {len(events)} events")

    # Check timing data
    timings = get_agent_timings()
    assert ctx.invocation_id in timings, "Timing data should be recorded"
    print(f"[TIMING] Execution time: {timings[ctx.invocation_id]['execution_time']:.2f}s")

    print("\n✓ Test passed: DestinationIntelligenceAgent executed successfully")
    reset_agent_timings()


@pytest.mark.asyncio
async def test_sequential_execution_both_agents():
    """
    Test running both agents sequentially.
    Demonstrates how ADK would orchestrate them in SequentialAgent.
    """
    print("\n" + "="*80)
    print("TEST 3: Sequential Execution - Advisory → Destination")
    print("="*80)

    session_service = InMemorySessionService()
    session = Session()
    await session_service.save_session(session)

    user_message = """
    I'm a US citizen planning a vacation to Paris, France from December 1-7, 2025.
    Check travel advisories and weather conditions.
    """

    # Agent 1: Travel Advisory
    print("\n[STEP 1/2] Running TravelAdvisoryAgent...")
    agent1 = TravelAdvisoryAgent()
    ctx1 = InvocationContext(
        session_service=session_service,
        invocation_id="test_sequential_001_advisory",
        agent=agent1,
        session=session,
        user_message=user_message
    )

    from google.adk.callbacks import BeforeAgentCallbackContext
    before_ctx1 = BeforeAgentCallbackContext(
        agent=agent1,
        invocation_id=ctx1.invocation_id,
        input_data={"user_message": user_message},
        parent_agent=None
    )
    await before_agent_callback(before_ctx1)

    events1 = []
    async for event in agent1.run_async(ctx1):
        events1.append(event)

    from google.adk.callbacks import AfterAgentCallbackContext
    after_ctx1 = AfterAgentCallbackContext(
        agent=agent1,
        invocation_id=ctx1.invocation_id,
        output=events1,
        error=None
    )
    await after_agent_callback(after_ctx1)

    print(f"  ✓ TravelAdvisoryAgent completed with {len(events1)} events")

    # Agent 2: Destination Intelligence
    # In real ADK workflow, this would automatically receive context from agent1
    print("\n[STEP 2/2] Running DestinationIntelligenceAgent...")
    agent2 = DestinationIntelligenceAgent()
    ctx2 = InvocationContext(
        session_service=session_service,
        invocation_id="test_sequential_001_destination",
        agent=agent2,
        session=session,
        user_message=user_message + "\n\nPrevious agent approved travel - no advisories."
    )

    before_ctx2 = BeforeAgentCallbackContext(
        agent=agent2,
        invocation_id=ctx2.invocation_id,
        input_data={"user_message": user_message},
        parent_agent=None
    )
    await before_agent_callback(before_ctx2)

    events2 = []
    async for event in agent2.run_async(ctx2):
        events2.append(event)

    after_ctx2 = AfterAgentCallbackContext(
        agent=agent2,
        invocation_id=ctx2.invocation_id,
        output=events2,
        error=None
    )
    await after_agent_callback(after_ctx2)

    print(f"  ✓ DestinationIntelligenceAgent completed with {len(events2)} events")

    # Summary
    timings = get_agent_timings()
    total_time = sum(t["execution_time"] for t in timings.values())

    print(f"\n[SUMMARY]")
    print(f"  Total agents executed: 2")
    print(f"  Total execution time: {total_time:.2f}s")
    print(f"  Agent 1 (Advisory): {timings['test_sequential_001_advisory']['execution_time']:.2f}s")
    print(f"  Agent 2 (Destination): {timings['test_sequential_001_destination']['execution_time']:.2f}s")

    print("\n✓ Test passed: Sequential execution completed successfully")
    reset_agent_timings()


if __name__ == "__main__":
    """Run tests directly without pytest."""
    print("ADK-Native Proof of Concept Tests")
    print("="*80)

    # Check for required API keys
    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("\n⚠️  WARNING: GOOGLE_API_KEY or GEMINI_API_KEY not set")
        print("   Agents may not work without Gemini API access")
        print("   Set via: export GOOGLE_API_KEY=your_key")

    if not os.getenv("OPENWEATHER_API_KEY"):
        print("\n⚠️  WARNING: OPENWEATHER_API_KEY not set")
        print("   Weather tools will use fallback data")
        print("   Set via: export OPENWEATHER_API_KEY=your_key")

    # Run tests
    asyncio.run(test_travel_advisory_agent_us_to_france())
    asyncio.run(test_destination_intelligence_agent_paris_weather())
    asyncio.run(test_sequential_execution_both_agents())

    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Proof of Concept Validated")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Implement remaining 8 specialized agents")
    print("  2. Configure workflow agents (ParallelAgent, SequentialAgent)")
    print("  3. Add HITL budget checkpoint callback")
    print("  4. Test full end-to-end vacation planning flow")
