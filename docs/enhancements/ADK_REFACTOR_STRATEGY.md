# ADK Workflow Agents Refactoring - Step-by-Step Strategy

**Created**: 2025-11-21
**Status**: Ready to Execute
**Approach**: Incremental refactoring, one agent at a time
**Goal**: Align with ADK's native workflow patterns while preserving functionality

---

## Understanding Current Architecture

### Layer 1: ADK Web Interface Entry Point
**File**: `agents/vacation_planner/agent.py`
- Uses ADK's native `Agent` class
- Exposes `FunctionTool` wrappers
- ✅ Already ADK-compliant

### Layer 2: Specialized Agents (Leaf Agents)
**Files**: `src/agents/destination_intelligence.py`, `immigration_specialist.py`, etc.
- Use custom `BaseAgent` with `execute()` method
- Called via tool wrappers that await `agent.execute(input_data)`
- ✅ Keep as-is - they work fine through tool wrappers

### Layer 3: Workflow Agents (NEEDS REFACTORING)
**Files**:
- `src/agents/orchestrator.py` - Coordinates everything
- `src/agents/sequential_agent.py` - Research phase
- `src/agents/parallel_agent.py` - Booking phase
- `src/agents/loop_agent.py` - Budget optimization

**Problem**: These use custom workflow logic instead of ADK's `ParallelAgent`, `SequentialAgent`, `LoopAgent`

---

## Refactoring Strategy

### Key Insight: Adapter Pattern

We'll create **ADK-native workflow agents** that orchestrate **our existing specialized agents** through an adapter:

```python
# Adapter that wraps our custom agents for ADK workflow agents
class ADKAgentAdapter(google.adk.agents.BaseAgent):
    """Adapts our custom agent.execute() to ADK's run_async() interface"""

    def __init__(self, custom_agent):
        self.custom_agent = custom_agent
        super().__init__(
            name=custom_agent.name,
            description=custom_agent.description
        )

    async def run_async(self, context: InvocationContext):
        # Extract input from context
        input_data = context.user_message or context.initial_input

        # Call our custom agent
        result = await self.custom_agent.execute(input_data)

        # Yield ADK events
        yield AgentResponseChunk(result)
```

This allows us to:
1. ✅ Use ADK's `ParallelAgent`, `SequentialAgent`, `LoopAgent`
2. ✅ Keep our specialized agents unchanged
3. ✅ Preserve all custom features (data transformation, performance metrics)

---

## Phase 1: Create ADK Adapter for Custom Agents

**File to create**: `src/agents/adk_adapter.py`

```python
"""
ADK Agent Adapter - Bridges custom BaseAgent to ADK's workflow agents
"""
from typing import Dict, Any, AsyncGenerator
from google.adk.agents import BaseAgent as ADKBaseAgent
from google.adk.core import InvocationContext
from google.adk.events import Event, AgentResponseChunk
from .base_agent import BaseAgent as CustomBaseAgent


class ADKAgentAdapter(ADKBaseAgent):
    """
    Adapts our custom BaseAgent (with execute() method) to ADK's BaseAgent interface.
    This allows our custom agents to work with ADK's ParallelAgent, SequentialAgent, LoopAgent.
    """

    def __init__(self, custom_agent: CustomBaseAgent):
        """
        Args:
            custom_agent: Our custom agent with execute() method
        """
        self.custom_agent = custom_agent
        super().__init__(
            name=custom_agent.name,
            description=custom_agent.description
        )

    async def run_async(self, context: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        ADK workflow agents call this method.
        We extract input, call our custom agent.execute(), and yield the result as events.
        """
        # Extract input from context
        # TODO: Determine correct way to extract input from InvocationContext
        input_data = self._extract_input_from_context(context)

        # Call our custom agent
        result = await self.custom_agent.execute(input_data)

        # Yield result as ADK event
        yield AgentResponseChunk(content=result)

    def _extract_input_from_context(self, context: InvocationContext) -> Dict[str, Any]:
        """Extract our input dict from ADK's InvocationContext"""
        # TODO: Research correct extraction method
        # Possibilities:
        # - context.user_message
        # - context.initial_input
        # - context.parameters
        return {}  # Placeholder
```

**Estimated Time**: 2 hours (includes research on Invocation Context)

---

## Phase 2: Refactor ParallelBookingAgent

**Current**: `src/agents/parallel_agent.py` (~230 lines of custom code)

**New Approach**: Use ADK's `ParallelAgent` with adapted sub-agents

**File to create**: `src/agents/adk_parallel_booking.py`

```python
"""
Parallel Booking Agent - Uses ADK's ParallelAgent with adapted sub-agents
"""
from google.adk.agents import ParallelAgent
from .adk_adapter import ADKAgentAdapter
from .booking_agents import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from .experience_curator import ExperienceCuratorAgent


# Adapt our custom agents to ADK interface
flight_adapter = ADKAgentAdapter(FlightBookingAgent())
hotel_adapter = ADKAgentAdapter(HotelBookingAgent())
car_adapter = ADKAgentAdapter(CarRentalAgent())
experience_adapter = ADKAgentAdapter(ExperienceCuratorAgent())

# Create ADK ParallelAgent
parallel_booking_agent = ParallelAgent(
    name="parallel_booking",
    sub_agents=[
        flight_adapter,
        hotel_adapter,
        car_adapter,
        experience_adapter
    ],
    description="Orchestrates booking phase with parallel execution"
)
```

**Orchestrator Integration**:
```python
# src/agents/orchestrator.py
from .adk_parallel_booking import parallel_booking_agent

# In _execute_impl:
# OLD: booking_result = await self.booking_agent.execute(booking_input)
# NEW: Consume event stream from ADK agent
events = []
async for event in parallel_booking_agent.run_async(context):
    events.append(event)
booking_result = self._extract_result_from_events(events)
```

**Challenges**:
- Need to create `InvocationContext` from our input dict
- Need to extract final result from event stream
- Need to compile booking summary (currently done in custom agent)

**Estimated Time**: 4 hours

---

## Phase 3: Refactor SequentialResearchAgent

**Critical Feature**: Custom data transformation between agents

**Current**: `src/agents/sequential_agent.py`
- `_prepare_agent_input()` - Customizes input for each agent
- `_accumulate_data()` - Transforms output to input for next agent
- `_compile_research_report()` - Aggregates results

**ADK Limitation**: `SequentialAgent` may not support custom transformations

**Solution**: Wrapper around ADK's SequentialAgent

**File to create**: `src/agents/adk_sequential_research.py`

```python
"""
Sequential Research Agent - Wraps ADK SequentialAgent with custom data flow
"""
from google.adk.agents import SequentialAgent
from .adk_adapter import ADKAgentAdapter
from .destination_intelligence import DestinationIntelligenceAgent
from .immigration_specialist import ImmigrationSpecialistAgent
from .financial_advisor import FinancialAdvisorAgent
from .base_agent import BaseAgent


class SequentialResearchAgent(BaseAgent):
    """
    Wraps ADK SequentialAgent while preserving custom data transformation logic.
    """

    def __init__(self):
        super().__init__(
            name="sequential_research",
            description="Orchestrates research phase in sequential order"
        )

        # Create adapted sub-agents
        self.dest_adapter = ADKAgentAdapter(DestinationIntelligenceAgent())
        self.imm_adapter = ADKAgentAdapter(ImmigrationSpecialistAgent())
        self.fin_adapter = ADKAgentAdapter(FinancialAdvisorAgent())

        # ADK SequentialAgent for execution
        self.adk_sequential = SequentialAgent(
            name="research_sequential",
            sub_agents=[
                self.dest_adapter,
                self.imm_adapter,
                self.fin_adapter
            ]
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute with custom data transformation.
        Instead of using ADK directly, we manually orchestrate with transformations.
        """
        results = {}
        accumulated_data = input_data.copy()

        # Execute agents sequentially with custom transformations
        # Agent 1: Destination Intelligence
        dest_input = self._prepare_agent_input("destination", accumulated_data, results)
        dest_result = await self.dest_adapter.custom_agent.execute(dest_input)
        results["destination"] = dest_result
        accumulated_data = self._accumulate_data(accumulated_data, "destination", dest_result)

        # Agent 2: Immigration Specialist
        imm_input = self._prepare_agent_input("immigration", accumulated_data, results)
        imm_result = await self.imm_adapter.custom_agent.execute(imm_input)
        results["immigration"] = imm_result
        accumulated_data = self._accumulate_data(accumulated_data, "immigration", imm_result)

        # Agent 3: Financial Advisor
        fin_input = self._prepare_agent_input("financial", accumulated_data, results)
        fin_result = await self.fin_adapter.custom_agent.execute(fin_input)
        results["financial"] = fin_result

        # Compile research report
        research_report = self._compile_research_report(results, input_data)

        return {
            "status": "success",
            "phase": "research",
            "results": results,
            "research_report": research_report,
            # ... existing fields
        }

    # Keep existing _prepare_agent_input, _accumulate_data, _compile_research_report methods
```

**Alternative**: If we can't get custom data flow working with ADK, keep the sequential agent as-is.

**Estimated Time**: 6 hours (complex data transformation logic)

---

## Phase 4: Refactor LoopBudgetOptimizer

**File to create**: `src/agents/adk_loop_optimizer.py`

```python
"""
Loop Budget Optimizer - Uses ADK's LoopAgent
"""
from google.adk.agents import LoopAgent
from .adk_adapter import ADKAgentAdapter
from .budget_analyzer import BudgetAnalyzerAgent  # Existing agent


budget_analyzer_adapter = ADKAgentAdapter(BudgetAnalyzerAgent())

loop_budget_optimizer = LoopAgent(
    name="loop_budget_optimizer",
    sub_agent=budget_analyzer_adapter,
    max_iterations=5,
    # convergence_check=lambda result: result.get("status") == "success"  # May need custom function
    description="Iterates budget optimization until convergence"
)
```

**Estimated Time**: 3 hours

---

## Phase 5: Update Orchestrator

**File**: `src/agents/orchestrator.py`

Update to use refactored workflow agents.

**Estimated Time**: 3 hours

---

## Revised Estimates

| Phase | Task | Time | Risk |
|-------|------|------|------|
| 1 | Create ADK Adapter | 2h | Medium |
| 2 | Refactor ParallelBookingAgent | 4h | Medium |
| 3 | Refactor SequentialResearchAgent | 6h | High |
| 4 | Refactor LoopBudgetOptimizer | 3h | Low |
| 5 | Update Orchestrator | 3h | Medium |
| **Testing** | Integration tests | 4h | High |
| **TOTAL** | | **22 hours** | |

---

## Decision Point

Before proceeding, we need to answer:

### Research Questions

1. **InvocationContext**: How do we create it from our input dict?
2. **Event Extraction**: How do we get the final result from the event stream?
3. **Data Transformation**: Can we inject custom logic between ADK SequentialAgent sub-agents?

**Recommendation**: Start with **Phase 1 (ADK Adapter)** as a proof of concept. Once we validate the adapter works, proceed with other phases.

---

## Next Steps

1. Research `InvocationContext` usage
2. Create minimal prototype of `ADKAgentAdapter`
3. Test with one simple agent
4. If successful, proceed with full refactoring
5. If blockers found, document and reassess approach

**Your approval needed**: Should I proceed with Phase 1 (ADK Adapter prototype)?
