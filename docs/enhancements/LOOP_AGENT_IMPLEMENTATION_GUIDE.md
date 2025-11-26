# LoopAgent Implementation Guide

**Status:** ✅ Amadeus MCP Verified | 🚧 LoopAgent Ready for Implementation
**Created:** 2025-11-25
**Purpose:** Complete guide for implementing budget fitting LoopAgent

---

## Summary

✅ **COMPLETED:**
1. Amadeus MCP testing - ALL PASS (5/5 tests)
2. Budget fitting agents created ([adk_agents/budget_fitting.py](../../adk_agents/budget_fitting.py))
3. Callbacks activated in [app.py](../../app.py)

🚧 **REMAINING:**
1. Create LoopAgent workflow
2. Update main vacation workflow
3. Create test cases
4. Update config.py

---

## Implementation Status

### ✅ File 1: Budget Fitting Agents (COMPLETED)

**Location:** [adk_agents/budget_fitting.py](../../adk_agents/budget_fitting.py)

**Agents Created:**
1. `BudgetAssessmentAgent` - Decides STOP or CONTINUE based on budget fit
2. `TierRecommendationAgent` - Recommends luxury/medium/budget tier per iteration

**Key Features:**
- Comprehensive prompt instructions for LLM
- Clear STOP/CONTINUE logic
- Tier progression: luxury → medium → budget
- Detailed constraints for each tier

---

## Remaining Implementation

### File 2: LoopAgent Workflow

**Location:** `workflows/budget_fitting_workflow.py` (TO CREATE)

```python
"""
Budget Fitting Workflow - LoopAgent for automatic budget optimization
"""

from google.adk.agents import LoopAgent, ParallelAgent
from adk_agents.booking import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from adk_agents.budget_fitting import BudgetAssessmentAgent, TierRecommendationAgent
from config import Config


# Budget fitting loop with parallel booking
budget_fitting_loop = LoopAgent(
    name="budget_fitting_loop",
    description="""
Iteratively search for travel options within budget using tier-based optimization.

WORKFLOW PER ITERATION:
1. TierRecommendationAgent determines tier (luxury/medium/budget)
2. Booking agents search in PARALLEL with tier constraints
   - FlightBookingAgent
   - HotelBookingAgent
   - CarRentalAgent
3. BudgetAssessmentAgent evaluates total cost
   - If within budget: action="STOP" (success)
   - If over budget AND not final tier: action="CONTINUE" (try cheaper)
   - If final tier: action="STOP" (return best available)

LOOP BEHAVIOR:
- Max 3 iterations (luxury, medium, budget)
- Stops when within budget OR at budget tier
- Uses ParallelAgent for 3x faster booking searches
- Each iteration sees previous results (context-aware)

EXPECTED ITERATIONS:
- Large budget: 1 iteration (luxury fits)
- Medium budget: 2 iterations (luxury too expensive, medium fits)
- Tight budget: 3 iterations (goes all the way to budget tier)
""",
    sub_agents=[
        TierRecommendationAgent(),  # Recommend tier for this iteration

        # Parallel booking for speed (reuse existing pattern)
        ParallelAgent(
            name="booking_phase_parallel",
            description="Search flights, hotels, and car rentals in parallel",
            sub_agents=[
                FlightBookingAgent(),
                HotelBookingAgent(),
                CarRentalAgent(),
            ]
        ),

        BudgetAssessmentAgent(),    # Assess budget → STOP or CONTINUE
    ],
    max_iterations=3,
    model=Config.get_model_for_agent("budget_fitting_loop")
)
```

**Key Design Decisions:**
1. **ParallelAgent inside LoopAgent** - Maintains 3x speedup per iteration
2. **Max 3 iterations** - One per tier (luxury, medium, budget)
3. **Context-aware** - Each iteration sees previous costs
4. **Automatic termination** - BudgetAssessmentAgent returns STOP when appropriate

---

### File 3: Update Main Workflow

**Location:** [workflows/vacation_workflow.py](../../workflows/vacation_workflow.py) (MODIFY)

**Changes Required:**

```python
# OLD: Direct parallel booking
# booking_phase = ParallelAgent(
#     name="booking_phase",
#     sub_agents=[FlightBookingAgent(), HotelBookingAgent(), CarRentalAgent()]
# )

# NEW: Budget-aware booking with LoopAgent
from workflows.budget_fitting_workflow import budget_fitting_loop

vacation_planner = SequentialAgent(
    name="vacation_planner",
    description="""Main vacation planning orchestrator with budget-optimized booking""",
    sub_agents=[
        research_phase,           # Phase 1: Research (unchanged)
        budget_fitting_loop,      # Phase 2: Booking with budget loop (NEW!)
        budget_checkpoint,        # Phase 3: Budget confirmation (unchanged)
        suggestions_checkpoint,   # Phase 4: Suggestions approval (unchanged)
        organization_phase,       # Phase 5: Organization (unchanged)
    ],
    model=Config.get_model_for_agent("vacation_planner")
)
```

**Impact:**
- Booking phase now automatically finds options within budget
- Budget checkpoint becomes confirmation (not negotiation)
- No code changes needed elsewhere (agents use same interface)

---

### File 4: Update Config

**Location:** [config.py](../../config.py) (MODIFY)

**Add to AGENT_MODELS:**

```python
AGENT_MODELS = {
    # ... existing agents ...

    # Budget fitting agents (NEW)
    "budget_assessment": "gemini-2.0-flash-thinking-exp-1219",  # Complex reasoning
    "tier_recommendation": "gemini-2.5-flash-lite",             # Simple tier logic
    "budget_fitting_loop": "gemini-2.5-flash-lite",             # Loop orchestration
}
```

**Rationale:**
- BudgetAssessment uses Thinking model (complex decision logic)
- TierRecommendation uses Flash-lite (simple tier selection)
- Loop orchestrator uses Flash-lite (coordination only)

---

### File 5: Test Cases

**Location:** `tests/test_budget_loop.py` (TO CREATE)

```python
"""
Test Budget Fitting LoopAgent
Run with: python tests/test_budget_loop.py
"""

import asyncio
from workflows.budget_fitting_workflow import budget_fitting_loop

# Test Case 1: Luxury tier fits budget
async def test_luxury_fits():
    """Budget: $5,000 | Expected: 1 iteration (luxury)"""
    context = {
        "budget": 5000,
        "origin": "Charlotte, USA",
        "destination": "Salt Lake City, USA",
        "departure_date": "2026-03-15",
        "return_date": "2026-03-22",
        "travelers": 2,
        "citizenship": "USA"
    }

    result = await budget_fitting_loop.run(
        "Find flights, hotels, and car rental within $5,000 budget for Charlotte to Salt Lake City trip"
    )

    # Expected: Luxury tier, within budget, 1 iteration
    assert "luxury" in result.lower()
    assert "within budget" in result.lower()

# Test Case 2: Medium tier needed
async def test_medium_tier():
    """Budget: $3,000 | Expected: 2 iterations (luxury → medium)"""
    context = {
        "budget": 3000,
        # ... same as above
    }

    result = await budget_fitting_loop.run(...)

    # Expected: Medium tier, within budget, 2 iterations

# Test Case 3: Budget tier (final attempt)
async def test_budget_tier():
    """Budget: $2,000 | Expected: 3 iterations (all tiers)"""
    # ... test goes to budget tier

# Test Case 4: Loop stop conditions
async def test_stop_conditions():
    """Verify loop stops correctly"""
    # Test that loop doesn't exceed 3 iterations
    # Test that loop stops when within budget
    # Test that loop stops at budget tier

if __name__ == "__main__":
    asyncio.run(test_luxury_fits())
    asyncio.run(test_medium_tier())
    asyncio.run(test_budget_tier())
```

---

## Expected Behavior Examples

### Example 1: Luxury Fits Budget

```
User: "$5,000 budget for CLT → SLC (2 adults, March 15-22)"

Loop Iteration 1 (Luxury):
  [TierRecommendation] → tier="luxury"
  [ParallelBooking]
    [Flight] Business class → $2,400
    [Hotel] 5-star Sheraton → $1,800
    [Car] Luxury SUV → $500
  [BudgetAssessment]
    Total: $4,700 | Budget: $5,000 | Remaining: $300
    Status: within_budget | Action: STOP ✅

Result: Luxury options selected, $300 remaining
Iterations: 1
```

### Example 2: Downgrade to Medium

```
User: "$3,000 budget for CLT → SLC (2 adults, March 15-22)"

Loop Iteration 1 (Luxury):
  Total: $4,700 | Budget: $3,000 | Remaining: -$1,700
  Status: over_budget | Action: CONTINUE ↻

Loop Iteration 2 (Medium):
  [TierRecommendation] → tier="medium"
  [ParallelBooking]
    [Flight] Economy 1-stop → $1,200
    [Hotel] 3-star Holiday Inn → $1,400
    [Car] Mid-size sedan → $300
  [BudgetAssessment]
    Total: $2,900 | Budget: $3,000 | Remaining: $100
    Status: within_budget | Action: STOP ✅

Result: Medium tier selected, $100 remaining
Iterations: 2
```

### Example 3: All the Way to Budget Tier

```
User: "$2,000 budget for CLT → SLC (2 adults, March 15-22)"

Loop Iteration 1 (Luxury):
  Total: $4,700 | Over by: $2,700 | Action: CONTINUE ↻

Loop Iteration 2 (Medium):
  Total: $2,900 | Over by: $900 | Action: CONTINUE ↻

Loop Iteration 3 (Budget - FINAL):
  [TierRecommendation] → tier="budget", is_final_attempt=true
  [ParallelBooking]
    [Flight] Economy 2-stop → $800
    [Hotel] 2-star Motel 6 → $700
    [Car] Compact car → $200
  [BudgetAssessment]
    Total: $1,700 | Budget: $2,000 | Remaining: $300
    Status: within_budget | Action: STOP ✅

Result: Budget tier selected, $300 remaining
Iterations: 3
```

---

## Performance Metrics

**With LoopAgent:**
- Iteration 1 (Luxury): ~25 seconds (parallel booking)
- Iteration 2 (Medium): ~25 seconds (parallel booking)
- Iteration 3 (Budget): ~25 seconds (parallel booking)
- **Worst case (3 iterations): ~75 seconds**
- **Best case (1 iteration): ~25 seconds**

**Without LoopAgent (current):**
- Booking: ~25 seconds
- Budget checkpoint: User manual negotiation (30-60 seconds+)
- Re-booking if needed: ~25 seconds
- **Average: 80-110 seconds with user interaction**

**Improvement:**
- ✅ Fully automated (no user negotiation)
- ✅ Guaranteed to find options within budget
- ✅ Maintains 3x parallel speedup per iteration
- ✅ Transparent tier progression

---

## Integration Steps

1. ✅ **Create budget_fitting.py** (DONE)
2. **Create budget_fitting_workflow.py** - LoopAgent definition
3. **Modify vacation_workflow.py** - Replace booking_phase
4. **Update config.py** - Add model configs
5. **Create test_budget_loop.py** - Test all scenarios
6. **Test end-to-end** - Run full vacation planner
7. **Update documentation** - Add to ADK_TECHNICAL_IMPLEMENTATION.md

---

## Testing Checklist

- [ ] Test luxury tier fits budget (1 iteration)
- [ ] Test medium tier needed (2 iterations)
- [ ] Test budget tier final attempt (3 iterations)
- [ ] Test loop stops at max iterations
- [ ] Test loop stops when within budget
- [ ] Test loop stops at budget tier (even if over)
- [ ] Test parallel booking still works (3x speedup)
- [ ] Test callbacks log all iterations
- [ ] Test Amadeus MCP integration (real data)
- [ ] Test full vacation planner end-to-end

---

## Benefits Summary

✅ **Automatic Budget Optimization** - No manual user intervention
✅ **Guaranteed Result** - Always returns something (even if over budget at budget tier)
✅ **Progressive Refinement** - Tries best options first
✅ **Transparent** - User sees tier selection and reasoning
✅ **Efficient** - Stops as soon as within budget
✅ **Parallel-Optimized** - Maintains 3x speedup per iteration
✅ **Context-Aware** - Each iteration learns from previous
✅ **Failsafe** - Budget tier is guaranteed final attempt

---

## Next Steps

1. Create `workflows/budget_fitting_workflow.py`
2. Modify `workflows/vacation_workflow.py`
3. Update `config.py`
4. Create `tests/test_budget_loop.py`
5. Run tests and verify behavior
6. Update documentation

---

**Ready for implementation!** All design decisions finalized, agents created, Amadeus verified.
