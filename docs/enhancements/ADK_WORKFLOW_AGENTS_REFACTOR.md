# ADK Workflow Agents Refactoring - Implementation Plan

**Feature**: Replace Custom Workflow Implementations with ADK Built-in Agents
**Branch**: `feature/adk-workflow-agents`
**Status**: Planning
**Priority**: High
**Estimated Effort**: 4-6 hours
**Created**: 2025-11-21

---

## Problem Statement

### Current Implementation

The project currently uses **custom implementations** of workflow patterns instead of the official ADK workflow agents:

1. **ParallelBookingAgent** ([src/agents/parallel_agent.py](../../src/agents/parallel_agent.py))
   - Custom `asyncio.gather()` implementation
   - Manual task tracking and speedup calculation
   - 230+ lines of custom code

2. **SequentialResearchAgent** ([src/agents/sequential_agent.py](../../src/agents/sequential_agent.py))
   - Custom sequential execution with data accumulation
   - Manual state management
   - ~150+ lines of custom code

3. **LoopBudgetOptimizer** ([src/agents/loop_agent.py](../../src/agents/loop_agent.py))
   - Custom loop implementation with max iterations
   - Manual convergence checking
   - ~200+ lines of custom code

### Issues

1. **Code Duplication**: Reimplementing patterns that ADK already provides
2. **Maintenance Burden**: Need to maintain custom workflow logic
3. **Missing Features**: ADK agents have built-in optimizations we're not using
4. **Not Following Best Practices**: Official ADK documentation recommends using built-in agents
5. **Learning Curve**: New developers need to understand custom implementations vs ADK patterns

---

## Proposed Solution

### Approach: Replace Custom Agents with ADK Built-in Workflow Agents

**Import from**: `google.adk.agents`

Available workflow agents:
1. **ParallelAgent** - Concurrent execution of sub-agents
2. **SequentialAgent** - Sequential execution with data passing
3. **LoopAgent** - Iterative execution until convergence

### ADK Library Usage

```python
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
```

---

## Implementation Plan

### Phase 1: Parallel Agent Refactoring (2 hours)

#### 1.1 Replace ParallelBookingAgent with ADK ParallelAgent

**Current Code** ([src/agents/parallel_agent.py](../../src/agents/parallel_agent.py)):
```python
class ParallelBookingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="parallel_booking", ...)
        self.flight_agent = FlightBookingAgent()
        self.hotel_agent = HotelBookingAgent()
        self.car_agent = CarRentalAgent()
        self.experience_agent = ExperienceCuratorAgent()

    async def _execute_impl(self, input_data):
        tasks = []
        for task_name, agent in self.parallel_tasks:
            task = asyncio.create_task(
                self._execute_with_tracking(task_name, agent, task_input)
            )
            tasks.append(task)

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        # ... manual result processing ...
```

**Proposed Refactor**:
```python
from google.adk.agents import ParallelAgent
from .booking_agents import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from .experience_curator import ExperienceCuratorAgent

# Create parallel booking agent using ADK ParallelAgent
parallel_booking_agent = ParallelAgent(
    name="parallel_booking",
    sub_agents=[
        FlightBookingAgent(),
        HotelBookingAgent(),
        CarRentalAgent(),
        ExperienceCuratorAgent()
    ],
    description="Orchestrates booking phase with parallel execution"
)
```

**Benefits**:
- Reduces code from 230+ lines to ~15 lines
- Automatic event handling and branch management
- Built-in exception handling
- Proper invocation context isolation for sub-agents

---

### Phase 2: Sequential Agent Refactoring (1.5 hours)

#### 2.1 Replace SequentialResearchAgent with ADK SequentialAgent

**Current Code** ([src/agents/sequential_agent.py](../../src/agents/sequential_agent.py)):
```python
class SequentialResearchAgent(BaseAgent):
    async def _execute_impl(self, input_data):
        accumulated_data = {}

        # Execute agents sequentially
        dest_result = await self.destination_agent.execute(input_data)
        accumulated_data["destination"] = dest_result

        visa_result = await self.immigration_agent.execute(input_data)
        accumulated_data["visa"] = visa_result

        currency_result = await self.financial_agent.execute(input_data)
        accumulated_data["currency"] = currency_result

        return accumulated_data
```

**Proposed Refactor**:
```python
from google.adk.agents import SequentialAgent

sequential_research_agent = SequentialAgent(
    name="sequential_research",
    sub_agents=[
        DestinationIntelligenceAgent(),
        ImmigrationSpecialistAgent(),
        FinancialAdvisorAgent()
    ],
    description="Runs research agents sequentially with data accumulation"
)
```

**Benefits**:
- Reduces code from 150+ lines to ~12 lines
- Automatic data passing between agents
- Built-in state management
- Proper event streaming

---

### Phase 3: Loop Agent Refactoring (1.5 hours)

#### 3.1 Replace LoopBudgetOptimizer with ADK LoopAgent

**Current Code** ([src/agents/loop_agent.py](../../src/agents/loop_agent.py)):
```python
class LoopBudgetOptimizer(BaseAgent):
    async def _execute_impl(self, input_data):
        iteration = 0
        max_iterations = 5

        while iteration < max_iterations:
            # Check budget fit
            result = await self._check_budget(input_data)

            if result["status"] == "success":
                break  # Converged

            # Apply optimization strategy
            input_data = self._apply_strategy(input_data, iteration)
            iteration += 1

        return result
```

**Proposed Refactor**:
```python
from google.adk.agents import LoopAgent

loop_budget_optimizer = LoopAgent(
    name="loop_budget_optimizer",
    sub_agent=BudgetAnalyzerAgent(),  # Single agent to loop
    max_iterations=5,
    convergence_check=lambda result: result.get("status") == "success",
    description="Iterates budget optimization until convergence"
)
```

**Benefits**:
- Reduces code from 200+ lines to ~10 lines
- Built-in convergence checking
- Automatic iteration tracking
- Proper loop termination handling

---

### Phase 4: Update Orchestrator (1 hour)

#### 4.1 Update OrchestratorAgent to use new workflow agents

**File**: [src/agents/orchestrator.py](../../src/agents/orchestrator.py)

**Changes**:
```python
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent
from .booking_agents import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from .experience_curator import ExperienceCuratorAgent
from .destination_intelligence import DestinationIntelligenceAgent
from .immigration_specialist import ImmigrationSpecialistAgent
from .financial_advisor import FinancialAdvisorAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)

        # Use ADK workflow agents
        self.research_agent = SequentialAgent(
            name="sequential_research",
            sub_agents=[
                DestinationIntelligenceAgent(),
                ImmigrationSpecialistAgent(),
                FinancialAdvisorAgent()
            ],
            description="Runs research agents sequentially"
        )

        self.booking_agent = ParallelAgent(
            name="parallel_booking",
            sub_agents=[
                FlightBookingAgent(),
                HotelBookingAgent(),
                CarRentalAgent(),
                ExperienceCuratorAgent()
            ],
            description="Runs booking agents in parallel"
        )

        self.optimizer_agent = LoopAgent(
            name="loop_budget_optimizer",
            sub_agent=BudgetAnalyzerAgent(),
            max_iterations=5,
            convergence_check=lambda r: r.get("status") == "success",
            description="Optimizes budget iteratively"
        )
```

---

## Migration Strategy

### Step-by-Step Migration

1. **Create feature branch**: `git checkout -b feature/adk-workflow-agents`

2. **Phase 1: Parallel Agent**
   - Create new file: `src/agents/adk_parallel_booking.py`
   - Implement using `ParallelAgent`
   - Test parallel execution
   - Update orchestrator to use new agent
   - Remove old `parallel_agent.py` after validation

3. **Phase 2: Sequential Agent**
   - Create new file: `src/agents/adk_sequential_research.py`
   - Implement using `SequentialAgent`
   - Test sequential data accumulation
   - Update orchestrator
   - Remove old `sequential_agent.py`

4. **Phase 3: Loop Agent**
   - Create new file: `src/agents/adk_loop_optimizer.py`
   - Implement using `LoopAgent`
   - Test convergence logic
   - Update orchestrator
   - Remove old `loop_agent.py`

5. **Phase 4: Integration Testing**
   - Test full vacation planning workflow
   - Verify performance improvements
   - Validate A2A communication still works
   - Check observability (tracing, metrics)

6. **Phase 5: Documentation**
   - Update [docs/actual/ADK_FEATURES_IMPLEMENTED.md](../../docs/actual/ADK_FEATURES_IMPLEMENTED.md)
   - Update [docs/actual/ARCHITECTURE_COMPARISON.md](../../docs/actual/ARCHITECTURE_COMPARISON.md)
   - Update workflow pattern documentation

---

## Expected Benefits

### Code Reduction
| Agent | Before (LOC) | After (LOC) | Reduction |
|-------|-------------|------------|-----------|
| ParallelBookingAgent | 230 | 15 | **93%** |
| SequentialResearchAgent | 150 | 12 | **92%** |
| LoopBudgetOptimizer | 200 | 10 | **95%** |
| **Total** | **580** | **37** | **94%** |

### Feature Improvements
1. **Built-in Event Streaming**: ADK agents handle event propagation automatically
2. **Invocation Context Isolation**: Proper branch management for sub-agents
3. **Exception Handling**: Built-in error handling and recovery
4. **State Management**: Automatic state tracking
5. **Performance**: ADK-optimized execution patterns

### Maintenance Benefits
1. **Less Custom Code**: 580 → 37 lines (94% reduction)
2. **Official ADK Patterns**: Following best practices
3. **Easier Onboarding**: New developers familiar with ADK will understand immediately
4. **Automatic Updates**: ADK improvements benefit us automatically

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_adk_workflow_agents.py` (NEW)

```python
import pytest
from google.adk.agents import ParallelAgent, SequentialAgent, LoopAgent

@pytest.mark.asyncio
async def test_parallel_booking_agent():
    """Test ParallelAgent with booking sub-agents."""
    parallel_agent = ParallelAgent(
        name="parallel_booking",
        sub_agents=[
            MockFlightAgent(),
            MockHotelAgent()
        ]
    )

    result = await parallel_agent.execute({...})
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_sequential_research_agent():
    """Test SequentialAgent with research sub-agents."""
    sequential_agent = SequentialAgent(
        name="sequential_research",
        sub_agents=[
            MockDestinationAgent(),
            MockImmigrationAgent()
        ]
    )

    result = await sequential_agent.execute({...})
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_loop_budget_optimizer():
    """Test LoopAgent with budget optimization."""
    loop_agent = LoopAgent(
        name="loop_optimizer",
        sub_agent=MockBudgetAgent(),
        max_iterations=5
    )

    result = await loop_agent.execute({...})
    assert result["iterations"] <= 5
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **ADK API marked @experimental** | High | Monitor ADK releases, maintain fallback to custom implementation |
| **Breaking changes in ADK** | Medium | Pin ADK version, test before upgrading |
| **Performance regression** | Medium | Benchmark before/after, optimize if needed |
| **A2A communication breaks** | High | Test message passing thoroughly, validate handlers |
| **Event streaming issues** | Medium | Test with observability enabled, validate callbacks |

---

## Documentation Updates

Files to update after refactoring:

1. **[docs/actual/ADK_FEATURES_IMPLEMENTED.md](../../docs/actual/ADK_FEATURES_IMPLEMENTED.md)**
   - Update "Workflow Patterns" section
   - Add note about using ADK built-in agents
   - Document import paths

2. **[docs/actual/ARCHITECTURE_COMPARISON.md](../../docs/actual/ARCHITECTURE_COMPARISON.md)**
   - Update workflow execution patterns diagrams
   - Note transition to ADK agents

3. **[docs/actual/README.md](../../docs/actual/README.md)**
   - Update technology stack
   - Note use of official ADK workflow agents

4. **[README.md](../../README.md)**
   - Update features list
   - Highlight ADK library usage

---

## Implementation Checklist

### Phase 1: Parallel Agent
- [ ] Create `src/agents/adk_parallel_booking.py`
- [ ] Implement using `ParallelAgent` from `google.adk.agents`
- [ ] Test parallel execution with 4 sub-agents
- [ ] Verify performance (should maintain 3-4x speedup)
- [ ] Update orchestrator to use new agent
- [ ] Remove old `src/agents/parallel_agent.py`

### Phase 2: Sequential Agent
- [ ] Create `src/agents/adk_sequential_research.py`
- [ ] Implement using `SequentialAgent`
- [ ] Test data accumulation across 3 agents
- [ ] Verify A2A messaging works
- [ ] Update orchestrator
- [ ] Remove old `src/agents/sequential_agent.py`

### Phase 3: Loop Agent
- [ ] Create `src/agents/adk_loop_optimizer.py`
- [ ] Implement using `LoopAgent`
- [ ] Test convergence logic (max 5 iterations)
- [ ] Verify HITL budget checkpoint
- [ ] Update orchestrator
- [ ] Remove old `src/agents/loop_agent.py`

### Phase 4: Testing
- [ ] Write unit tests for all 3 workflow agents
- [ ] Integration test full vacation planning workflow
- [ ] Performance benchmark (compare before/after)
- [ ] Validate observability (tracing + metrics)

### Phase 5: Documentation
- [ ] Update ADK_FEATURES_IMPLEMENTED.md
- [ ] Update ARCHITECTURE_COMPARISON.md
- [ ] Update README.md
- [ ] Add migration notes to PR description

---

## References

- [ADK Parallel Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [ADK Sequential Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [ADK Loop Agents Documentation](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Current Custom Implementations](../../src/agents/)

---

**Status**: Ready for implementation
**Next Step**: Create feature branch and start with Phase 1 (Parallel Agent)

**Estimated Total Time**: 4-6 hours
**Expected Code Reduction**: 580 → 37 lines (94%)
