"""
Test ADK Built-in Workflow Agents

This test verifies the behavior of ADK's ParallelAgent, SequentialAgent, and LoopAgent
to understand their return value structures and data flow before refactoring.

Run with: pytest tests/test_adk_workflow_agents.py -v
"""

import pytest
import asyncio
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
from google.adk.agents.base_agent import BaseAgent


# ============================================================================
# Mock Agents for Testing
# ============================================================================

class MockAgent1(BaseAgent):
    """Mock agent that returns structured data."""

    def __init__(self):
        super().__init__(
            name="mock_agent_1",
            description="First mock agent"
        )

    async def _execute_impl(self, input_data):
        await asyncio.sleep(0.1)  # Simulate work
        return {
            "status": "success",
            "agent": "mock_1",
            "output": f"Processed: {input_data.get('value', 'none')}",
            "metadata": {"execution_time_ms": 100}
        }


class MockAgent2(BaseAgent):
    """Mock agent that depends on previous agent's output."""

    def __init__(self):
        super().__init__(
            name="mock_agent_2",
            description="Second mock agent"
        )

    async def _execute_impl(self, input_data):
        await asyncio.sleep(0.1)

        # Check if we receive data from previous agent
        previous_output = input_data.get("output", "no_previous_data")

        return {
            "status": "success",
            "agent": "mock_2",
            "previous_data": previous_output,  # Should receive from Mock1
            "output": f"Extended: {previous_output}",
            "metadata": {"execution_time_ms": 100}
        }


class MockAgent3(BaseAgent):
    """Mock agent for parallel execution."""

    def __init__(self):
        super().__init__(
            name="mock_agent_3",
            description="Third mock agent"
        )

    async def _execute_impl(self, input_data):
        await asyncio.sleep(0.2)
        return {
            "status": "success",
            "agent": "mock_3",
            "output": "Parallel task completed",
            "metadata": {"execution_time_ms": 200}
        }


# ============================================================================
# Test: ParallelAgent
# ============================================================================

@pytest.mark.asyncio
async def test_parallel_agent_basic():
    """Test ADK ParallelAgent with multiple sub-agents."""

    parallel_agent = ParallelAgent(
        name="test_parallel",
        sub_agents=[MockAgent1(), MockAgent2(), MockAgent3()],
        description="Test parallel execution"
    )

    input_data = {"value": "test_input"}

    result = await parallel_agent.run_async(input_data)

    # CRITICAL: What does ADK ParallelAgent return?
    print("\n" + "="*80)
    print("PARALLEL AGENT RESULT:")
    print("="*80)
    print(f"Type: {type(result)}")
    print(f"Keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    print(f"Full result: {result}")
    print("="*80)

    # Verify expectations
    assert result is not None
    # TODO: Add assertions based on actual ADK behavior


@pytest.mark.asyncio
async def test_parallel_agent_performance_metrics():
    """Check if ADK ParallelAgent provides performance metrics."""

    parallel_agent = ParallelAgent(
        name="test_perf",
        sub_agents=[MockAgent1(), MockAgent2()],
        description="Test performance tracking"
    )

    result = await parallel_agent.run_async({"value": "perf_test"})

    # CRITICAL: Does ADK provide speedup calculation?
    print("\n" + "="*80)
    print("PARALLEL PERFORMANCE METRICS:")
    print("="*80)

    # Check for our expected fields
    has_status = "status" in result if isinstance(result, dict) else False
    has_metadata = "_metadata" in result if isinstance(result, dict) else False
    has_performance = "performance" in result if isinstance(result, dict) else False
    has_speedup = False

    if isinstance(result, dict) and "performance" in result:
        has_speedup = "speedup_factor" in result["performance"]

    print(f"Has 'status': {has_status}")
    print(f"Has '_metadata': {has_metadata}")
    print(f"Has 'performance': {has_performance}")
    print(f"Has 'speedup_factor': {has_speedup}")
    print("="*80)

    # Document findings
    assert result is not None


# ============================================================================
# Test: SequentialAgent
# ============================================================================

@pytest.mark.asyncio
async def test_sequential_agent_data_passing():
    """CRITICAL TEST: How does SequentialAgent pass data between sub-agents?"""

    sequential_agent = SequentialAgent(
        name="test_sequential",
        sub_agents=[MockAgent1(), MockAgent2()],
        description="Test sequential data flow"
    )

    result = await sequential_agent.run_async({"value": "sequential_test"})

    print("\n" + "="*80)
    print("SEQUENTIAL AGENT RESULT:")
    print("="*80)
    print(f"Full result: {result}")
    print("="*80)

    # CRITICAL QUESTION: Did MockAgent2 receive MockAgent1's output?
    # Check if "previous_data" field contains MockAgent1's output
    print("\n" + "="*80)
    print("DATA FLOW ANALYSIS:")
    print("="*80)

    # Try to extract MockAgent2's result
    # (Structure unknown - need to test to find out)
    print(f"Result type: {type(result)}")
    print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")

    # TODO: Verify data transformation capability
    print("="*80)

    assert result is not None


@pytest.mark.asyncio
async def test_sequential_agent_return_structure():
    """Check SequentialAgent return value structure for Orchestrator compatibility."""

    sequential_agent = SequentialAgent(
        name="test_structure",
        sub_agents=[MockAgent1(), MockAgent2()],
        description="Test return structure"
    )

    result = await sequential_agent.run_async({"value": "structure_test"})

    print("\n" + "="*80)
    print("SEQUENTIAL RETURN VALUE STRUCTURE:")
    print("="*80)

    # Check for Orchestrator's expected fields
    if isinstance(result, dict):
        has_status = "status" in result
        has_metadata = "_metadata" in result
        has_exec_time = False
        has_successful_steps = "successful_steps" in result

        if has_metadata and isinstance(result["_metadata"], dict):
            has_exec_time = "execution_time_ms" in result["_metadata"]

        print(f"Has 'status': {has_status}")
        print(f"Has '_metadata': {has_metadata}")
        print(f"Has '_metadata.execution_time_ms': {has_exec_time}")
        print(f"Has 'successful_steps': {has_successful_steps}")
        print(f"\nFull structure: {list(result.keys())}")

    print("="*80)

    assert result is not None


# ============================================================================
# Test: LoopAgent
# ============================================================================

@pytest.mark.asyncio
async def test_loop_agent_basic():
    """Test ADK LoopAgent with convergence check."""

    class ConvergingAgent(BaseAgent):
        def __init__(self):
            super().__init__(name="converging", description="Test convergence")
            self.iteration_count = 0

        async def _execute_impl(self, input_data):
            self.iteration_count += 1
            converged = self.iteration_count >= 3

            return {
                "status": "success" if converged else "in_progress",
                "iteration": self.iteration_count,
                "converged": converged,
                "value": 100 - (3 - self.iteration_count) * 10
            }

    converging_agent = ConvergingAgent()

    loop_agent = LoopAgent(
        name="test_loop",
        sub_agent=converging_agent,
        max_iterations=5,
        # convergence_check=lambda r: r.get("converged", False),  # May not work
        description="Test loop execution"
    )

    result = await loop_agent.run_async({"target": 100})

    print("\n" + "="*80)
    print("LOOP AGENT RESULT:")
    print("="*80)
    print(f"Full result: {result}")
    print("="*80)

    # CRITICAL: Check for iteration tracking
    if isinstance(result, dict):
        has_iterations = "iterations_used" in result or "iteration" in result
        has_convergence = "converged" in result

        print(f"Has iteration tracking: {has_iterations}")
        print(f"Has convergence flag: {has_convergence}")

    print("="*80)

    assert result is not None


# ============================================================================
# Comparison Test: Custom vs ADK
# ============================================================================

@pytest.mark.asyncio
async def test_compare_custom_vs_adk():
    """Side-by-side comparison of custom agent vs ADK agent."""

    from src.agents.parallel_agent import ParallelBookingAgent
    from src.agents.booking_agents import FlightBookingAgent, HotelBookingAgent

    # Test custom implementation
    custom_agent = ParallelBookingAgent()

    custom_input = {
        "origin": "NYC",
        "destination": "Paris, France",
        "departure_date": "2025-06-15",
        "return_date": "2025-06-25",
        "travelers": 2
    }

    custom_result = await custom_agent.execute(custom_input)  # Custom agent uses execute()

    # Test ADK implementation
    adk_agent = ParallelAgent(
        name="adk_booking",
        sub_agents=[FlightBookingAgent(), HotelBookingAgent()],
        description="ADK parallel booking"
    )

    adk_result = await adk_agent.run_async(custom_input)  # ADK agent uses run_async()

    print("\n" + "="*80)
    print("CUSTOM vs ADK COMPARISON:")
    print("="*80)
    print("\nCUSTOM AGENT RESULT:")
    print(f"  Keys: {list(custom_result.keys())}")
    print(f"  Has speedup: {'performance' in custom_result and 'speedup_factor' in custom_result['performance']}")
    print(f"  Has booking_summary: {'booking_summary' in custom_result}")

    print("\nADK AGENT RESULT:")
    print(f"  Keys: {list(adk_result.keys() if isinstance(adk_result, dict) else [])}")
    print(f"  Full result: {adk_result}")
    print("="*80)

    # This test reveals compatibility gaps
    assert custom_result is not None
    assert adk_result is not None


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    # Run tests directly
    asyncio.run(test_parallel_agent_basic())
    asyncio.run(test_parallel_agent_performance_metrics())
    asyncio.run(test_sequential_agent_data_passing())
    asyncio.run(test_sequential_agent_return_structure())
    asyncio.run(test_loop_agent_basic())
    # asyncio.run(test_compare_custom_vs_adk())  # Uncomment after fixing imports
