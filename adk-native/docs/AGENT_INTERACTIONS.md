# Agent Interaction Diagrams

**Purpose:** Detailed view of how agents communicate, share data, and coordinate work

---

## Table of Contents

1. [Agent Communication Patterns](#agent-communication-patterns)
2. [Phase 1: Research Interactions](#phase-1-research-interactions)
3. [Phase 2: Booking Interactions](#phase-2-booking-interactions)
4. [Phase 3 & 4: HITL Checkpoint Interactions](#phase-3--4-hitl-checkpoint-interactions)
5. [Phase 5: Organization Interactions](#phase-5-organization-interactions)
6. [Cross-Agent Data Dependencies](#cross-agent-data-dependencies)
7. [Context Sharing Patterns](#context-sharing-patterns)

---

## Agent Communication Patterns

### Agent-to-Agent Communication via Context

```mermaid
graph TB
    subgraph "Direct Communication (via InvocationContext)"
        A1[Agent 1<br/>Writes Data] -->|Shared Context| CTX[(Invocation<br/>Context)]
        CTX -->|Read Data| A2[Agent 2<br/>Reads Data]

        A2 -->|Writes More Data| CTX
        CTX -->|Read All Data| A3[Agent 3<br/>Reads Data]
    end

    subgraph "Example: Travel Advisory → Immigration"
        TA[Travel Advisory] -->|Write: travel_type='domestic'| CTX2[(Context)]
        CTX2 -->|Read: travel_type| IS[Immigration]

        IS -.Skip visa tools if domestic.-> IS
    end

    subgraph "Example: Destination → Suggestions"
        DI[Destination] -->|Write: weather_data| CTX3[(Context)]
        CTX3 -->|Read: weather_data| SC[Suggestions<br/>Checkpoint]

        SC -.Point 1: Weather summary.-> SC
    end

    style CTX fill:#ffff99
    style CTX2 fill:#ffff99
    style CTX3 fill:#ffff99
```

### No Direct Agent-to-Agent Messaging

```mermaid
graph LR
    A1[Agent 1] x--x A2[Agent 2]
    A1 -->|Write| Context[(Context)]
    Context -->|Read| A2

    note1[No A2A messaging<br/>All communication via<br/>shared context]

    style note1 fill:#ffcccc
    style Context fill:#ffff99
```

**Key Principle:** Agents don't send messages directly. All data sharing happens through **InvocationContext**.

---

## Phase 1: Research Interactions

### Sequential Flow with Context Building

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Orch as Orchestrator
    participant Context
    participant TA as Travel Advisory
    participant StateDept as State Dept API
    participant Tavily as Tavily API
    participant DI as Destination Intelligence
    participant Weather as Weather API
    participant IS as Immigration Specialist
    participant CE as Currency Exchange
    participant RestCountries
    participant ExchangeRate

    User->>Orch: Submit query:<br/>Salt Lake City, USA<br/>from Charlotte, USA
    Orch->>Context: Initialize context

    Note over Orch,TA: Agent 1: Travel Advisory

    Orch->>TA: Execute
    TA->>Context: Read user query
    TA->>TA: Parse origin & destination
    TA->>TA: Check if same country?<br/>(Charlotte, USA == Salt Lake City, USA)
    TA->>StateDept: Check advisories<br/>(for USA)
    StateDept-->>TA: No advisories (domestic)
    TA->>Tavily: Search global events<br/>(Salt Lake City safety)
    Tavily-->>TA: Current alerts
    TA->>Context: Write:<br/>- travel_type: "domestic"<br/>- origin: "Charlotte, USA"<br/>- destination: "Salt Lake City, USA"<br/>- can_proceed: true
    TA-->>Orch: Complete

    Note over Orch,DI: Agent 2: Destination Intelligence

    Orch->>DI: Execute
    DI->>Context: Read destination
    DI->>Context: Check for existing weather data
    Context-->>DI: No data found
    DI->>Weather: Get current weather<br/>(Salt Lake City)
    Weather-->>DI: Temp: 4°C, Clear
    DI->>Weather: Get forecast
    Weather-->>DI: Next 7 days
    DI->>DI: Analyze weather<br/>(Cold, <10°C → winter packing)
    DI->>Context: Write:<br/>- weather_data: {temp, conditions}<br/>- packing_list: [heavy coat, ...]<br/>- analysis: "Cold December"
    DI-->>Orch: Complete

    Note over Orch,IS: Agent 3: Immigration Specialist

    Orch->>IS: Execute
    IS->>Context: Read travel_type
    Context-->>IS: travel_type: "domestic"
    IS->>IS: Check: Is domestic?<br/>YES → Skip all visa tools!
    IS->>Context: Write:<br/>- visa_required: false<br/>- requirements: "Domestic travel -<br/>  ID only"
    IS-->>Orch: Complete (NO TOOL CALLS)

    Note over Orch,CE: Agent 4: Currency Exchange

    Orch->>CE: Execute
    CE->>Context: Read origin & destination
    CE->>RestCountries: Get currency (USA)
    RestCountries-->>CE: USD
    CE->>CE: Same country → No conversion
    CE->>ExchangeRate: Get exchange rate<br/>(USD → USD)
    ExchangeRate-->>CE: 1.0 (same currency)
    CE->>Context: Write:<br/>- currency: "USD"<br/>- rate: 1.0<br/>- no_conversion_needed: true
    CE-->>Orch: Complete

    Note over Orch: Research Phase Complete<br/>Context now has:<br/>- Travel type<br/>- Weather<br/>- Visa info<br/>- Currency
```

### Context State After Phase 1

```mermaid
graph TB
    subgraph "InvocationContext After Research Phase"
        Context[Context Object]

        Context --> UD[User Data]
        Context --> TA_Data[Travel Advisory Data]
        Context --> DI_Data[Destination Data]
        Context --> IS_Data[Immigration Data]
        Context --> CE_Data[Currency Data]

        UD --> UD1["query: 'Plan 2-week vacation...'"]
        UD --> UD2["budget: $2000"]
        UD --> UD3["travelers: 2"]

        TA_Data --> TA1["travel_type: 'domestic'"]
        TA_Data --> TA2["can_proceed: true"]
        TA_Data --> TA3["origin: 'Charlotte, USA'"]
        TA_Data --> TA4["destination: 'Salt Lake City, USA'"]

        DI_Data --> DI1["weather: {temp: 4°C, clear}"]
        DI_Data --> DI2["packing_list: [coat, gloves,...]"]
        DI_Data --> DI3["timestamp: 2025-11-22 01:30"]

        IS_Data --> IS1["visa_required: false"]
        IS_Data --> IS2["requirements: 'ID only'"]

        CE_Data --> CE1["currency: 'USD'"]
        CE_Data --> CE2["rate: 1.0"]
    end

    style Context fill:#ffff99
```

---

## Phase 2: Booking Interactions

### Parallel Execution with Context Reads

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Context
    box Parallel Agents (Fork)
    participant FB as Flight Booking
    participant HB as Hotel Booking
    participant CR as Car Rental
    end

    Note over Orch: Research Complete<br/>Start Booking Phase

    par Parallel Execution
        Orch->>FB: Execute (async)
        and
        Orch->>HB: Execute (async)
        and
        Orch->>CR: Execute (async)
    end

    Note over FB,CR: All 3 agents run SIMULTANEOUSLY

    FB->>Context: Read origin, destination, dates, travelers
    HB->>Context: Read destination, dates, travelers
    CR->>Context: Read destination, dates, travelers

    FB->>FB: Estimate flight cost<br/>(Charlotte ↔ SLC)<br/>LLM knowledge
    HB->>HB: Estimate hotel cost<br/>(SLC, 14 nights)<br/>LLM knowledge
    CR->>CR: Estimate car rental<br/>(SLC, 3 days)<br/>LLM knowledge

    par Write Results
        FB->>Context: Write:<br/>- flight_cost: $1000<br/>- airlines: [Southwest,...]
        and
        HB->>Context: Write:<br/>- hotel_cost: $560<br/>- recommendations: [...]
        and
        CR->>Context: Write:<br/>- car_cost: $230<br/>- rental_details: [...]
    end

    par All Complete
        FB-->>Orch: Complete
        and
        HB-->>Orch: Complete
        and
        CR-->>Orch: Complete
    end

    Note over Orch: Join Point<br/>All estimates ready
```

### Timing Diagram (Parallel vs Sequential)

```mermaid
gantt
    title Booking Phase: Parallel vs Sequential
    dateFormat X
    axisFormat %s

    section Parallel (ACTUAL)
    Flight Booking    :0, 10s
    Hotel Booking     :0, 10s
    Car Rental        :0, 10s
    Total Time        :crit, 0, 10s

    section Sequential (OLD)
    Flight Booking    :15, 25s
    Hotel Booking     :25, 35s
    Car Rental        :35, 45s
    Total Time        :crit, 15, 45s
```

**Speed-up:** 3x faster (30s → 10s)

---

## Phase 3 & 4: HITL Checkpoint Interactions

### Budget Checkpoint Decision Flow

```mermaid
stateDiagram-v2
    [*] --> BudgetAgent

    state BudgetAgent {
        [*] --> ReadContext
        ReadContext --> ExtractCosts
        ExtractCosts --> CalculateTotal

        state CalculateTotal {
            [*] --> flights: $1000
            flights --> hotels: $560
            hotels --> activities: $150 (est)
            activities --> food: $420 (est)
            food --> total: $2,130
        }

        total --> AssessFit

        state AssessFit <<choice>>
        AssessFit --> TooLow: $2,130 > $2,000 * 1.5?<br/>NO
        AssessFit --> Excess: $2,000 > $2,130 * 2.0?<br/>NO
        AssessFit --> Reasonable: Within ±50%?<br/>YES (budget=$2k, est=$2.1k)
    }

    Reasonable --> WriteContext: status: "proceed"

    WriteContext --> NextPhase: Continue to<br/>Suggestions Checkpoint

    TooLow --> StopWorkflow
    Excess --> StopWorkflow

    state StopWorkflow {
        [*] --> PresentOptions
        PresentOptions --> WaitUser: STOP execution
    }

    StopWorkflow --> UserDecision

    state UserDecision <<choice>>
    UserDecision --> Rerun: Option 3:<br/>Reduce scope
    UserDecision --> Continue: Option 1:<br/>Proceed anyway

    Rerun --> [*]: Re-enter at<br/>Booking Phase

    Continue --> NextPhase

    NextPhase --> [*]
```

### Suggestions Checkpoint Interaction

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Context
    participant SC as Suggestions Checkpoint
    participant User

    Note over Orch: Budget Checkpoint Passed<br/>Start Suggestions Checkpoint

    Orch->>SC: Execute
    SC->>Context: Read ALL previous agent data
    Context-->>SC: Travel Advisory data
    Context-->>SC: Destination data
    Context-->>SC: Immigration data
    Context-->>SC: Currency data
    Context-->>SC: Booking estimates
    Context-->>SC: Budget assessment

    SC->>SC: Synthesize 7-point overview

    Note over SC: Generate Overview
    SC->>SC: 1. Weather: "Cold December, 0-10°C"
    SC->>SC: 2. Visa: "No visa - domestic"
    SC->>SC: 3. Flights: "$1,000 for 2 adults"
    SC->>SC: 4. Hotels: "$560 for 14 nights"
    SC->>SC: 5. Activities: "Temple Square, skiing"
    SC->>SC: 6. Transport: "Public transit + 3-day car"
    SC->>SC: 7. Food: "$420, cook some meals"

    SC->>User: 📋 STOP - Show Overview<br/><br/>**Key Highlights:**<br/>1. Weather: Cold December...<br/>2. Visa: No visa...<br/>3-7. [other points]<br/><br/>✋ Please review and respond:<br/>- "Proceed"<br/>- "Change X"<br/>- "Questions"

    User->>SC: "Proceed"

    SC->>Context: Write:<br/>- user_approved: true<br/>- timestamp: 2025-11-22 01:45

    SC-->>Orch: Continue to Organization Phase
```

### Cross-Checkpoint Data Flow

```mermaid
graph TB
    subgraph "Budget Checkpoint Input"
        BC_In1[flight_cost: $1000]
        BC_In2[hotel_cost: $560]
        BC_In3[activities: $150]
        BC_In4[food: $420]
        BC_In5[user_budget: $2000]
    end

    subgraph "Budget Checkpoint Output"
        BC_Out1[total_estimated: $2,130]
        BC_Out2[status: 'proceed']
        BC_Out3[scenario: 'reasonable']
        BC_Out4[breakdown: {...}]
    end

    subgraph "Suggestions Checkpoint Input"
        SC_In1[ALL previous agent outputs]
        SC_In2[Budget assessment]
    end

    subgraph "Suggestions Checkpoint Output"
        SC_Out1[overview: 7-point summary]
        SC_Out2[user_approved: true/false]
        SC_Out3[user_feedback: '...']
    end

    BC_In1 --> BC_Calc[Calculate Total]
    BC_In2 --> BC_Calc
    BC_In3 --> BC_Calc
    BC_In4 --> BC_Calc
    BC_In5 --> BC_Calc

    BC_Calc --> BC_Out1
    BC_Calc --> BC_Out2
    BC_Calc --> BC_Out3
    BC_Calc --> BC_Out4

    BC_Out1 --> SC_In2
    BC_Out2 --> SC_In2
    SC_In1 --> SC_Synth[Synthesize Overview]
    SC_In2 --> SC_Synth

    SC_Synth --> SC_Out1
    SC_Synth --> SC_Out2
    SC_Synth --> SC_Out3

    style BC_Calc fill:#ffcc99
    style SC_Synth fill:#ffcc99
```

---

## Phase 5: Organization Interactions

### Activities → Itinerary → Documents

```mermaid
sequenceDiagram
    autonumber
    participant Orch as Orchestrator
    participant Context
    participant AA as Activities Agent
    participant IA as Itinerary Agent
    participant DG as Document Generator

    Note over Orch: User Approved Plan<br/>Start Organization Phase

    Orch->>AA: Execute
    AA->>Context: Read:<br/>- destination<br/>- interests<br/>- budget<br/>- weather<br/>- dates
    AA->>AA: Generate activity recommendations:<br/>- Temple Square (free)<br/>- Skiing/hiking<br/>- Capitol Building<br/>- Museums
    AA->>Context: Write:<br/>- activities: [list]<br/>- categorized_by_interest<br/>- estimated_costs
    AA-->>Orch: Complete

    Orch->>IA: Execute
    IA->>Context: Read:<br/>- activities<br/>- dates (14 nights)<br/>- weather<br/>- budget constraints
    IA->>IA: Generate daily itinerary:<br/>Day 1: Arrival + downtown<br/>Day 2: Temple Square<br/>Day 3-4: Skiing<br/>...
    IA->>IA: Optimize route:<br/>Minimize travel time
    IA->>IA: Add transportation details
    IA->>Context: Write:<br/>- daily_itinerary: [14 days]<br/>- optimized_routes<br/>- transportation_info
    IA-->>Orch: Complete

    Orch->>DG: Execute
    DG->>Context: Read ALL data:<br/>- Travel Advisory<br/>- Weather<br/>- Immigration<br/>- Budget<br/>- Activities<br/>- Itinerary
    DG->>DG: Generate documents:<br/>1. Trip Summary<br/>2. Pre-Departure Checklist<br/>3. Important Info Sheet<br/>4. Daily Itinerary<br/>5. Budget Tracker<br/>6. Contact List<br/>7. Packing List
    DG->>Context: Write:<br/>- documents: {all 7 docs}
    DG-->>Orch: Complete

    Note over Orch: Organization Phase Complete<br/>All documents ready
```

### Document Generation Data Sources

```mermaid
graph TB
    subgraph "Data Sources"
        TA_Data[Travel Advisory:<br/>- Origin<br/>- Destination<br/>- Advisories]
        DI_Data[Destination:<br/>- Weather<br/>- Packing list<br/>- Best time to visit]
        IS_Data[Immigration:<br/>- Visa requirements<br/>- Passport rules<br/>- Entry restrictions]
        CE_Data[Currency:<br/>- Exchange rate<br/>- Payment methods<br/>- Budget breakdown]
        Book_Data[Booking:<br/>- Flight estimates<br/>- Hotel estimates<br/>- Car rental details]
        Budget_Data[Budget:<br/>- Total costs<br/>- Breakdown<br/>- Sufficiency]
        Act_Data[Activities:<br/>- Recommendations<br/>- Costs<br/>- Categories]
        Itin_Data[Itinerary:<br/>- Daily schedule<br/>- Routes<br/>- Transportation]
    end

    subgraph "Generated Documents"
        Doc1[1. Trip Summary]
        Doc2[2. Pre-Departure<br/>Checklist]
        Doc3[3. Important Info<br/>Sheet]
        Doc4[4. Daily Itinerary]
        Doc5[5. Budget Tracker]
        Doc6[6. Contact List]
        Doc7[7. Packing List]
    end

    TA_Data --> Doc1
    DI_Data --> Doc1
    Book_Data --> Doc1

    IS_Data --> Doc2
    CE_Data --> Doc2
    DI_Data --> Doc2

    TA_Data --> Doc3
    IS_Data --> Doc3
    CE_Data --> Doc3

    Itin_Data --> Doc4
    Act_Data --> Doc4

    Budget_Data --> Doc5
    Book_Data --> Doc5

    TA_Data --> Doc6
    Book_Data --> Doc6

    DI_Data --> Doc7

    style Doc1 fill:#ccffcc
    style Doc2 fill:#ccffcc
    style Doc3 fill:#ccffcc
    style Doc4 fill:#ccffcc
    style Doc5 fill:#ccffcc
    style Doc6 fill:#ccffcc
    style Doc7 fill:#ccffcc
```

---

## Cross-Agent Data Dependencies

### Complete Dependency Graph

```mermaid
graph TD
    User[User Input] --> TA[Travel Advisory]
    User --> DI[Destination Intelligence]
    User --> IS[Immigration Specialist]
    User --> CE[Currency Exchange]

    TA -->|travel_type| IS
    TA -->|origin, destination| DI
    TA -->|origin, destination| CE

    DI -->|weather| AA[Activities Agent]
    DI -->|packing_list| DG[Document Generator]

    IS -->|visa_requirements| DG

    CE -->|currency, rates| Budget[Budget Checkpoint]

    User -->|budget| Budget

    TA -->|origin, destination| FB[Flight Booking]
    TA -->|origin, destination| HB[Hotel Booking]
    TA -->|destination| CR[Car Rental]

    DI -->|dates| FB
    DI -->|dates| HB
    DI -->|dates| CR

    FB -->|flight_cost| Budget
    HB -->|hotel_cost| Budget
    CR -->|car_cost| Budget

    Budget -->|budget_status| SC[Suggestions Checkpoint]

    TA -->|all_data| SC
    DI -->|all_data| SC
    IS -->|all_data| SC
    CE -->|all_data| SC
    FB -->|all_data| SC
    HB -->|all_data| SC
    CR -->|all_data| SC

    SC -->|user_approved| AA

    DI -->|interests| AA
    Budget -->|budget_constraints| AA

    AA -->|activities| IA[Itinerary Agent]
    DI -->|dates| IA
    Budget -->|constraints| IA

    IA -->|itinerary| DG
    AA -->|activities| DG
    Budget -->|breakdown| DG
    TA -->|travel_info| DG
    DI -->|weather| DG
    IS -->|visa| DG
    CE -->|currency| DG

    style TA fill:#99ccff
    style DI fill:#99ff99
    style IS fill:#99ff99
    style Budget fill:#ff9999
    style SC fill:#ff9999
```

---

## Context Sharing Patterns

### Pattern 1: Direct Pass-Through

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant CTX as Context
    participant A2 as Agent 2

    A1->>CTX: Write: key='value'
    A2->>CTX: Read: key
    CTX-->>A2: 'value'

    Note over A1,A2: Simple data pass-through<br/>No transformation
```

**Example:** Travel Advisory writes `travel_type: 'domestic'`, Immigration reads it directly.

### Pattern 2: Aggregation

```mermaid
sequenceDiagram
    participant A1 as Agent 1
    participant A2 as Agent 2
    participant A3 as Agent 3
    participant CTX as Context
    participant A4 as Agent 4 (Aggregator)

    A1->>CTX: Write: data1
    A2->>CTX: Write: data2
    A3->>CTX: Write: data3

    A4->>CTX: Read: data1, data2, data3
    CTX-->>A4: [all data]
    A4->>A4: Combine and synthesize
    A4->>CTX: Write: aggregated_result

    Note over A1,A4: Multiple inputs combined<br/>into single output
```

**Example:** Suggestions Checkpoint reads ALL previous agent outputs and creates 7-point overview.

### Pattern 3: Conditional Execution

```mermaid
flowchart TD
    A1[Agent 1] -->|Write: flag| CTX[(Context)]
    CTX -->|Read: flag| A2[Agent 2]

    A2 --> Check{Check flag<br/>value?}
    Check -->|true| Execute[Execute normal flow]
    Check -->|false| Skip[Skip certain tools]

    Execute --> Result1[Full execution]
    Skip --> Result2[Optimized execution]

    Note over A1,A2: Agent behavior changes<br/>based on context
```

**Example:** Immigration checks `travel_type`. If `'domestic'`, skip all visa tools.

### Pattern 4: Context Reuse (Optimization)

```mermaid
sequenceDiagram
    participant A1 as Destination (1st run)
    participant CTX as Context
    participant A2 as Destination (2nd run)

    Note over A1: User reduces trip duration

    A1->>CTX: Write: weather_data<br/>(timestamp: 01:30)
    A1->>CTX: Call weather API

    Note over A1,A2: User selects "Reduce scope"<br/>Workflow re-runs

    A2->>CTX: Check for weather_data
    CTX-->>A2: weather_data exists<br/>(timestamp: 01:30)
    A2->>A2: Check: Is fresh?<br/>(< 15 min old)<br/>YES
    A2->>A2: REUSE data<br/>Skip API call

    Note over A2: Optimization:<br/>No redundant API call
```

**Example:** Weather data reused when budget reduction triggers workflow re-run.

---

## Error Propagation

### How Errors Flow Between Agents

```mermaid
graph TD
    A1[Travel Advisory] -->|Error: Travel Blocked| Stop[STOP Workflow]
    A1 -->|Success| A2[Destination]

    A2 -->|Error: Weather API failed| Fallback1[Use LLM Estimate]
    Fallback1 --> A3[Immigration]

    A3 -->|Success| A4[Currency]

    A4 -->|Error: Exchange API failed| Fallback2[Use Hardcoded Rates]
    Fallback2 --> Continue[Continue Workflow]

    A5[Budget HITL] -->|Error: Budget too low| UserInput[Request User Decision]
    UserInput -->|User: Proceed anyway| Continue2[Continue]
    UserInput -->|User: Stop| Stop2[STOP Workflow]

    Continue --> A6[Suggestions HITL]
    Continue2 --> A6

    A6 -->|User: Approve| A7[Organization]
    A6 -->|User: Change| Rerun[Re-run Workflow]

    style Stop fill:#ff9999
    style Stop2 fill:#ff9999
    style Fallback1 fill:#ffcc99
    style Fallback2 fill:#ffcc99
```

---

## Summary

### Key Interaction Patterns

1. **Sequential Communication:** Agents execute in order, building context
2. **Parallel Communication:** Multiple agents read context simultaneously
3. **Context Sharing:** All data passed via InvocationContext (no direct messaging)
4. **Conditional Logic:** Agents adapt behavior based on context flags
5. **Context Reuse:** Agents check for existing data before calling tools
6. **Aggregation:** Later agents synthesize outputs from multiple earlier agents
7. **HITL Interruption:** Checkpoints can STOP workflow and request user input

### Performance Benefits

- **Parallel Booking:** 3x speedup
- **Context Reuse:** 60% fewer redundant calls
- **Domestic Optimization:** 100% reduction in unnecessary visa checks
- **HITL Checkpoints:** Prevent wasted work on unwanted plans

---

**Next:** Review [System Design](./SYSTEM_DESIGN.md) for implementation details

**Document Version:** 1.0
**Last Updated:** 2025-11-22
