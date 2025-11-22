"""
ADK Canonical Callbacks for Logging and Observability

Implements before_agent and after_agent callbacks as per:
https://google.github.io/adk-docs/callbacks/

These callbacks provide:
- Agent execution logging
- Performance timing
- A2A communication tracking
- Error monitoring
"""

from google.adk.callbacks import BeforeAgentCallbackContext, AfterAgentCallbackContext
from loguru import logger
from typing import Optional
import time


# Store timing data for performance metrics
_agent_timings = {}


async def before_agent_callback(ctx: BeforeAgentCallbackContext) -> None:
    """
    Callback invoked BEFORE agent execution.

    Use cases:
    - Log agent start
    - Record start time for performance tracking
    - Log input data for debugging
    - Potential HITL checkpoints (budget validation)

    Args:
        ctx: Contains agent, input_data, invocation_id
    """
    agent_name = ctx.agent.name
    invocation_id = ctx.invocation_id

    logger.info(f"[AGENT_START] {agent_name} | invocation={invocation_id}")

    # Store start time for performance calculation
    _agent_timings[invocation_id] = {
        "agent": agent_name,
        "start_time": time.time(),
        "parent_agent": ctx.parent_agent.name if ctx.parent_agent else None
    }

    # Log input preview (truncate if too long)
    input_preview = str(ctx.input_data)[:200]
    logger.debug(f"[AGENT_INPUT] {agent_name} | input={input_preview}...")


async def after_agent_callback(ctx: AfterAgentCallbackContext) -> None:
    """
    Callback invoked AFTER agent execution completes.

    Use cases:
    - Log agent completion
    - Calculate execution time
    - Track performance metrics
    - Log errors if agent failed
    - Calculate parallel speedup for workflow agents

    Args:
        ctx: Contains agent, output, invocation_id, error (if any)
    """
    agent_name = ctx.agent.name
    invocation_id = ctx.invocation_id

    # Calculate execution time
    timing_data = _agent_timings.get(invocation_id, {})
    start_time = timing_data.get("start_time")
    execution_time = time.time() - start_time if start_time else 0

    if ctx.error:
        logger.error(
            f"[AGENT_ERROR] {agent_name} | "
            f"invocation={invocation_id} | "
            f"time={execution_time:.2f}s | "
            f"error={ctx.error}"
        )
    else:
        logger.info(
            f"[AGENT_COMPLETE] {agent_name} | "
            f"invocation={invocation_id} | "
            f"time={execution_time:.2f}s"
        )

        # Log output preview
        output_preview = str(ctx.output)[:200]
        logger.debug(f"[AGENT_OUTPUT] {agent_name} | output={output_preview}...")

    # Store timing for potential speedup calculation
    timing_data["end_time"] = time.time()
    timing_data["execution_time"] = execution_time
    timing_data["error"] = ctx.error is not None

    # For parallel workflow agents, calculate speedup
    parent_agent = timing_data.get("parent_agent")
    if parent_agent and "parallel" in parent_agent.lower():
        _calculate_parallel_speedup(parent_agent, invocation_id, timing_data)


def _calculate_parallel_speedup(parent_agent: str, invocation_id: str, timing_data: dict) -> None:
    """
    Calculate parallel execution speedup.

    Compares total sequential time vs actual parallel time.
    Logs speedup factor achieved by parallel execution.
    """
    # Get all agents with same parent
    sibling_timings = [
        t for t in _agent_timings.values()
        if t.get("parent_agent") == parent_agent and t.get("end_time")
    ]

    if len(sibling_timings) < 2:
        return  # Need at least 2 parallel agents to calculate speedup

    # Calculate total sequential time (if run sequentially)
    total_sequential = sum(t["execution_time"] for t in sibling_timings)

    # Actual parallel time = max of all parallel executions
    actual_parallel = max(t["execution_time"] for t in sibling_timings)

    speedup = total_sequential / actual_parallel if actual_parallel > 0 else 1.0

    logger.info(
        f"[PARALLEL_SPEEDUP] {parent_agent} | "
        f"sequential={total_sequential:.2f}s | "
        f"parallel={actual_parallel:.2f}s | "
        f"speedup={speedup:.2f}x | "
        f"agents={len(sibling_timings)}"
    )


def get_agent_timings() -> dict:
    """
    Get all agent timing data.

    Returns:
        Dictionary of invocation_id -> timing data
    """
    return _agent_timings.copy()


def reset_agent_timings() -> None:
    """Clear timing data (useful between test runs)."""
    global _agent_timings
    _agent_timings = {}
