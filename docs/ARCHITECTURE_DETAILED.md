# Detailed Architecture with Advanced ADK Features

## System Architecture Overview

```mermaid
flowchart TB
    User[User Request] --> Security[Security Guardian<br/>Custom PII Tool]

    Security --> Orchestrator[Main Orchestrator<br/>with Observability]

    Orchestrator --> Sequential[Sequential Research Phase]

    subgraph Sequential Agent
        Sequential --> Dest[Destination Agent<br/>Weather MCP]
        Dest -->|A2A Message| Imm[Immigration Agent<br/>Visa Check]
        Imm --> Fin[Financial Agent<br/>Currency MCP]
    end

    Fin --> Parallel[Parallel Booking Phase]

    subgraph Parallel Agent
        Parallel --> Flight[Flight Agent]
        Parallel --> Hotel[Hotel Agent]
        Parallel --> Car[Car Agent]
        Parallel --> Activity[Activity Agent]
    end

    Flight --> Loop[Loop Budget Optimizer]
    Hotel --> Loop
    Car --> Loop
    Activity --> Loop

    subgraph Loop Agent
        Loop --> Calculate[Function Tool<br/>Budget Calculator]
        Calculate --> Check{Within Budget?}
        Check -->|No| Optimize[Optimize Options]
        Optimize --> Calculate
        Check -->|Yes| HITL[Human Decision]
    end

    HITL --> Final[Final Itinerary Generator]

    subgraph Observability Layer
        Trace[Distributed Tracing]
        Metrics[Metrics Collection]
        Logs[Structured Logging]
    end

    Orchestrator -.->|Track| Trace
    Sequential -.->|Measure| Metrics
    Parallel -.->|Log| Logs
    Loop -.->|Monitor| Metrics

    style Security fill:#ea4335,color:#fff
    style Sequential fill:#4285f4,color:#fff
    style Parallel fill:#34a853,color:#fff
    style Loop fill:#fbbc04,color:#000
    style Observability Layer fill:#f5f5f5,color:#000
```

## Agent Execution Flow with Callbacks

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant CB as Callbacks
    participant SEQ as Sequential Agent
    participant PARN as Parallel Agent
    participant LOOP as Loop Agent
    participant OBS as Observability

    U->>O: Vacation Request

    O->>CB: before_agent_execute
    CB->>OBS: Log Start Event
    CB-->>O: proceed

    O->>SEQ: Execute Research Phase

    SEQ->>CB: before_agent_execute(destination)
    CB-->>SEQ: proceed
    SEQ->>SEQ: Weather Analysis (MCP)
    SEQ->>CB: after_agent_execute
    CB->>OBS: Log Metrics

    SEQ->>SEQ: A2A Message to Immigration
    SEQ->>SEQ: Visa Check
    SEQ->>SEQ: Financial Setup
    SEQ-->>O: Research Results

    O->>PARN: Execute Booking Phase

    par Parallel Execution
        PARN->>CB: before_tool_execute(flight_search)
        CB-->>PARN: proceed
        PARN->>PARN: Flight Search
        PARN->>CB: after_tool_execute

        PARN->>CB: before_tool_execute(hotel_search)
        CB-->>PARN: proceed
        PARN->>PARN: Hotel Search
        PARN->>CB: after_tool_execute

        PARN->>CB: before_tool_execute(car_search)
        CB-->>PARN: proceed
        PARN->>PARN: Car Search
        PARN->>CB: after_tool_execute
    end

    PARN-->>O: Booking Results

    O->>LOOP: Optimize Budget

    loop Until Budget Met or Max Iterations
        LOOP->>CB: before_tool_execute(budget_calc)
        CB-->>LOOP: proceed
        LOOP->>LOOP: Calculate Total
        LOOP->>CB: after_tool_execute

        alt Over Budget
            LOOP->>LOOP: Find Cheaper Options
        else Within Budget
            LOOP->>LOOP: Exit Loop
        end
    end

    LOOP-->>O: Optimized Options

    O->>CB: after_agent_execute
    CB->>OBS: Log Final Metrics
    O-->>U: Complete Itinerary
```

## Tool Types and Callbacks Flow

```mermaid
graph LR
    subgraph Function Tools
        FT1[Budget Calculator<br/>Direct Python]
        FT2[Date Calculator]
    end

    subgraph Custom Tools
        CT1[PII Detector<br/>Complex Logic]
        CT2[Data Validator]
    end

    subgraph Built-in Tools
        BT1[Web Search<br/>ADK Native]
        BT2[Code Executor<br/>ADK Native]
    end

    subgraph MCP Tools
        MT1[Weather MCP<br/>External Server]
        MT2[Currency MCP<br/>External Server]
    end

    Agent[Agent] --> ToolRouter{Tool Router}

    ToolRouter --> FT1
    ToolRouter --> CT1
    ToolRouter --> BT1
    ToolRouter --> MT1

    FT1 --> BeforeCallback[Before Callback]
    CT1 --> BeforeCallback
    BT1 --> BeforeCallback
    MT1 --> BeforeCallback

    BeforeCallback --> Execute[Execute Tool]
    Execute --> AfterCallback[After Callback]

    AfterCallback --> Enhance[Enhance Result]
    Enhance --> Agent

    style BeforeCallback fill:#fbbc04,color:#000
    style AfterCallback fill:#34a853,color:#fff
```

## Agent-to-Agent Communication Patterns

```mermaid
flowchart TB
    subgraph Destination Intelligence Agent
        D1[Analyze Weather]
        D2[Detect Severe Conditions]
        D3[Send A2A Advisory]
    end

    subgraph Immigration Agent
        I1[Register Message Handler]
        I2[Receive A2A Message]
        I3[Check Emergency Restrictions]
        I4[Send Acknowledgment]
    end

    subgraph Financial Agent
        F1[Request Currency Rates]
        F2[Send A2A to Currency MCP]
        F3[Receive Real-time Rates]
    end

    D1 --> D2
    D2 -->|Severe Weather| D3
    D3 -->|A2A Message| I2
    I2 --> I3
    I3 --> I4
    I4 -.->|Acknowledgment| D3

    F1 --> F2
    F2 -->|A2A Request| Currency[Currency MCP Server]
    Currency -->|A2A Response| F3

    style D3 fill:#4285f4,color:#fff
    style I2 fill:#34a853,color:#fff
    style F2 fill:#fbbc04,color:#000
```

## Observability Architecture

```mermaid
graph TB
    subgraph Application Layer
        Agent1[Agents]
        Tool1[Tools]
        MCP1[MCP Servers]
    end

    subgraph Observability SDK
        Trace[Tracing Provider]
        Metrics[Metrics Provider]
        Logs[Logging Provider]
    end

    subgraph Google Cloud
        CloudTrace[Cloud Trace]
        CloudMonitoring[Cloud Monitoring]
        CloudLogging[Cloud Logging]
    end

    subgraph Dashboards
        TraceUI[Trace Explorer]
        MetricsUI[Metrics Explorer]
        LogsUI[Logs Explorer]
    end

    Agent1 --> Trace
    Agent1 --> Metrics
    Agent1 --> Logs

    Tool1 --> Trace
    Tool1 --> Metrics
    Tool1 --> Logs

    MCP1 --> Trace
    MCP1 --> Metrics

    Trace --> CloudTrace
    Metrics --> CloudMonitoring
    Logs --> CloudLogging

    CloudTrace --> TraceUI
    CloudMonitoring --> MetricsUI
    CloudLogging --> LogsUI

    style Trace fill:#4285f4,color:#fff
    style Metrics fill:#34a853,color:#fff
    style Logs fill:#fbbc04,color:#000
```

## Complete Data Flow with All Features

```mermaid
flowchart TB
    Start([User Inputs Vacation Request]) --> PII[Custom Tool: PII Detector]

    PII -->|Before Callback| PIILog[Log PII Check Start]
    PIILog --> PIIExec[Execute Detection]
    PIIExec -->|After Callback| PIIResult[Enhanced Result]

    PIIResult --> Orch[Orchestrator Start]

    Orch -->|Start Span| TraceRoot[Root Trace Span]
    TraceRoot -->|Metric: request_count| MetricInc[Increment Counter]

    MetricInc --> SeqStart[Sequential Agent: Research]

    SeqStart -->|Span: research_phase| TraceSeq[Research Trace]
    TraceSeq --> WeatherAgent[Destination Agent]

    WeatherAgent -->|MCP Call| WeatherMCP[Weather MCP Server]
    WeatherMCP -->|Before Callback| WeatherLog[Log Weather Request]
    WeatherLog --> WeatherData[Fetch Weather Data]
    WeatherData -->|After Callback| WeatherMetric[Record Duration]

    WeatherMetric -->|Severe Weather?| A2ACheck{Check Conditions}
    A2ACheck -->|Yes| A2AMsg[Send A2A to Immigration]
    A2ACheck -->|No| ImmAgent[Immigration Agent]
    A2AMsg --> ImmAgent

    ImmAgent -->|Handle A2A| ImmProcess[Process Advisory]
    ImmProcess --> VisaCheck[Check Visa Requirements]
    VisaCheck --> FinAgent[Financial Agent]

    FinAgent -->|MCP Call| CurrencyMCP[Currency MCP Server]
    CurrencyMCP --> CurrencyData[Get Exchange Rates]
    CurrencyData --> SeqComplete[Sequential Complete]

    SeqComplete -->|Metric: seq_duration| RecordSeq[Record Duration]
    RecordSeq --> ParStart[Parallel Agent: Booking]

    ParStart -->|Span: booking_phase| TracePar[Booking Trace]

    TracePar --> ParExec{Parallel Execution}
    ParExec -->|Thread 1| Flight[Flight Search]
    ParExec -->|Thread 2| Hotel[Hotel Search]
    ParExec -->|Thread 3| Car[Car Search]
    ParExec -->|Thread 4| Activity[Activity Search]

    Flight -->|Callback| FlightMetric[Log Flight Duration]
    Hotel -->|Callback| HotelMetric[Log Hotel Duration]
    Car -->|Callback| CarMetric[Log Car Duration]
    Activity -->|Callback| ActivityMetric[Log Activity Duration]

    FlightMetric --> ParComplete[Gather Results]
    HotelMetric --> ParComplete
    CarMetric --> ParComplete
    ActivityMetric --> ParComplete

    ParComplete -->|Metric: parallel_speedup| RecordPar[Record Speedup]
    RecordPar --> LoopStart[Loop Agent: Budget Optimizer]

    LoopStart -->|Span: budget_loop| TraceLoop[Loop Trace]
    TraceLoop --> LoopIter{Iteration Start}

    LoopIter -->|Function Tool| BudgetCalc[Budget Calculator]
    BudgetCalc -->|Before Callback| CalcLog[Log Calculation]
    CalcLog --> CalcExec[Execute Calculation]
    CalcExec -->|After Callback| CalcResult[Enhanced Result]

    CalcResult --> BudgetCheck{Within Budget?}
    BudgetCheck -->|No| Optimize[Find Cheaper Options]
    Optimize -->|Metric: iteration_count| IterMetric[Record Iteration]
    IterMetric --> LoopIter

    BudgetCheck -->|Yes| HITL[Human Decision Point]
    HITL -->|Log: user_decision| DecisionLog[Log Decision]

    DecisionLog --> FinalGen[Generate Final Itinerary]
    FinalGen -->|Close Span| TraceEnd[End Root Span]

    TraceEnd -->|Metric: total_duration| FinalMetric[Record Total Time]
    FinalMetric -->|Log: completion| CompletionLog[Log Success]

    CompletionLog --> End([Return Complete Plan])

    style PII fill:#ea4335,color:#fff
    style SeqStart fill:#4285f4,color:#fff
    style ParStart fill:#34a853,color:#fff
    style LoopStart fill:#fbbc04,color:#000
    style A2AMsg fill:#9c27b0,color:#fff
```

## Callback Execution Timeline

```
Time →

Before Agent Execute (Orchestrator)
    ├─ Log Start
    ├─ Start Tracing Span
    └─ Initialize Metrics

Before Agent Execute (Sequential)
    ├─ Validate Input
    └─ Log Sequential Start

    Before Tool Execute (Weather MCP)
        ├─ Validate Args
        ├─ Start Timer
        └─ Log Tool Start

    Execute: Weather MCP

    After Tool Execute (Weather MCP)
        ├─ Record Duration
        ├─ Enhance Result
        ├─ Log Completion
        └─ Update Metrics

    A2A Communication (Destination → Immigration)
        ├─ Log Message Sent
        └─ Log Acknowledgment

After Agent Execute (Sequential)
    ├─ Record Duration
    └─ Log Sequential Complete

Before Agent Execute (Parallel)
    ├─ Log Parallel Start
    └─ Fork Execution Threads

    [Parallel Execution of 4 Agents]
    Each with Before/After Tool Callbacks

After Agent Execute (Parallel)
    ├─ Merge Results
    ├─ Record Speedup Metric
    └─ Log Parallel Complete

Before Agent Execute (Loop)
    ├─ Initialize Loop Counter
    └─ Log Loop Start

    [Loop Iterations]
    Each iteration with Before/After Callbacks

After Agent Execute (Loop)
    ├─ Record Iteration Count
    ├─ Record Final Budget
    └─ Log Loop Complete

After Agent Execute (Orchestrator)
    ├─ Close Tracing Span
    ├─ Finalize Metrics
    ├─ Log Success
    └─ Return Results
```

## Tool Response Enhancement Flow

```mermaid
flowchart LR
    Tool[Tool Executes] --> RawResult[Raw Result]

    RawResult --> AfterCallback[After Tool Callback]

    AfterCallback --> Validate{Valid Result?}
    Validate -->|No| Error[Error Handling]
    Validate -->|Yes| Enhance[Enhance Result]

    Enhance --> AddMeta[Add Metadata]
    AddMeta --> AddTrace[Add Trace ID]
    AddTrace --> AddTime[Add Timestamp]
    AddTime --> Format[Format Result]

    Format --> Cache[Update Cache]
    Cache --> Metric[Record Metrics]
    Metric --> Enhanced[Enhanced Result]

    Error --> Log[Log Error]
    Log --> Retry{Should Retry?}
    Retry -->|Yes| Tool
    Retry -->|No| ErrorResult[Error Result]

    Enhanced --> Agent[Return to Agent]
    ErrorResult --> Agent

    style AfterCallback fill:#34a853,color:#fff
    style Enhance fill:#4285f4,color:#fff
    style Error fill:#ea4335,color:#fff
```

## Performance Metrics Tracked

```yaml
Metrics Collected:

Counters:
  - vacation_requests_total (by destination, agent_type)
  - tool_calls_total (by tool_name, success)
  - agent_executions_total (by agent_name, phase)
  - a2a_messages_total (by from_agent, to_agent)
  - errors_total (by error_type, component)

Histograms:
  - agent_execution_duration_seconds (by agent_name)
  - tool_execution_duration_seconds (by tool_name)
  - loop_iterations_count (by optimization_type)
  - parallel_speedup_factor (by phase)

Gauges:
  - estimated_vacation_budget_usd (by currency)
  - active_sessions_count
  - cache_hit_rate_percentage
  - pii_detections_per_request

Traces:
  - End-to-end vacation planning span
  - Agent execution spans (nested)
  - Tool execution spans (nested)
  - A2A communication spans
  - Loop iteration spans
```

## Summary: Advanced Features Used

| Feature | Implementation | Location | Purpose |
|---------|----------------|----------|---------|
| **SequentialAgent** | Research Phase | Orchestrator → Agents | Order-dependent research |
| **ParallelAgent** | Booking Phase | Orchestrator → Booking | Concurrent searches |
| **LoopAgent** | Budget Optimizer | After Booking | Iterative refinement |
| **A2A Communication** | Destination ↔ Immigration | Between Agents | Advisory messages |
| **Function Tools** | Budget Calculator | Loop Agent | Simple calculations |
| **Custom Tools** | PII Detector | Security Phase | Complex business logic |
| **Built-in Tools** | Web Search | Research | ADK provided |
| **MCP Tools** | Weather, Currency | Multiple Agents | External services |
| **Before Callbacks** | All Tools & Agents | Everywhere | Pre-execution logic |
| **After Callbacks** | All Tools & Agents | Everywhere | Post-execution enhancement |
| **Distributed Tracing** | Google Cloud Trace | Observability | End-to-end tracking |
| **Metrics Collection** | Custom Metrics | Observability | Performance monitoring |
| **Structured Logging** | Cloud Logging | Observability | Debug & audit |

---

This architecture provides a production-ready, observable, and performant vacation planning system using all major Google ADK features.
