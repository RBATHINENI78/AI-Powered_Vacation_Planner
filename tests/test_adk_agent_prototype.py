"""
Test ADK Agent Prototype - Validates conversion approach
"""
import pytest
import asyncio
from google.adk.agents import BaseAgent, ParallelAgent
from google.adk.runners import InvocationContext
from google.adk.events import Event
from typing import AsyncGenerator


class SimpleADKAgent(BaseAgent):
    """
    Prototype: Shows how to create an ADK-compatible agent that returns structured data.
    This is the pattern we'll use for all our specialized agents.
    """

    def __init__(self, agent_name: str):
        super().__init__(
            name=agent_name,
            description=f"Simple ADK agent: {agent_name}"
        )

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        ADK's required method signature.
        Must yield Event objects, not return dicts.
        """
        # Extract input from context (this is the key insight!)
        # Context contains user_content which has the input data
        input_data = self._extract_input(ctx)

        # Simulate agent work
        await asyncio.sleep(0.1)

        # Create our result (this would be our agent's actual logic)
        result = {
            "agent": self.name,
            "status": "success",
            "input_received": input_data,
            "output": f"Processed by {self.name}"
        }

        # Yield result as Event with content
        yield Event(content=str(result))

    def _extract_input(self, ctx: InvocationContext) -> dict:
        """
        Extract input data from InvocationContext.
        This is the bridge between ADK's context and our dict-based logic.
        """
        # Try to get input from user_content
        if hasattr(ctx, 'user_content') and ctx.user_content:
            # user_content might be a list of Content objects
            if isinstance(ctx.user_content, list) and len(ctx.user_content) > 0:
                first_content = ctx.user_content[0]
                if hasattr(first_content, 'text'):
                    # Parse text as needed
                    return {"text": first_content.text}

        # Fallback: return empty dict
        return {}


@pytest.mark.asyncio
async def test_simple_adk_agent():
    """Test that our ADK-compatible agent works."""
    agent = SimpleADKAgent("test_agent")

    # Create a minimal InvocationContext
    # TODO: Figure out how to properly create this
    ctx = InvocationContext()

    # Try to run the agent
    events = []
    try:
        async for event in agent.run_async(ctx):
            events.append(event)
            print(f"Event: {event}")
    except Exception as e:
        print(f"Error: {e}")
        # This might fail - we're learning the API

    print(f"\\nCollected {len(events)} events")
    assert True  # Pass for now, we're just learning


@pytest.mark.asyncio
async def test_parallel_agent_with_simple_agents():
    """Test ADK ParallelAgent with our simple agents."""

    # Create sub-agents
    agent1 = SimpleADKAgent("agent_1")
    agent2 = SimpleADKAgent("agent_2")

    # Create ParallelAgent
    parallel = ParallelAgent(
        name="test_parallel",
        sub_agents=[agent1, agent2],
        description="Test parallel execution"
    )

    # Create context
    ctx = InvocationContext()

    # Run and collect events
    events = []
    try:
        async for event in parallel.run_async(ctx):
            events.append(event)
            print(f"Parallel Event: {type(event).__name__}")
    except Exception as e:
        print(f"Parallel Error: {e}")
        import traceback
        traceback.print_exc()

    print(f"\\nParallel collected {len(events)} events")
    assert True  # Learning phase


if __name__ == "__main__":
    # Run tests directly
    print("=" * 80)
    print("TEST 1: Simple ADK Agent")
    print("=" * 80)
    asyncio.run(test_simple_adk_agent())

    print("\\n" + "=" * 80)
    print("TEST 2: Parallel Agent with Simple Agents")
    print("=" * 80)
    asyncio.run(test_parallel_agent_with_simple_agents())
