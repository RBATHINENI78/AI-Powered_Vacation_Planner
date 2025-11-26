"""
Budget Fitting Workflow - LoopAgent for Automatic Budget Optimization

This workflow uses ADK's LoopAgent to iteratively search for travel options
within budget by trying progressively cheaper tiers (luxury → medium → budget).

Key Features:
- Automatic tier progression (no user intervention)
- Maintains parallel booking speedup (3x faster)
- Guaranteed result (budget tier is final attempt)
- Context-aware (each iteration sees previous results)
"""

from google.adk.agents import LoopAgent, ParallelAgent
from adk_agents.booking import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from adk_agents.budget_fitting import BudgetAssessmentAgent, TierRecommendationAgent
from config import Config


# Budget fitting loop with parallel booking for speed
budget_fitting_loop = LoopAgent(
    name="budget_fitting_loop",
    description="""
Iteratively search for travel options within budget using tier-based optimization.

**WORKFLOW PER ITERATION:**

1. **TierRecommendationAgent** determines booking tier:
   - Iteration 1: "luxury" (business class, 5-star hotels, luxury cars)
   - Iteration 2: "medium" (economy class, 3-4 star hotels, standard cars)
   - Iteration 3: "budget" (economy class, 2-3 star hotels, compact cars)

2. **ParallelAgent** searches for bookings simultaneously (3x speedup):
   - FlightBookingAgent - Searches flights with tier constraints
   - HotelBookingAgent - Searches hotels with tier constraints
   - CarRentalAgent - Searches car rentals with tier constraints

3. **BudgetAssessmentAgent** evaluates total cost:
   - Calculates: total_cost = flights + hotels + car_rental
   - Compares: total_cost vs user's budget
   - Decision:
     * If within budget: action="STOP" ✅ (success, return options)
     * If over budget AND not final tier: action="CONTINUE" ↻ (try cheaper)
     * If over budget BUT final tier: action="STOP" ⚠️ (return best available)

**LOOP BEHAVIOR:**

- Max 3 iterations (one per tier)
- Stops when:
  a) Total cost ≤ budget (success at any tier)
  b) Reached budget tier (final attempt, regardless of fit)
  c) Max iterations reached (3 iterations)

- Each iteration sees previous results (context-aware)
- ParallelAgent maintains 3x speedup per iteration
- BudgetAssessmentAgent's action="STOP" terminates the loop

**EXPECTED EXECUTION PATTERNS:**

Pattern 1: Large Budget (1 iteration)
  User budget: $5,000
  Luxury tier: $4,700 → Within budget → STOP ✅
  Result: Luxury options, $300 remaining
  Time: ~25 seconds

Pattern 2: Medium Budget (2 iterations)
  User budget: $3,000
  Luxury tier: $4,700 → Over budget → CONTINUE ↻
  Medium tier: $2,900 → Within budget → STOP ✅
  Result: Medium options, $100 remaining
  Time: ~50 seconds

Pattern 3: Tight Budget (3 iterations)
  User budget: $2,000
  Luxury tier: $4,700 → Over budget → CONTINUE ↻
  Medium tier: $2,900 → Over budget → CONTINUE ↻
  Budget tier: $1,700 → Within budget → STOP ✅
  Result: Budget options, $300 remaining
  Time: ~75 seconds

Pattern 4: Very Tight Budget (3 iterations, over budget)
  User budget: $1,500
  Luxury tier: $4,700 → Over budget → CONTINUE ↻
  Medium tier: $2,900 → Over budget → CONTINUE ↻
  Budget tier: $1,700 → Over by $200 BUT final tier → STOP ⚠️
  Result: Budget options (best available), $200 over budget
  Time: ~75 seconds

**ADVANTAGES:**

✅ Automatic optimization - No manual user negotiation
✅ Efficient - Stops as soon as within budget
✅ Fast - Maintains parallel booking speedup (3x)
✅ Guaranteed result - Always returns something
✅ Transparent - User sees tier selection and reasoning
✅ Progressive refinement - Tries best options first
✅ Context-aware - Learns from previous iterations
✅ Observable - Full callback logging per iteration

**INTEGRATION:**

This LoopAgent replaces the simple ParallelAgent booking phase in the main
vacation workflow. It provides budget-aware booking while maintaining the
same interface and performance characteristics.
""",
    sub_agents=[
        # Agent 1: Recommend tier for this iteration
        TierRecommendationAgent(),

        # Agent 2: Search bookings in parallel (maintains 3x speedup)
        ParallelAgent(
            name="booking_phase_parallel",
            description="""
Search for flights, hotels, and car rentals simultaneously.

This ParallelAgent maintains the 3x speedup from the original booking phase
while allowing tier-based constraints to be applied per iteration.

Sub-agents run concurrently:
- FlightBookingAgent
- HotelBookingAgent
- CarRentalAgent

Total time: max(flight_time, hotel_time, car_time) ≈ 20-25 seconds
Sequential time would be: flight_time + hotel_time + car_time ≈ 60-75 seconds
Speedup: ~3x faster
""",
            sub_agents=[
                FlightBookingAgent(),
                HotelBookingAgent(),
                CarRentalAgent(),
            ]
        ),

        # Agent 3: Assess budget and decide STOP or CONTINUE
        BudgetAssessmentAgent(),
    ],
    max_iterations=3
)


# Alternative: SequentialAgent wrapper for booking (for testing)
# This version runs booking agents sequentially instead of in parallel.
# Use this for debugging or if parallel execution causes issues.
# Expected time: ~60-75 seconds per iteration vs ~25 seconds with parallel.

from google.adk.agents import SequentialAgent

budget_fitting_loop_sequential = LoopAgent(
    name="budget_fitting_loop_sequential",
    description="""Same as budget_fitting_loop but uses SequentialAgent instead of ParallelAgent.

Use this version for:
- Debugging loop behavior
- Testing tier progression
- Environments where parallel execution is problematic

Note: This will be ~3x slower per iteration but otherwise identical.
""",
    sub_agents=[
        TierRecommendationAgent(),

        SequentialAgent(
            name="booking_phase_sequential",
            description="Search for flights, hotels, and car rentals sequentially",
            sub_agents=[
                FlightBookingAgent(),
                HotelBookingAgent(),
                CarRentalAgent(),
            ]
        ),

        BudgetAssessmentAgent(),
    ],
    max_iterations=3
)


# Export the parallel version as default
__all__ = ['budget_fitting_loop', 'budget_fitting_loop_sequential']
