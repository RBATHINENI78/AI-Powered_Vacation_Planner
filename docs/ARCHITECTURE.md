# AI-Powered Vacation Planner - System Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Multi-Agent Architecture](#multi-agent-architecture)
3. [Workflow Diagrams](#workflow-diagrams)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Integration Architecture](#integration-architecture)

---

## System Overview

```mermaid
graph TB
    User[User Interface] --> Orchestrator[Orchestrator Agent]

    Orchestrator --> SecurityGuard[Security Guardian Agent]
    SecurityGuard --> Orchestrator

    Orchestrator --> DestAgent[Destination Intelligence Agent]
    Orchestrator --> BookAgent[Booking Operations Agent]
    Orchestrator --> ExpAgent[Experience Curator Agent]
    Orchestrator --> FinAgent[Financial Advisor Agent]
    Orchestrator --> ImmAgent[Immigration Specialist Agent]

    DestAgent --> WeatherAPI[Weather APIs]
    BookAgent --> FlightAPI[Flight APIs]
    BookAgent --> HotelAPI[Hotel APIs]
    BookAgent --> CarAPI[Car Rental APIs]
    ExpAgent --> ActivityAPI[Activity APIs]
    ExpAgent --> TourAPI[Tour Operator APIs]
    FinAgent --> CurrencyAPI[Currency Exchange APIs]
    ImmAgent --> VisaDB[Visa Database]

    DestAgent --> Memory[(Session Memory)]
    BookAgent --> Memory
    ExpAgent --> Memory
    FinAgent --> Memory
    ImmAgent --> Memory

    Orchestrator --> Output[Generated Itinerary & Documents]

    style Orchestrator fill:#4285f4,color:#fff
    style SecurityGuard fill:#ea4335,color:#fff
    style Memory fill:#fbbc04,color:#000
    style Output fill:#34a853,color:#fff
```

---

## Multi-Agent Architecture

### Agent Hierarchy and Responsibilities

```mermaid
graph TD
    A[Orchestrator Agent] --> B[Security Guardian Agent]
    A --> C[Destination Intelligence Agent]
    A --> D[Booking Operations Agent]
    A --> E[Experience Curator Agent]
    A --> F[Financial Advisor Agent]
    A --> G[Immigration Specialist Agent]

    B --> B1[PII Detection]
    B --> B2[Data Redaction]
    B --> B3[Audit Logging]

    C --> C1[Weather Analysis]
    C --> C2[Climate Scoring]
    C --> C3[Seasonal Insights]

    D --> D1[Flight Search]
    D --> D2[Hotel Finder]
    D --> D3[Car Rental]

    E --> E1[Activity Discovery]
    E --> E2[Tour Recommendations]
    E --> E3[Cultural Insights]

    F --> F1[Currency Conversion]
    F --> F2[Budget Estimation]
    F --> F3[Cost Optimization]

    G --> G1[Visa Requirements]
    G --> G2[Documentation Guide]
    G --> G3[Application Process]

    style A fill:#4285f4,color:#fff
    style B fill:#ea4335,color:#fff
    style C fill:#34a853,color:#fff
    style D fill:#fbbc04,color:#000
    style E fill:#9c27b0,color:#fff
    style F fill:#ff6f00,color:#fff
    style G fill:#00acc1,color:#fff
```

### Agent Communication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant O as Orchestrator
    participant S as Security Guardian
    participant D as Destination Agent
    participant B as Booking Agent
    participant F as Financial Agent
    participant I as Immigration Agent
    participant M as Memory Store

    U->>O: Vacation Request (Dest, Dates, Origin)
    O->>S: Validate Input
    S->>S: Check for PII
    S-->>O: Validated Input

    O->>M: Store User Context

    par Parallel Agent Execution
        O->>D: Analyze Destination
        O->>I: Check Visa Requirements
        O->>F: Initialize Budget Framework
    end

    D->>D: Weather Analysis
    D-->>O: Weather Report

    I->>I: Visa Check
    I-->>O: Visa Requirements

    F->>F: Currency Rates
    F-->>O: Budget Framework

    O->>U: Present Initial Insights
    U->>O: Confirm Preferences

    O->>B: Search Flights & Hotels
    B-->>O: Booking Options

    O->>F: Calculate Total Cost
    F-->>O: Budget Estimate

    O->>U: Present Options (HITL)
    U->>O: Make Decisions

    O->>M: Update Session
    O->>U: Final Itinerary
```

---

## Workflow Diagrams

### End-to-End Vacation Planning Workflow

```mermaid
flowchart TD
    Start([User Starts Planning]) --> Input[Provide Destination, Dates, Origin, Citizenship]
    Input --> SecCheck{Security Check}

    SecCheck -->|PII Detected| Redact[Redact & Notify User]
    Redact --> SecCheck
    SecCheck -->|Clean| InitAgents[Initialize Specialized Agents]

    InitAgents --> ParallelPhase1{Parallel Analysis}

    ParallelPhase1 --> Weather[Weather Analysis]
    ParallelPhase1 --> Visa[Visa Requirements Check]
    ParallelPhase1 --> Budget[Budget Framework Setup]

    Weather --> AggResults1[Aggregate Phase 1 Results]
    Visa --> AggResults1
    Budget --> AggResults1

    AggResults1 --> HITL1{Human Decision Point 1}
    HITL1 -->|Adjust Dates?| DateMod[Modify Travel Dates]
    DateMod --> ParallelPhase2
    HITL1 -->|Proceed| ParallelPhase2{Parallel Booking Search}

    ParallelPhase2 --> Flights[Search Flights]
    ParallelPhase2 --> Hotels[Search Hotels]
    ParallelPhase2 --> Cars[Search Car Rentals]
    ParallelPhase2 --> Activities[Discover Activities]

    Flights --> AggResults2[Aggregate Phase 2 Results]
    Hotels --> AggResults2
    Cars --> AggResults2
    Activities --> AggResults2

    AggResults2 --> CalcCost[Calculate Total Budget]
    CalcCost --> HITL2{Human Decision Point 2}

    HITL2 -->|Adjust Options?| Optimize[Optimize Selections]
    Optimize --> CalcCost
    HITL2 -->|Approve| Generate[Generate Itinerary]

    Generate --> VisaGuide[Add Visa Application Guide]
    VisaGuide --> FinalDoc[Complete Travel Package]
    FinalDoc --> SaveMem[(Save to Memory)]
    SaveMem --> End([Deliver to User])

    style Start fill:#4285f4,color:#fff
    style SecCheck fill:#ea4335,color:#fff
    style HITL1 fill:#fbbc04,color:#000
    style HITL2 fill:#fbbc04,color:#000
    style End fill:#34a853,color:#fff
```

### Human-in-the-Loop Decision Points

```mermaid
flowchart LR
    A[Agent Analysis] --> B{Requires User Input?}

    B -->|Yes| C[Identify Decision Type]
    B -->|No| D[Continue Automated]

    C --> E{Decision Type}

    E -->|Date Adjustment| F[Present Weather/Event Data]
    E -->|Budget Constraint| G[Present Cost Options]
    E -->|Activity Selection| H[Present Interest-Based Options]
    E -->|Booking Choice| I[Present Comparison Matrix]

    F --> J[Ask User Decision]
    G --> J
    H --> J
    I --> J

    J --> K[Receive User Input]
    K --> L[Update Agent Context]
    L --> M[Continue Workflow]

    D --> M

    style B fill:#fbbc04,color:#000
    style E fill:#fbbc04,color:#000
    style J fill:#4285f4,color:#fff
    style L fill:#34a853,color:#fff
```

---

## Data Flow

### Information Flow Architecture

```mermaid
flowchart TB
    subgraph Input Layer
        UI[User Interface]
        API[External APIs]
    end

    subgraph Processing Layer
        SEC[Security Guardian]
        ORCH[Orchestrator]

        subgraph Agent Pool
            AG1[Destination Agent]
            AG2[Booking Agent]
            AG3[Experience Agent]
            AG4[Financial Agent]
            AG5[Immigration Agent]
        end
    end

    subgraph Data Layer
        STM[(Short-term Memory)]
        LTM[(Long-term Memory)]
        CACHE[(API Cache)]
        DOCS[(Document Store)]
    end

    subgraph Output Layer
        ITIN[Itinerary]
        BUDGET[Budget Report]
        VISA[Visa Guide]
    end

    UI --> SEC
    SEC --> ORCH
    ORCH --> AG1 & AG2 & AG3 & AG4 & AG5

    AG1 & AG2 & AG3 & AG4 & AG5 --> API
    API --> CACHE
    CACHE --> AG1 & AG2 & AG3 & AG4 & AG5

    AG1 & AG2 & AG3 & AG4 & AG5 --> STM
    STM --> LTM

    ORCH --> ITIN & BUDGET & VISA
    ITIN & BUDGET & VISA --> DOCS
    DOCS --> UI

    style SEC fill:#ea4335,color:#fff
    style ORCH fill:#4285f4,color:#fff
    style STM fill:#fbbc04,color:#000
    style LTM fill:#ff6f00,color:#fff
```

### Session Memory Management

```mermaid
stateDiagram-v2
    [*] --> SessionInit: User Starts

    SessionInit --> ActiveSession: Create Session ID

    ActiveSession --> ShortTermMem: Store Conversation
    ActiveSession --> WorkingMem: Store Agent States

    ShortTermMem --> WorkingMem: Context Passing
    WorkingMem --> ShortTermMem: Update Context

    ActiveSession --> DecisionPoint: User Interaction
    DecisionPoint --> WorkingMem: Store Decision

    WorkingMem --> LongTermMem: Persist Preferences

    ActiveSession --> SessionEnd: Planning Complete
    SessionEnd --> LongTermMem: Archive Session
    SessionEnd --> DocStore: Save Documents

    LongTermMem --> [*]: Session Closed
    DocStore --> [*]: Documents Delivered

    note right of LongTermMem
        Stores:
        - User preferences
        - Historical decisions
        - Travel patterns
    end note

    note right of ShortTermMem
        Stores:
        - Current conversation
        - Active context
        - Pending decisions
    end note
```

---

## Security Architecture

### PII Detection and Protection Pipeline

```mermaid
flowchart TD
    Input[User Input] --> PIICheck{PII Detection Engine}

    PIICheck --> RegexScan[Regex Pattern Matching]
    PIICheck --> MLScan[ML-based Detection]

    RegexScan --> Patterns{Check Patterns}
    Patterns -->|SSN| DetectSSN[Detect SSN Format]
    Patterns -->|Passport| DetectPass[Detect Passport Number]
    Patterns -->|Credit Card| DetectCC[Detect Card Number]
    Patterns -->|Email| DetectEmail[Detect Email]
    Patterns -->|Phone| DetectPhone[Detect Phone]

    MLScan --> ContextAnal[Contextual Analysis]

    DetectSSN --> Found{PII Found?}
    DetectPass --> Found
    DetectCC --> Found
    DetectEmail --> Found
    DetectPhone --> Found
    ContextAnal --> Found

    Found -->|Yes| Redact[Redact Sensitive Data]
    Found -->|No| Pass[Pass Through]

    Redact --> Log[Log Security Event]
    Log --> Notify[Notify User]
    Notify --> Clean[Return Cleaned Input]

    Pass --> Clean
    Clean --> NextAgent[Forward to Next Agent]

    style PIICheck fill:#ea4335,color:#fff
    style Found fill:#fbbc04,color:#000
    style Redact fill:#ff6f00,color:#fff
    style Clean fill:#34a853,color:#fff
```

### Security Guardrail Implementation

```mermaid
graph TB
    subgraph Input Validation
        A[Raw Input] --> B[Syntax Validation]
        B --> C[Length Check]
        C --> D[Encoding Validation]
    end

    subgraph PII Protection
        D --> E[Pattern Matching]
        E --> F[ML Classification]
        F --> G[Confidence Scoring]
    end

    subgraph Action Decision
        G --> H{Confidence > 0.8?}
        H -->|Yes| I[Auto Redact]
        H -->|No| J{Confidence > 0.5?}
        J -->|Yes| K[Ask User Confirmation]
        J -->|No| L[Pass Through]
        K --> M{User Confirms PII?}
        M -->|Yes| I
        M -->|No| L
    end

    subgraph Output
        I --> N[Redacted Text]
        L --> O[Original Text]
        N --> P[Security Log]
        O --> Q[Proceed]
        P --> Q
    end

    style E fill:#ea4335,color:#fff
    style I fill:#ff6f00,color:#fff
    style Q fill:#34a853,color:#fff
```

---

## Integration Architecture

### MCP and Tool Integration

```mermaid
graph LR
    subgraph Google ADK Core
        ADK[ADK Runtime]
        ORCH[Orchestrator Agent]
    end

    subgraph MCP Layer
        MCP1[Weather MCP Server]
        MCP2[Booking MCP Server]
        MCP3[Currency MCP Server]
        MCP4[Visa MCP Server]
    end

    subgraph Tools
        T1[Weather Forecast Tool]
        T2[Flight Search Tool]
        T3[Hotel Finder Tool]
        T4[Currency Converter Tool]
        T5[Visa Checker Tool]
        T6[PII Detector Tool]
    end

    subgraph External Services
        W[Weather API]
        F[Flight APIs]
        H[Hotel APIs]
        C[Currency API]
        V[Visa Database]
    end

    ORCH --> MCP1 & MCP2 & MCP3 & MCP4

    MCP1 --> T1
    MCP2 --> T2 & T3
    MCP3 --> T4
    MCP4 --> T5
    ADK --> T6

    T1 --> W
    T2 --> F
    T3 --> H
    T4 --> C
    T5 --> V

    style ADK fill:#4285f4,color:#fff
    style MCP1 fill:#34a853,color:#fff
    style MCP2 fill:#34a853,color:#fff
    style MCP3 fill:#34a853,color:#fff
    style MCP4 fill:#34a853,color:#fff
```

### Agent-to-Tool Communication Pattern

```mermaid
sequenceDiagram
    participant A as Agent
    participant O as Orchestrator
    participant M as MCP Server
    participant T as Tool
    participant E as External API
    participant C as Cache

    A->>O: Request Tool Execution
    O->>O: Validate Request
    O->>M: Route to MCP Server
    M->>M: Prepare Tool Call

    M->>C: Check Cache
    alt Cache Hit
        C-->>M: Return Cached Data
        M-->>O: Cached Result
    else Cache Miss
        M->>T: Execute Tool
        T->>E: API Request
        E-->>T: API Response
        T->>T: Process Response
        T-->>M: Tool Result
        M->>C: Update Cache
        M-->>O: Fresh Result
    end

    O->>O: Validate Result
    O-->>A: Return Result
    A->>A: Process & Act
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph Client Layer
        WEB[Web Interface]
        MOBILE[Mobile App]
        API_CLIENT[API Client]
    end

    subgraph API Gateway
        GATEWAY[Load Balancer]
        AUTH[Authentication]
    end

    subgraph Application Layer
        APP1[App Instance 1]
        APP2[App Instance 2]
        APP3[App Instance 3]
    end

    subgraph Agent Layer
        AGENT_POOL[Agent Pool Manager]
        ORCH_POOL[Orchestrator Pool]
        WORKER_POOL[Worker Agent Pool]
    end

    subgraph Service Layer
        MCP_SVC[MCP Services]
        CACHE_SVC[Cache Service]
        QUEUE_SVC[Message Queue]
    end

    subgraph Data Layer
        DB[(PostgreSQL)]
        REDIS[(Redis Cache)]
        S3[(Document Storage)]
    end

    WEB & MOBILE & API_CLIENT --> GATEWAY
    GATEWAY --> AUTH
    AUTH --> APP1 & APP2 & APP3

    APP1 & APP2 & APP3 --> AGENT_POOL
    AGENT_POOL --> ORCH_POOL
    ORCH_POOL --> WORKER_POOL

    WORKER_POOL --> MCP_SVC
    WORKER_POOL --> CACHE_SVC
    WORKER_POOL --> QUEUE_SVC

    MCP_SVC --> DB
    CACHE_SVC --> REDIS
    WORKER_POOL --> S3

    style GATEWAY fill:#4285f4,color:#fff
    style AGENT_POOL fill:#34a853,color:#fff
    style DB fill:#fbbc04,color:#000
```

---

## Technology Stack

```mermaid
mindmap
  root((AI Vacation Planner))
    Core Framework
      Google ADK
      Python 3.11+
      Model Context Protocol
    AI & ML
      LLM Integration
      NLP Processing
      PII Detection Models
    Agent Technologies
      Multi-Agent Orchestration
      Tool Integration
      Memory Management
    APIs & Services
      Weather APIs
      Flight Booking APIs
      Hotel Search APIs
      Currency Exchange
      Visa Databases
    Data Storage
      PostgreSQL
      Redis Cache
      S3 Document Store
    Security
      PII Filtering
      Encryption
      Audit Logging
    Frontend
      Web Interface
      Mobile Apps
      API Endpoints
```

---

## Performance Optimization

```mermaid
flowchart LR
    A[User Request] --> B{Cache Check}
    B -->|Hit| C[Return Cached]
    B -->|Miss| D[Agent Processing]

    D --> E{Parallel Execution}
    E --> F1[Agent 1]
    E --> F2[Agent 2]
    E --> F3[Agent 3]

    F1 --> G[Result Aggregation]
    F2 --> G
    F3 --> G

    G --> H[Update Cache]
    H --> I[Return Result]
    C --> I

    style B fill:#fbbc04,color:#000
    style E fill:#34a853,color:#fff
    style H fill:#4285f4,color:#fff
```

---

## Monitoring and Observability

```mermaid
graph TB
    subgraph Application
        A1[Agent 1]
        A2[Agent 2]
        A3[Agent 3]
    end

    subgraph Monitoring
        M1[Metrics Collector]
        M2[Log Aggregator]
        M3[Trace Collector]
    end

    subgraph Analysis
        D1[Dashboards]
        D2[Alerts]
        D3[Analytics]
    end

    A1 & A2 & A3 --> M1
    A1 & A2 & A3 --> M2
    A1 & A2 & A3 --> M3

    M1 --> D1
    M2 --> D2
    M3 --> D3

    D1 & D2 & D3 --> Report[Performance Reports]

    style M1 fill:#4285f4,color:#fff
    style D2 fill:#ea4335,color:#fff
    style Report fill:#34a853,color:#fff
```

---

## Conclusion

This architecture provides a robust, scalable, and secure foundation for the AI-Powered Vacation Planner. The multi-agent design ensures specialization and efficiency, while the comprehensive security measures protect user data. The integration architecture enables seamless connectivity with external services, and the human-in-the-loop design ensures user control and personalization throughout the planning process.
