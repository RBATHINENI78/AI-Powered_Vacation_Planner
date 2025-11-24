# AI-Powered Vacation Planner (Google ADK)

**Enterprise-grade AI vacation planning system built with Google's Agent Development Kit (ADK)**

[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://google.github.io/adk-docs/)
[![Gemini Models](https://img.shields.io/badge/Gemini-2.5%20Flash%20Lite-EA4335)](https://ai.google.dev/)
[![Vertex AI Ready](https://img.shields.io/badge/Vertex%20AI-Ready-34A853)](https://cloud.google.com/vertex-ai)

## Overview

A production-ready multi-agent vacation planning system that coordinates **12 specialized AI agents** to create comprehensive travel plans. Built entirely with Google ADK's native patterns for optimal performance and maintainability.

### Key Features

✅ **12 Specialized Agents** - Travel advisory, destination intelligence, immigration, currency, flight/hotel/car rental booking, activities, itinerary, document generation, plus 2 HITL checkpoints
✅ **Dual HITL Checkpoints** - Budget assessment and suggestions approval require human input
✅ **Parallel Execution** - 3x speedup for booking phase using ParallelAgent
✅ **Date Inference** - Natural language dates ("December 2025, 1 month") automatically converted
✅ **Context-Aware** - Agents access previous outputs to reduce redundant API calls
✅ **Vertex AI Support** - Production deployment with enterprise-grade quotas and SLA
✅ **Real-Time APIs** - Amadeus integration for flights and hotels
✅ **Clean Output** - Organized vacation plans, not raw agent data

## Architecture

```
User Request
    ↓
ADK Web UI / CLI
    ↓
Main Orchestrator (vacation_planner - SequentialAgent)
    ↓
├─ Phase 1: Research (SequentialAgent)
│  ├─ Travel Advisory Agent
│  ├─ Destination Intelligence Agent
│  ├─ Immigration Specialist Agent
│  └─ Currency Exchange Agent
│
├─ Phase 2: Booking (ParallelAgent - 3x faster)
│  ├─ Flight Booking Agent
│  ├─ Hotel Booking Agent
│  └─ Car Rental Agent
│
├─ Phase 3: Budget Checkpoint 🚨 (HITL #1)
│  └─ Assess budget fit, present options if needed
│
├─ Phase 4: Suggestions Checkpoint 🚨 (HITL #2)
│  └─ Present 7-point overview, get user approval
│
└─ Phase 5: Organization (SequentialAgent)
   ├─ Activities Agent
   ├─ Itinerary Agent
   └─ Document Generator Agent
    ↓
Vertex AI / Gemini Models
    ↓
Comprehensive Vacation Plan
```

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud account (for Vertex AI - optional but recommended)
- API keys for external services (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/RBATHINENI78/AI-Powered_Vacation_Planner.git
cd AI-Powered_Vacation_Planner

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally (Free Gemini API)

```bash
# Start web UI
adk web agents_web --port 8080

# Access at http://localhost:8080/dev-ui/?app=vacation_planner

# Or run CLI
adk run
```

### Running on Vertex AI (Production)

See [VERTEX_AI_DEMO_PLAN.md](VERTEX_AI_DEMO_PLAN.md) for detailed setup instructions.

**Quick setup:**
```bash
# Set GCP environment variables
export GOOGLE_APPLICATION_CREDENTIALS=~/vacation-demo-key.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1

# ADK automatically detects and uses Vertex AI
adk web agents_web --port 8080
```

## Project Structure

```
.
├── adk_agents/              # 12 specialized ADK agents
│   ├── travel_advisory.py   # Travel restrictions checking
│   ├── destination.py       # Weather and packing recommendations
│   ├── immigration.py       # Visa requirements
│   ├── currency.py          # Currency exchange and budget
│   ├── booking.py           # Flight, hotel, car rental agents
│   ├── activities.py        # Activity recommendations
│   ├── itinerary.py         # Day-by-day itinerary generation
│   ├── documents.py         # Travel document generation
│   ├── budget_checkpoint.py # HITL budget assessment
│   └── suggestions_checkpoint.py # HITL approval checkpoint
│
├── workflows/               # ADK workflow orchestration
│   └── vacation_workflow.py # Main orchestrator (12 agents, 5 phases)
│
├── tools/                   # FunctionTool implementations
│   ├── weather_tools.py     # OpenWeather API integration
│   ├── booking_tools.py     # Flight/hotel/car rental tools
│   ├── state_dept_tools.py  # State Department API
│   └── currency_tools.py    # Exchange rates
│
├── mcp_servers/             # MCP server implementations
│   ├── amadeus_flights.py   # Amadeus Flight API
│   └── amadeus_hotels.py    # Amadeus Hotel API
│
├── callbacks/               # ADK canonical callbacks
│   ├── logging_callbacks.py # Performance tracking
│   └── hitl_callbacks.py    # HITL pause logic
│
├── agents_web/              # ADK web UI configuration
│   └── vacation_planner/    # Web agent entry point
│
├── config.py                # Centralized model configuration
├── app.py                   # ADK app entry point
├── .env.example             # Environment template
└── VERTEX_AI_DEMO_PLAN.md   # Production deployment guide
```

## Example Usage

### Simple Trip

**Input:**
```
"Plan a week-long trip to Hawaii for 2 adults in March 2026 with $5000 budget"
```

**Output includes:**
- Travel advisories and safety info
- Weather forecast for March 2026
- Visa requirements (none for US travelers)
- 3-5 specific flight options with airlines, prices, routes
- Hotel recommendations with booking links
- Budget checkpoint: "$4,200 estimated, $800 remaining - ✅ Within budget"
- 7-point trip overview for user approval
- Day-by-day itinerary with activities
- Travel documents and packing checklist

### Complex Multi-City Trip

**Input:**
```
"Plan a 2-week trip to Europe (Paris and Rome) for 2 people in June 2026 with $8000 budget"
```

**Handles:**
- Multi-city coordination
- International travel (visa, currency, customs)
- Inter-European flights/trains
- Budget allocation across cities
- Coordinated itinerary

## Configuration

### Model Selection

Edit `config.py` to customize models per agent:

```python
AGENT_MODELS = {
    # Complex reasoning - Thinking model
    "itinerary": "gemini-2.0-flash-thinking-exp-1219",
    "budget_checkpoint": "gemini-2.0-flash-thinking-exp-1219",

    # Simple tasks - Flash-lite model (cost-effective)
    "flight_booking": "gemini-2.5-flash-lite",
    "hotel_booking": "gemini-2.5-flash-lite",
    # ...
}
```

### API Keys

Required for full functionality (all optional):

- `OPENWEATHER_API_KEY` - Weather data (free tier: 1000 calls/day)
- `AMADEUS_CLIENT_ID` / `AMADEUS_CLIENT_SECRET` - Real flight/hotel data
- `GEMINI_API_KEY` - Free Gemini API (or use Vertex AI)

**Note:** System works without API keys using LLM knowledge-based estimates.

## Performance Metrics

- **Parallel Speedup**: Booking phase runs 3x faster than sequential
- **Code Reduction**: 86% less code vs custom implementation (2,789 → 400 lines)
- **Average Response Time**: ~45-60 seconds for complete plan
- **Cost per Trip** (Vertex AI):
  - Simple trip: ~$0.01-0.02
  - Complex trip: ~$0.05-0.10
  - Multi-city trip: ~$0.10-0.20

## Development

### Testing Individual Agents

```bash
# Test specific agent
python -c "from adk_agents.travel_advisory import TravelAdvisoryAgent; import asyncio; asyncio.run(TravelAdvisoryAgent().run('Check Hawaii'))"

# Test workflow phases
python workflows/vacation_workflow.py
```

### Running Tests

```bash
pytest tests/
```

## Troubleshooting

### Rate Limit Errors (429)

**Free Gemini API:**
- gemini-2.0-flash-exp: 200 req/min
- gemini-2.5-flash-lite: 250k tokens/min

**Solution:** Switch to Vertex AI for production quotas (10,000+ req/min)

### Date Inference Not Working

Ensure main orchestrator has date normalization instructions. Check `workflows/vacation_workflow.py` line 155-181.

### Flight Booking Not Providing Options

Agent must be instructed to follow `llm_instruction` from tools. See `adk_agents/booking.py` FlightBookingAgent description.

## Documentation

- [VERTEX_AI_DEMO_PLAN.md](VERTEX_AI_DEMO_PLAN.md) - Complete Vertex AI deployment guide
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Model configuration reference
- [GETTING_STARTED.md](GETTING_STARTED.md) - Detailed setup instructions

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Powered by [Google Gemini Models](https://ai.google.dev/)
- Real-time data from [Amadeus API](https://developers.amadeus.com/)
- Weather data from [OpenWeather API](https://openweathermap.org/api)

## Contact

**Repository:** https://github.com/RBATHINENI78/AI-Powered_Vacation_Planner

**Issues:** https://github.com/RBATHINENI78/AI-Powered_Vacation_Planner/issues

---

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
