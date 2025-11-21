# Cleanup Recommendations & Action Plan

**Project**: AI-Powered Vacation Planner
**Last Updated**: 2025-11-20
**Priority**: Medium
**Estimated Effort**: 2-3 hours

---

## Table of Contents
1. [Quick Summary](#quick-summary)
2. [Immediate Actions](#immediate-actions)
3. [Short-Term Actions](#short-term-actions)
4. [Long-Term Actions](#long-term-actions)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)

---

## Quick Summary

### What Needs to Be Done

| Priority | Action | Files | Time | Impact |
|----------|--------|-------|------|--------|
| HIGH | Delete obsolete tools | 6 files | 30 min | Cleanup dead code |
| MEDIUM | Update test_tools.py | 1 file | 1 hour | Enable async testing |
| LOW | Complete Amadeus flights | 1 file | 2 hours | Full booking integration |

### Expected Outcomes
- 881 lines of code removed
- Clear agent-only architecture
- Better test coverage
- Complete booking workflow

---

## Immediate Actions

### 1. Delete Obsolete Tool Files

**Priority**: HIGH
**Effort**: 30 minutes
**Risk**: LOW

#### Files to Delete (6 total)

```bash
src/tools/
├── __init__.py          # 828 bytes
├── weather_tool.py      # 5.0 KB
├── currency_tool.py     # 4.0 KB
├── budget_tool.py       # 5.1 KB
├── visa_tool.py         # 7.7 KB
└── pii_detector.py      # 4.9 KB
```

**Total Cleanup**: ~27.5 KB, 881 lines

#### Execution Steps

```bash
# 1. Create backup branch
git checkout -b cleanup/remove-obsolete-tools
git push origin cleanup/remove-obsolete-tools

# 2. Verify no dependencies (should return no results)
echo "Checking for imports..."
grep -r "from src.tools import" --include="*.py" .
grep -r "WeatherTool\|CurrencyTool\|BudgetTool\|VisaTool\|PIIDetector" \
  --include="*.py" src/ agents/

# 3. Delete files
cd /Users/rbathineni/Documents/GoogleADK/AI-Powered_Vacation_Planner
rm src/tools/weather_tool.py
rm src/tools/currency_tool.py
rm src/tools/budget_tool.py
rm src/tools/visa_tool.py
rm src/tools/pii_detector.py
rm src/tools/__init__.py

# 4. Remove __pycache__ if exists
rm -rf src/tools/__pycache__

# 5. Optionally remove empty directory
rm -rf src/tools/

# 6. Verify application still works
cd agents/vacation_planner
python -c "from agent import root_agent; print('✓ Agent loads successfully')"

# 7. Stage and commit
git add -A
git commit -m "refactor: Remove obsolete tools replaced by agents

DELETED (881 lines, ~27.5 KB):
- src/tools/weather_tool.py → DestinationIntelligenceAgent
- src/tools/currency_tool.py → FinancialAdvisorAgent
- src/tools/budget_tool.py → FinancialAdvisorAgent
- src/tools/visa_tool.py → ImmigrationSpecialistAgent
- src/tools/pii_detector.py → SecurityGuardianAgent
- src/tools/__init__.py

All functionality preserved in agent implementations with enhanced features."

# 8. Push changes
git push origin cleanup/remove-obsolete-tools
```

#### Verification Checklist

- [ ] Backup branch created
- [ ] No import references found
- [ ] Files deleted successfully
- [ ] Application starts without errors
- [ ] Test vacation planning request works
- [ ] All 7 FunctionTools still available
- [ ] Agents execute correctly
- [ ] Committed with clear message

#### Expected Results

**Before**:
```
src/
├── agents/          (11 files, ~3500 lines)
├── tools/           (6 files, ~881 lines)  ← DELETE THIS
├── callbacks/       (2 files, ~217 lines)
└── mcp_servers/     (4 files, ~600 lines)
```

**After**:
```
src/
├── agents/          (11 files, ~3500 lines)
├── callbacks/       (2 files, ~217 lines)
└── mcp_servers/     (4 files, ~600 lines)
```

**Impact**: -881 lines, cleaner architecture, agent-only pattern

---

## Short-Term Actions

### 2. Update test_tools.py for Async Interface

**Priority**: MEDIUM
**Effort**: 1 hour
**Risk**: LOW

#### Current State
```python
# test_tools.py - Current sync implementation
def test_weather_tool():
    tool = WeatherTool()
    result = tool.get_current_weather("Paris", "France")
    assert result is not None
```

#### Problem
- Tests reference deleted tools
- No async support
- Not integrated in CI/CD

#### Solution: Migrate to Agent Tests

**File**: Create `tests/test_agents.py`

```python
"""
Test suite for agent implementations
Replaces test_tools.py with async agent testing
"""

import pytest
import asyncio
from src.agents.destination_intelligence import DestinationIntelligenceAgent
from src.agents.immigration_specialist import ImmigrationSpecialistAgent
from src.agents.financial_advisor import FinancialAdvisorAgent
from src.agents.security_guardian import SecurityGuardianAgent


class TestDestinationIntelligence:
    """Test DestinationIntelligenceAgent (replaces WeatherTool tests)"""

    @pytest.mark.asyncio
    async def test_get_weather(self):
        agent = DestinationIntelligenceAgent()
        result = await agent.execute({
            "city": "Paris",
            "country": "France"
        })

        assert result["status"] == "success"
        assert "current_weather" in result
        assert "forecast" in result
        assert "packing_list" in result

    @pytest.mark.asyncio
    async def test_weather_with_severe_conditions(self):
        agent = DestinationIntelligenceAgent()
        # Test with city known for extreme weather
        result = await agent.execute({
            "city": "Phoenix",
            "country": "USA"
        })

        analysis = result.get("analysis", {})
        # Phoenix often has high temps
        assert "travel_conditions" in analysis


class TestImmigrationSpecialist:
    """Test ImmigrationSpecialistAgent (replaces VisaTool tests)"""

    @pytest.mark.asyncio
    async def test_visa_check_us_to_france(self):
        agent = ImmigrationSpecialistAgent()
        result = await agent.execute({
            "citizenship": "US",
            "destination": "Paris, France",
            "duration_days": 14
        })

        assert result["status"] == "success"
        assert "visa_requirements" in result
        visa_req = result["visa_requirements"]
        assert "required" in visa_req
        # US to France for 14 days = tourist visa waiver
        assert visa_req["required"] == False

    @pytest.mark.asyncio
    async def test_visa_check_with_long_duration(self):
        agent = ImmigrationSpecialistAgent()
        result = await agent.execute({
            "citizenship": "India",
            "destination": "London, UK",
            "duration_days": 180
        })

        assert result["status"] == "success"
        visa_req = result["visa_requirements"]
        # Long stay requires visa
        assert "required_documents" in result


class TestFinancialAdvisor:
    """Test FinancialAdvisorAgent (replaces CurrencyTool + BudgetTool)"""

    @pytest.mark.asyncio
    async def test_currency_and_budget(self):
        agent = FinancialAdvisorAgent()
        result = await agent.execute({
            "origin": "New York",
            "destination": "Paris, France",
            "budget": 3000,
            "travelers": 2,
            "nights": 7,
            "travel_style": "moderate"
        })

        assert result["status"] == "success"
        assert "currency_info" in result
        assert "budget_breakdown" in result

        currency = result["currency_info"]
        assert "from_currency" in currency
        assert "to_currency" in currency
        assert "exchange_rate" in currency

        budget = result["budget_breakdown"]
        assert "flights" in budget
        assert "hotels" in budget
        assert "total" in budget

    @pytest.mark.asyncio
    async def test_budget_styles(self):
        agent = FinancialAdvisorAgent()

        # Test budget style
        budget_result = await agent.execute({
            "destination": "Tokyo, Japan",
            "budget": 1500,
            "travelers": 2,
            "nights": 5,
            "travel_style": "budget"
        })

        # Test luxury style
        luxury_result = await agent.execute({
            "destination": "Tokyo, Japan",
            "budget": 8000,
            "travelers": 2,
            "nights": 5,
            "travel_style": "luxury"
        })

        # Luxury should have higher per-night costs
        budget_breakdown = budget_result["budget_breakdown"]
        luxury_breakdown = luxury_result["budget_breakdown"]

        assert luxury_breakdown["hotels"] > budget_breakdown["hotels"]


class TestSecurityGuardian:
    """Test SecurityGuardianAgent (replaces PIIDetector)"""

    @pytest.mark.asyncio
    async def test_no_pii(self):
        agent = SecurityGuardianAgent()
        result = await agent.execute({
            "text": "I want to visit Paris for 7 days with my family."
        })

        assert result["status"] == "success"
        assert result["pii_detected"] == False
        assert result["risk_level"] == "none"
        assert result["safe_to_proceed"] == True

    @pytest.mark.asyncio
    async def test_critical_pii(self):
        agent = SecurityGuardianAgent()
        result = await agent.execute({
            "text": "My SSN is 123-45-6789 and credit card is 1234-5678-9012-3456"
        })

        assert result["pii_detected"] == True
        assert result["risk_level"] == "critical"
        assert result["safe_to_proceed"] == False
        assert len(result["findings"]) >= 2

    @pytest.mark.asyncio
    async def test_medium_pii(self):
        agent = SecurityGuardianAgent()
        result = await agent.execute({
            "text": "Contact me at john@example.com or 555-123-4567"
        })

        assert result["pii_detected"] == True
        assert result["risk_level"] == "medium"
        # Medium risk still allows proceeding
        assert result["safe_to_proceed"] == True


class TestCallbacks:
    """Test callback integration"""

    @pytest.mark.asyncio
    async def test_tool_callbacks(self):
        from src.callbacks.tool_callbacks import callback_manager

        # Clear event log
        callback_manager.event_log = []

        # Execute a tool wrapped with @with_callbacks
        from agents.vacation_planner.agent import get_weather_info
        result = await get_weather_info("Paris", "France")

        # Check callback events
        events = callback_manager.event_log
        assert len(events) >= 2  # before + after

        before_event = [e for e in events if e["event"] == "before_tool_execute"]
        after_event = [e for e in events if e["event"] == "after_tool_execute"]

        assert len(before_event) >= 1
        assert len(after_event) >= 1

    @pytest.mark.asyncio
    async def test_agent_metrics(self):
        agent = DestinationIntelligenceAgent()
        initial_count = agent.metrics["executions"]

        await agent.execute({"city": "London", "country": "UK"})

        assert agent.metrics["executions"] == initial_count + 1
        assert agent.metrics["total_time"] > 0


# Configure pytest
pytest_plugins = ['pytest_asyncio']
```

#### Execution Steps

```bash
# 1. Install pytest-asyncio if needed
pip install pytest pytest-asyncio

# 2. Create tests directory if it doesn't exist
mkdir -p tests

# 3. Create test_agents.py with content above
# (Use your editor or the Write tool)

# 4. Delete or archive old test_tools.py
mv test_tools.py test_tools.py.old

# 5. Run new tests
cd /Users/rbathineni/Documents/GoogleADK/AI-Powered_Vacation_Planner
pytest tests/test_agents.py -v

# Expected output:
# test_agents.py::TestDestinationIntelligence::test_get_weather PASSED
# test_agents.py::TestImmigrationSpecialist::test_visa_check_us_to_france PASSED
# test_agents.py::TestFinancialAdvisor::test_currency_and_budget PASSED
# test_agents.py::TestSecurityGuardian::test_no_pii PASSED
# ... etc

# 6. Commit changes
git add tests/test_agents.py test_tools.py.old
git commit -m "test: Migrate to async agent tests

CHANGES:
- Created tests/test_agents.py with async/await support
- Tests for all 5 core agents
- Callback integration tests
- Archived old test_tools.py

All tests use pytest-asyncio for proper async handling."
```

#### Benefits
- Modern async test suite
- Better coverage of agent features
- Tests A2A communication
- Tests observability (callbacks, metrics)
- Can be integrated in CI/CD

---

### 3. Optional: Directory Restructuring

**Priority**: LOW
**Effort**: 30 minutes
**Risk**: LOW

If you want even cleaner structure:

```bash
# Current structure
src/
├── agents/
├── callbacks/
├── mcp_servers/
└── utils/

# Optional cleaner structure
src/
├── core/
│   ├── agents/
│   ├── callbacks/
│   └── workflows/
├── integrations/
│   └── mcp_servers/
└── utils/
```

**Not Recommended**: Stick with current structure to avoid import changes.

---

## Long-Term Actions

### 4. Complete Amadeus Flight Integration

**Priority**: LOW
**Effort**: 2 hours
**Risk**: MEDIUM

#### Current State
```python
# src/agents/booking_agents.py - FlightBookingAgent
class FlightBookingAgent(BaseAgent):
    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Try Amadeus API
        try:
            amadeus_result = search_flights_amadeus_sync(...)
            if "error" not in amadeus_result:
                return {"status": "success", "source": "amadeus_api", ...}
        except Exception as e:
            logger.warning(f"Amadeus API failed: {e}")

        # FALLBACK: Use LLM to generate flight data
        return self._generate_flight_options_llm(...)
```

#### Problem
Amadeus flight search works but may hit test environment limitations.

#### Improvements Needed

1. **Better Error Handling**
   ```python
   async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
       # Try Amadeus with timeout
       try:
           async with asyncio.timeout(10):
               result = await search_flights_amadeus(...)
               if self._validate_amadeus_response(result):
                   return self._format_amadeus_flights(result)
       except asyncio.TimeoutError:
           logger.warning("Amadeus API timeout")
       except Exception as e:
           logger.error(f"Amadeus error: {e}")

       # Fallback to LLM
       return await self._generate_flight_options_llm(...)
   ```

2. **Response Validation**
   ```python
   def _validate_amadeus_response(self, result: Dict) -> bool:
       if "error" in result:
           return False
       if "data" not in result:
           return False
       if not result["data"]:
           return False
       return True
   ```

3. **Caching for Test Environment**
   ```python
   # Cache successful Amadeus responses
   _flight_cache = {}

   async def _get_cached_or_fetch(self, cache_key: str, fetch_func):
       if cache_key in self._flight_cache:
           logger.info("Using cached flight data")
           return self._flight_cache[cache_key]

       result = await fetch_func()
       if result.get("status") == "success":
           self._flight_cache[cache_key] = result

       return result
   ```

#### Action Plan

1. **Test Current Implementation**
   ```bash
   # Test with common routes
   python -c "
   from src.agents.booking_agents import FlightBookingAgent
   import asyncio

   async def test():
       agent = FlightBookingAgent()
       result = await agent.execute({
           'origin': 'NYC',
           'destination': 'PAR',
           'departure_date': '2025-12-15',
           'return_date': '2025-12-25',
           'travelers': 2
       })
       print(result.get('source'))  # Should be 'amadeus_api' or 'llm_fallback'

   asyncio.run(test())
   "
   ```

2. **Add Better Logging**
   ```python
   logger.info(f"[FLIGHT] Searching: {origin} → {destination}")
   logger.info(f"[FLIGHT] Source: {source}")
   logger.info(f"[FLIGHT] Options found: {len(options)}")
   ```

3. **Document Limitations**
   ```markdown
   # Amadeus API Limitations (Test Environment)

   - Limited city/airport support
   - Sample data only
   - Recommended cities: NYC, LAX, LON, PAR, TYO
   - Production API has full coverage
   ```

---

## Testing Strategy

### Pre-Cleanup Tests

Run these BEFORE deleting files:

```bash
# 1. Verify no imports
grep -r "from src.tools import" --include="*.py" .

# 2. Check application loads
cd agents/vacation_planner
python -c "from agent import root_agent; print('OK')"

# 3. Test a vacation request (manual)
adk web
# Navigate to UI, submit: "Plan a 7-day trip to Paris for 2 people"
```

### Post-Cleanup Tests

Run these AFTER deleting files:

```bash
# 1. Application still loads
cd agents/vacation_planner
python -c "from agent import root_agent; print('✓ Agent loaded')"

# 2. FunctionTools still available
python -c "
from agent import default_api
tools = default_api.tools
print(f'✓ {len(tools)} tools registered')
for tool in tools:
    print(f'  - {tool._function.__name__}')
"

# 3. Agents execute correctly
python -c "
import asyncio
from src.agents.destination_intelligence import DestinationIntelligenceAgent

async def test():
    agent = DestinationIntelligenceAgent()
    result = await agent.execute({'city': 'Paris', 'country': 'France'})
    assert result['status'] == 'success'
    print('✓ DestinationIntelligence works')

asyncio.run(test())
"

# 4. Full workflow test
python -c "
import asyncio
from src.agents.orchestrator import OrchestratorAgent

async def test():
    orch = OrchestratorAgent()
    result = await orch.plan_vacation(
        'Plan a 7-day trip to Paris, France for 2 people with $3000 budget'
    )
    assert result['status'] == 'success' or result['status'] == 'blocked'
    print('✓ Orchestrator workflow complete')

asyncio.run(test())
"

# 5. Run new test suite (if created)
pytest tests/test_agents.py -v
```

---

## Rollback Plan

### If Something Goes Wrong

#### Option 1: Git Revert (Recommended)
```bash
# If cleanup is committed
git log --oneline | head -5
# Find commit hash of cleanup

git revert <commit-hash>
git push origin feature/code-cleanup

# Files are restored
```

#### Option 2: Restore from Backup Branch
```bash
# If you created backup branch
git checkout backup/tools-cleanup-2025-11-20 -- src/tools/
git commit -m "Restore tools from backup"
```

#### Option 3: Manual Restoration
```bash
# Restore from git history
git checkout HEAD~1 -- src/tools/
git commit -m "Restore tools directory"
```

---

## Summary Checklist

### Immediate (HIGH Priority)
- [ ] Create backup branch
- [ ] Verify no dependencies on tools
- [ ] Delete 6 obsolete tool files
- [ ] Test application still works
- [ ] Commit with clear message
- [ ] Document in this file

### Short-Term (MEDIUM Priority)
- [ ] Install pytest-asyncio
- [ ] Create tests/test_agents.py
- [ ] Write async agent tests
- [ ] Archive old test_tools.py
- [ ] Run test suite
- [ ] Integrate in CI/CD (optional)

### Long-Term (LOW Priority)
- [ ] Test Amadeus flight integration thoroughly
- [ ] Add response caching
- [ ] Improve error messages
- [ ] Document API limitations
- [ ] Consider production API upgrade

---

## Effort Breakdown

| Task | Time | Complexity |
|------|------|-----------|
| Delete obsolete tools | 30 min | Low |
| Create async tests | 1 hour | Medium |
| Run full test suite | 15 min | Low |
| Flight integration improvements | 2 hours | Medium |
| **Total** | **~4 hours** | **Medium** |

---

## Success Metrics

After completion, you should have:

- [x] 881 fewer lines of code
- [x] 6 fewer files to maintain
- [x] Clear agent-only architecture
- [x] Async test suite with >80% coverage
- [x] Documented migration path
- [x] Rollback plan in place

---

## Questions & Troubleshooting

### Q: What if tests fail after deletion?
**A**: Restore from backup branch, investigate which component still references tools.

### Q: Can I keep tools for reference?
**A**: Yes, create a `docs/legacy/` directory and move them there instead of deleting.

### Q: What about test_tools.py?
**A**: Archive it (.old extension) and create new async agent tests.

### Q: Should I delete __pycache__?
**A**: Python will recreate it. Safe to delete, but not required.

### Q: How do I know cleanup is complete?
**A**: Run all post-cleanup tests. If application works, cleanup is successful.

---

## Next Steps

1. **Review this document**
2. **Execute immediate actions** (delete obsolete tools)
3. **Test thoroughly**
4. **Commit changes**
5. **Schedule short-term actions** (async tests)
6. **Plan long-term improvements** (Amadeus integration)

---

**End of Document**

**Status**: Ready for execution
**Approval**: Pending user review
**Estimated Completion**: 1-2 sessions
