# ADK Features Implemented - Comprehensive Inventory

**Project**: AI-Powered Vacation Planner
**Framework**: Google Agent Development Kit (ADK)
**Last Updated**: 2025-11-20

---

## Table of Contents
1. [Agent Architecture](#agent-architecture)
2. [Workflow Patterns](#workflow-patterns)
3. [Function Tools](#function-tools)
4. [MCP Servers](#mcp-servers)
5. [Agent-to-Agent Communication](#agent-to-agent-communication)
6. [Observability](#observability)
7. [External API Integrations](#external-api-integrations)

---

## Agent Architecture

### 11 Specialized Agents Implemented

#### 1. BaseAgent (Foundation)
**File**: `src/agents/base_agent.py`

Core functionality for all agents:
- A2A (Agent-to-Agent) communication with message registry
- Before/After execution callbacks
- Observability (tracing, metrics, logging)
- Message handlers registration

```python
class BaseAgent(ABC):
    # Class-level message registry for A2A communication
    _message_registry: Dict[str, List[AgentMessage]] = {}
    _message_handlers: Dict[str, Dict[str, Callable]] = {}
```

**Key Features**:
- `send_message()`: Send messages to other agents with priority
- `receive_messages()`: Receive filtered messages
- `process_messages()`: Process pending messages with handlers
- `execute()`: Main execution with full callback support

---

#### 2. OrchestratorAgent (Main Coordinator)
**File**: `src/agents/orchestrator.py`

Master orchestrator for 4-phase vacation planning workflow:
1. Security Phase - PII detection
2. Research Phase - Sequential execution
3. Booking Phase - Parallel execution
4. Optimization Phase - Loop execution

```python
class OrchestratorAgent(BaseAgent):
    def __init__(self):
        self.security_agent = SecurityGuardianAgent()
        self.research_agent = SequentialResearchAgent()
        self.booking_agent = ParallelBookingAgent()
        self.optimizer_agent = LoopBudgetOptimizer()
```

**Capabilities**:
- Natural language request parsing
- Phase coordination with rollback on critical errors
- Final plan compilation with itinerary generation
- A2A message handling for security alerts and budget updates

---

#### 3. SecurityGuardianAgent (PII Detection)
**File**: `src/agents/security_guardian.py`

Protects user data with 8 PII detection patterns:
- SSN, Credit Card (critical severity)
- Passport, Driver's License, Bank Account (high severity)
- Email, Phone, Date of Birth (medium severity)

```python
self.pii_patterns = {
    "ssn": {
        "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
        "severity": "critical",
        "description": "Social Security Number"
    },
    # ... 7 more patterns
}
```

**A2A Communication**:
Sends critical alerts to Orchestrator when high-risk PII detected.

---

#### 4. DestinationIntelligenceAgent (Weather & Analysis)
**File**: `src/agents/destination_intelligence.py`

Real-time weather analysis using OpenWeather API:
- Current weather conditions
- 5-day forecast with daily summaries
- Travel condition analysis
- Dynamic packing list generation

**MCP Pattern Integration**:
Uses external API with fallback handling.

**A2A Communication**:
Sends weather advisories to Immigration Specialist for severe weather.

---

#### 5. ImmigrationSpecialistAgent
**File**: `src/agents/immigration_specialist.py`

Visa requirements and travel document analysis:
- Visa requirement checking via RestCountries API
- Duration-based visa type determination
- Required documents list generation
- Travel warnings

---

#### 6. FinancialAdvisorAgent
**File**: `src/agents/financial_advisor.py`

Currency exchange and budgeting:
- Real-time exchange rates via ExchangeRate API
- Budget breakdown (flights, hotels, activities, food, transport)
- Travel style-based recommendations
- Saving tips generation

**A2A Communication**:
Sends budget updates to Orchestrator.

---

#### 7-8. FlightBookingAgent & HotelBookingAgent
**File**: `src/agents/booking_agents.py`

**FlightBookingAgent**:
- Amadeus API integration (MCP server)
- Flight search with fallback to LLM
- Price comparison and recommendations

**HotelBookingAgent**:
- Amadeus Hotels API via MCP server
- Hotel categorization (budget, mid-range, luxury)
- Real booking links generation

---

#### 9. CarRentalAgent
**File**: `src/agents/booking_agents.py`

Vehicle rental recommendations:
- Car type suggestions based on group size
- Cost estimation
- Optional service (can be removed by optimizer)

---

#### 10. ExperienceCuratorAgent
**File**: `src/agents/experience_curator.py`

Activity and attraction curation:
- Interest-based filtering (museums, food, entertainment)
- Day-by-day itinerary generation
- Budget-aware activity planning
- Local tips and booking information

**Activity Database**: 3 cities (Paris, Tokyo, London) with 50+ activities

---

#### 11. DocumentGeneratorAgent
**File**: `src/agents/document_generator.py`

Final trip document compilation:
- Markdown-formatted trip plans
- Section organization (overview, weather, bookings, budget)
- Integration of all agent results

---

## Workflow Patterns

### 1. Sequential Pattern

**Implementation**: `SequentialResearchAgent`
**File**: `src/agents/sequential_agent.py`

Order-dependent research phase execution:

```python
self.execution_order = [
    ("destination", self.destination_agent),
    ("immigration", self.immigration_agent),
    ("financial", self.financial_agent)
]
```

**Data Flow**:
```
Destination → Weather Data
    ↓
Immigration → Uses weather warnings for advisories
    ↓
Financial → Uses visa requirements for budget
```

**Error Handling**:
- Critical step failure (destination) = abort
- Non-critical failure = continue with warnings

**Example**:
```python
# Each step accumulates data for next step
accumulated_data = input_data.copy()
for step_name, agent in self.execution_order:
    result = await agent.execute(agent_input)
    accumulated_data = self._accumulate_data(accumulated_data, step_name, result)
```

---

### 2. Parallel Pattern

**Implementation**: `ParallelBookingAgent`
**File**: `src/agents/parallel_agent.py`

Concurrent execution for independent tasks:

```python
self.parallel_tasks = [
    ("flights", self.flight_agent),
    ("hotels", self.hotel_agent),
    ("car_rental", self.car_agent),
    ("activities", self.experience_agent)
]
```

**Performance Gain**: 3-4x speedup

```python
# Create async tasks
tasks = [asyncio.create_task(agent.execute(input))
         for _, agent in self.parallel_tasks]

# Execute all concurrently
results_list = await asyncio.gather(*tasks, return_exceptions=True)

# Calculate speedup
speedup = total_sequential_time / actual_parallel_time
# Typical: 4000ms / 1200ms = 3.33x speedup
```

**Metrics Tracked**:
- Total sequential time (sum of all tasks)
- Actual parallel time (max of all tasks)
- Speedup factor
- Success/failure counts

---

### 3. Loop Pattern

**Implementation**: `LoopBudgetOptimizer`
**File**: `src/agents/loop_agent.py`

Iterative refinement with Human-in-the-Loop (HITL):

```python
self.optimization_strategies = [
    ("downgrade_hotel", self._downgrade_hotel, 0.15),      # 15% savings
    ("cheaper_flights", self._find_cheaper_flights, 0.20), # 20% savings
    ("reduce_activities", self._reduce_activities, 0.10),  # 10% savings
    ("shorter_stay", self._reduce_duration, 0.25),         # 25% savings
    ("remove_car", self._remove_car_rental, 0.05)          # 5% savings
]
```

**HITL Decision Points**:
```python
async def _request_human_approval(
    self,
    strategy: str,
    description: str,
    savings: float,
    new_cost: float
) -> Dict[str, Any]:
    logger.info(f"[HITL] Requesting approval for: {strategy}")
    logger.info(f"[HITL] Potential savings: ${savings:.2f}")
    # In production, waits for user input
    return {"approved": True}
```

**Loop Execution**:
```python
iteration = 0
while current_cost > target_budget and iteration < max_iterations:
    iteration += 1
    best_strategy = self._select_strategy(current_cost, target_budget, bookings)
    optimized, savings, description = strategy_func(current_bookings)

    if not auto_approve:
        decision = await self._request_human_approval(...)
        if not decision.get("approved"):
            continue

    current_bookings = optimized
    current_cost -= savings
```

**Exit Conditions**:
- Budget met: `current_cost <= target_budget`
- Max iterations: `iteration >= max_iterations`
- No more strategies: `viable_strategies == []`

---

## Function Tools

### 7 FunctionTools with @with_callbacks

**File**: `agents/vacation_planner/agent.py`

All tools wrapped with callback decorator for observability:

#### 1. get_weather_info
```python
@with_callbacks
async def get_weather_info(city: str, country: str = "") -> dict:
    """Get weather information for a destination."""
    result = await destination_intelligence.execute({
        "city": city,
        "country": country
    })
    return result
```

#### 2. check_visa_requirements
```python
@with_callbacks
async def check_visa_requirements(
    citizenship: str,
    destination: str,
    duration_days: int = 30,
    origin: str = ""
) -> dict:
    """Check visa requirements with domestic travel detection."""
    # Detects domestic travel
    if origin_country == dest_country:
        return {"travel_type": "domestic", "visa_required": False}

    # International travel
    result = await immigration_specialist.execute({
        "citizenship": citizenship,
        "destination": destination,
        "duration_days": duration_days
    })
    return result
```

#### 3. get_currency_exchange
```python
@with_callbacks
async def get_currency_exchange(
    origin: str,
    destination: str,
    amount: float = 1.0,
    travelers: int = 2,
    nights: int = 7
) -> dict:
    """Get currency exchange AND budget breakdown."""
    # Skips for domestic travel
    if origin_country == dest_country:
        return {"travel_type": "domestic", "currency_exchange_needed": False}

    result = await financial_advisor.execute({...})
    return {
        "currency_info": result["currency_info"],
        "budget_breakdown": result["budget_breakdown"],
        "saving_tips": result["saving_tips"]
    }
```

#### 4. search_flights
```python
@with_callbacks
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    travelers: int = 1
) -> dict:
    """Search for flights using Flight Booking agent."""
    result = await flight_booking.execute({...})
    return result.get("flight_info", {})
```

#### 5. search_hotels
```python
@with_callbacks
async def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1
) -> dict:
    """Search for hotels using Hotel Booking agent."""
    result = await hotel_booking.execute({...})
    # Returns Amadeus API results or LLM fallback
    return result
```

#### 6. generate_detailed_itinerary
```python
@with_callbacks
async def generate_detailed_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: str,
    travelers: int = 2
) -> dict:
    """Generate detailed day-by-day itinerary."""
    return {
        "destination": destination,
        "days": days,
        "interests": interests,
        "instruction": f"Generate a detailed {days}-day itinerary"
    }
```

#### 7. generate_trip_document
```python
@with_callbacks
async def generate_trip_document(
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int,
    origin: str = "",
    interests: str = "",
    budget: float = 0.0
) -> dict:
    """Generate complete trip planning document."""
    result = await document_generator.execute({...})
    return result.get("document", {})
```

---

## MCP Servers

### 3 MCP Server Implementations

**Directory**: `src/mcp_servers/`

#### 1. amadeus_client.py
```python
class AmadeusClient:
    """Base client for Amadeus API authentication and requests."""

    async def get_access_token(self) -> str:
        """OAuth 2.0 token acquisition"""

    async def get_city_code(self, city_name: str) -> Dict:
        """City/airport code lookup"""

    async def search_hotels(self, city_code: str, ...) -> Dict:
        """Hotel search API"""

    async def search_flights(self, origin: str, destination: str, ...) -> Dict:
        """Flight search API"""
```

#### 2. amadeus_hotels.py
```python
async def search_hotels_amadeus(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1
) -> Dict[str, Any]:
    """
    Real-time hotel search with:
    - City code lookup
    - Hotel search
    - Categorization (budget, mid-range, luxury)
    - Booking URL generation
    """
```

**Response Structure**:
```json
{
  "destination": "Paris",
  "hotels": {
    "budget": [...],
    "mid_range": [...],
    "luxury": [...]
  },
  "source": "amadeus_api"
}
```

#### 3. amadeus_flights.py
```python
async def search_flights_amadeus(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
    travelers: int = 1,
    cabin_class: str = "economy"
) -> Dict[str, Any]:
    """
    Flight search with:
    - Multi-city support
    - Return/one-way flights
    - Price comparison
    """
```

---

## Agent-to-Agent Communication

### A2A Message Examples

#### Security Alert (SecurityGuardian → Orchestrator)
```python
# In SecurityGuardianAgent
if risk_level == "critical":
    self.send_message(
        to_agent="orchestrator",
        message_type="security_alert",
        content={
            "alert_type": "critical_pii_detected",
            "findings_count": len(findings),
            "risk_level": risk_level
        },
        priority="critical"
    )
```

#### Weather Advisory (DestinationIntelligence → Immigration)
```python
# In DestinationIntelligenceAgent
if analysis.get("severe_weather"):
    self.send_message(
        to_agent="immigration_specialist",
        message_type="weather_advisory",
        content={
            "destination": f"{city}, {country}",
            "advisory_type": "severe_weather",
            "conditions": analysis.get("warnings", []),
            "recommendation": "Check for travel restrictions"
        },
        priority="high"
    )
```

#### Message Handler Registration
```python
# In OrchestratorAgent.__init__
self.register_message_handler("security_alert", self._handle_security_alert)
self.register_message_handler("budget_update", self._handle_budget_update)

def _handle_security_alert(self, message) -> Dict[str, Any]:
    logger.warning(f"[ORCHESTRATOR] Security alert: {message.content}")
    return {"status": "acknowledged", "action": "reviewing"}
```

### Message Structure
```python
class AgentMessage:
    def __init__(self, from_agent, to_agent, message_type, content, priority):
        self.id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.priority = priority  # low, normal, high, critical
        self.timestamp = datetime.utcnow().isoformat()
        self.acknowledged = False
```

---

## Observability

### 1. Tracing

**Implementation**: `src/callbacks/tool_callbacks.py`

```python
class ToolCallbackManager:
    def before_tool_execute(self, tool_name: str, tool_args: Dict) -> Dict:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "before_tool_execute",
            "tool": tool_name,
            "args": tool_args
        }
        self.event_log.append(event)
        logger.info(f"[BEFORE] Tool: {tool_name}")
        return {"proceed": True, "request_id": f"{tool_name}_{int(time.time())}"}

    def after_tool_execute(self, tool_name: str, tool_result: Any, error: Exception = None):
        execution_time = time.time() - start_time
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "after_tool_execute",
            "tool": tool_name,
            "execution_time_ms": round(execution_time * 1000, 2),
            "success": error is None
        }
        self.event_log.append(event)
```

### 2. Metrics

**Agent Metrics** (per agent):
```python
self.metrics = {
    "executions": 0,
    "total_time": 0,
    "errors": 0,
    "messages_sent": 0,
    "messages_received": 0
}

def get_metrics(self) -> Dict[str, Any]:
    return {
        "agent": self.name,
        "metrics": self.metrics,
        "avg_execution_time": self.metrics["total_time"] / self.metrics["executions"]
    }
```

**Tool Metrics** (per tool):
```python
self.metrics[tool_name] = {
    "start_time": time.time(),
    "call_count": self.metrics.get(tool_name, {}).get("call_count", 0) + 1,
    "last_execution_time": execution_time,
    "last_success": error is None
}
```

### 3. Logging

**Structured Logging with Loguru**:
```python
logger.info(f"[ORCHESTRATOR] Starting vacation planning session: {session_id}")
logger.info(f"[SEQUENTIAL] Executing step: {step_name}")
logger.info(f"[PARALLEL] Completed booking phase. Speedup: {speedup:.2f}x")
logger.warning(f"[ALERT] Slow tool: {tool_name} took {execution_time:.2f}s")
logger.error(f"[EXECUTE] {self.name} failed: {e}")
```

**Execution Metadata**:
```python
result["_metadata"] = {
    "agent": self.name,
    "execution_time_ms": round(execution_time * 1000, 2),
    "timestamp": datetime.utcnow().isoformat(),
    "messages_processed": len(message_results)
}
```

---

## External API Integrations

### 1. OpenWeather API
**Agent**: DestinationIntelligenceAgent
**Endpoints**:
- `/weather` - Current weather
- `/forecast` - 5-day forecast

**Usage**:
```python
async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{self.base_url}/weather",
        params={
            "q": f"{city},{country}",
            "appid": self.api_key,
            "units": "metric"
        }
    )
```

### 2. ExchangeRate API
**Agent**: FinancialAdvisorAgent
**Endpoint**: `/latest`

**Usage**:
```python
url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    data = response.json()
    rate = data["rates"].get(to_currency, 1.0)
```

### 3. RestCountries API
**Agent**: ImmigrationSpecialistAgent
**Endpoint**: `/name/{country}`

**Usage**:
```python
url = f"https://restcountries.com/v3.1/name/{destination_country}"
async with httpx.AsyncClient() as client:
    response = await client.get(url)
    country_data = response.json()[0]
```

### 4. Amadeus Travel API
**Agents**: FlightBookingAgent, HotelBookingAgent
**Endpoints**:
- `/v1/security/oauth2/token` - Authentication
- `/v1/reference-data/locations/cities` - City lookup
- `/v3/shopping/hotel-offers` - Hotel search
- `/v2/shopping/flight-offers` - Flight search

**Authentication**:
```python
async def get_access_token(self) -> str:
    response = await client.post(
        f"{self.base_url}/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
    )
    return response.json()["access_token"]
```

---

## Summary Statistics

| Category | Count | Details |
|----------|-------|---------|
| **Agents** | 11 | Base, Orchestrator, Security, Destination, Immigration, Financial, Flight, Hotel, CarRental, Experience, Document |
| **Workflow Patterns** | 3 | Sequential, Parallel, Loop |
| **FunctionTools** | 7 | All with @with_callbacks decorator |
| **MCP Servers** | 3 | amadeus_client, amadeus_hotels, amadeus_flights |
| **External APIs** | 4 | OpenWeather, ExchangeRate, RestCountries, Amadeus |
| **A2A Message Types** | 3 | security_alert, weather_advisory, budget_update |
| **Observability Features** | 3 | Tracing (event log), Metrics (per agent/tool), Logging (structured) |
| **Total Code Lines** | ~3500+ | Across all agents and supporting code |

---

## Key ADK Patterns Demonstrated

1. **Multi-Agent Orchestration**: Orchestrator coordinates 4 phases with specialized agents
2. **Workflow Patterns**: Sequential (research), Parallel (booking), Loop (optimization)
3. **A2A Communication**: Inter-agent messaging with priority and handlers
4. **Callbacks & Observability**: Before/after hooks, metrics, structured logging
5. **MCP Integration**: External API abstraction (Amadeus, OpenWeather)
6. **HITL Decision Points**: Budget optimization with human approval
7. **Error Handling**: Graceful degradation, fallback strategies
8. **Real-time Data**: Live API integration with caching and fallbacks

---

**End of Document**
