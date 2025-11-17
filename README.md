# AI-Powered Global Vacation Planner

> Your Intelligent Travel Companion for Seamless Trip Planning

[![Google ADK](https://img.shields.io/badge/Google-ADK-4285f4?style=flat-square&logo=google)](https://adk.google)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## Overview

The **AI-Powered Global Vacation Planner** is a sophisticated multi-agent application built on Google's Agent Development Kit (ADK) that transforms vacation planning from a time-consuming chore into an intelligent, automated experience. By orchestrating specialized AI agents, integrating real-time data sources, and implementing human-in-the-loop decision-making, this application provides comprehensive, personalized vacation planning services.

### Key Features

- **Multi-Agent Architecture**: Specialized agents for weather, bookings, activities, finance, immigration, and security
- **Comprehensive Planning**: Flights, hotels, car rentals, activities, budget estimation, and visa guidance
- **Human-in-the-Loop**: Strategic decision points for user input and preference refinement
- **Security-First**: Advanced PII detection and protection mechanisms
- **Real-Time Data**: Live weather, flight, hotel, currency, and visa information
- **Session Memory**: Persistent conversation history and context management
- **MCP Integration**: Model Context Protocol for efficient tool communication

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Google ADK installed
- API keys for weather, flight, hotel services
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Powered_Vacation_Planner.git
cd AI-Powered_Vacation_Planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/init_db.py

# Run the application
python src/main.py
```

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Security Guardian Agent (PII)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Destination     │ │   Booking    │ │   Experience     │
│  Intelligence    │ │  Operations  │ │    Curator       │
└──────────────────┘ └──────────────┘ └──────────────────┘
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Financial      │ │ Immigration  │ │  Session Memory  │
│    Advisor       │ │  Specialist  │ │   & Documents    │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

### Agent Responsibilities

| Agent | Responsibility |
|-------|---------------|
| **Orchestrator** | Coordinates all agents, manages workflow, generates final itinerary |
| **Security Guardian** | Detects and redacts PII, ensures data security |
| **Destination Intelligence** | Weather analysis, climate scoring, seasonal insights |
| **Booking Operations** | Searches flights, hotels, car rentals |
| **Experience Curator** | Discovers activities, tours, cultural experiences |
| **Financial Advisor** | Currency conversion, budget estimation, cost optimization |
| **Immigration Specialist** | Visa requirements, documentation guidance, application process |

---

## Usage Examples

### Basic Vacation Planning

```python
from src.agents.orchestrator import OrchestratorAgent

# Initialize orchestrator
orchestrator = OrchestratorAgent(config)

# Plan vacation
result = await orchestrator.plan_vacation({
    "destination": "Paris, France",
    "origin": "New York, USA",
    "citizenship": "United States",
    "start_date": "2025-06-15",
    "end_date": "2025-06-25",
    "travelers": 2,
    "budget_preference": "moderate",
    "interests": ["museums", "cuisine", "architecture"]
})

print(result["itinerary"])
print(result["budget"])
print(result["visa_guide"])
```

### Human-in-the-Loop Example

```python
# The system will automatically prompt for decisions:

# Decision Point 1: Weather Analysis
"""
Based on weather analysis, Paris will have:
- Average temp: 20-25°C
- Rain probability: 30%
- Peak tourist season

Would you like to:
1. Keep current dates
2. Shift to September (better weather, fewer tourists)
3. Extend trip duration
"""

# Decision Point 2: Booking Selection
"""
Flight Options:
A) Direct flight - $850 per person
B) 1 stop - $620 per person
C) 2 stops - $480 per person

Which option do you prefer? [A/B/C]
"""
```

---

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Project Submission](docs/PROJECT_SUBMISSION.md)**: Complete project write-up (<1500 words)
- **[Architecture](docs/ARCHITECTURE.md)**: System design and Mermaid diagrams
- **[Security & PII Protection](docs/SECURITY_AND_PII_PROTECTION.md)**: Security framework and implementation
- **[Technical Implementation](docs/TECHNICAL_IMPLEMENTATION.md)**: Code examples and deployment guide

---

## Key Technologies

### Core Framework
- **Google ADK**: Multi-agent orchestration
- **Python 3.11+**: Application development
- **Model Context Protocol (MCP)**: Tool integration

### AI/ML
- **Google Gemini**: Language model
- **Microsoft Presidio**: PII detection
- **Sentence Transformers**: Embeddings

### Data & Storage
- **PostgreSQL**: Persistent data storage
- **Redis**: Session management & caching
- **S3/GCS**: Document storage

### External APIs
- **OpenWeather API**: Weather data
- **Amadeus API**: Flights & hotels
- **Rentalcars.com API**: Car rentals
- **ExchangeRate-API**: Currency conversion
- **VisaHQ API**: Visa information

---

## Security Features

### PII Protection

The application implements multi-layered PII detection:

1. **Pattern-based Detection**: Regex patterns for SSN, passport, credit cards
2. **ML-based Detection**: Microsoft Presidio for contextual PII
3. **Contextual Analysis**: Understanding PII from surrounding text

### Redaction Example

```
Input:  "My SSN is 123-45-6789 and I want to visit Paris"
Output: "My SSN is [SSN REDACTED] and I want to visit Paris"
        + Security event logged
        + User notification sent
```

### Compliance

- ✅ GDPR compliant
- ✅ CCPA compliant
- ✅ PCI DSS standards for payment data
- ✅ SOC 2 requirements

---

## Human-in-the-Loop Workflow

The system identifies strategic decision points where user input enhances planning:

```mermaid
graph LR
    A[Agent Analysis] --> B{Needs User Input?}
    B -->|Yes| C[Present Options]
    B -->|No| D[Continue Automation]
    C --> E[Receive Decision]
    E --> F[Update Context]
    F --> D
    D --> G[Next Stage]
```

### Decision Types

1. **Date Adjustments**: When weather suggests better periods
2. **Budget Optimization**: When cost-saving alternatives exist
3. **Booking Selection**: Choosing between flight/hotel options
4. **Activity Preferences**: Selecting experiences and tours

---

## Project Structure

```
AI-Powered_Vacation_Planner/
├── src/
│   ├── agents/              # Agent implementations
│   ├── tools/               # Tool implementations
│   ├── mcp/                 # MCP server implementations
│   ├── memory/              # Session & memory management
│   ├── prompts/             # Prompt templates
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── config/                  # Configuration files
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_agents/

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/

# Type checking
mypy src/

# Linting
pylint src/
```

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t vacation-planner .

# Run with docker-compose
docker-compose up -d
```

### Environment Variables

Required environment variables:

```env
# API Keys
OPENWEATHER_API_KEY=your_key_here
AMADEUS_API_KEY=your_key_here
AMADEUS_API_SECRET=your_secret_here
EXCHANGERATE_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vacation_planner
REDIS_URL=redis://localhost:6379/0

# Google ADK
GOOGLE_ADK_PROJECT_ID=your_project_id
GOOGLE_ADK_API_KEY=your_api_key

# Security
ENCRYPTION_KEY=your_encryption_key
SECRET_KEY=your_secret_key
```

---

## Roadmap

### Phase 1: Core Features ✅
- [x] Multi-agent architecture
- [x] Weather and destination analysis
- [x] Booking search integration
- [x] Budget estimation
- [x] Visa requirements
- [x] PII protection

### Phase 2: Enhanced Features (In Progress)
- [ ] Real-time booking capabilities
- [ ] Group trip planning
- [ ] Loyalty program integration
- [ ] Mobile application

### Phase 3: Advanced Features (Planned)
- [ ] AR/VR destination previews
- [ ] Real-time trip support during travel
- [ ] Sustainable travel options
- [ ] Social sharing and collaboration

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Google ADK Team**: For the powerful agent development framework
- **OpenWeather**: Weather data API
- **Amadeus**: Travel data APIs
- **Microsoft Presidio**: PII detection library
- **Open Source Community**: For the amazing tools and libraries

---

## Contact

**Project Maintainer**: [Your Name]
- Email: your.email@example.com
- LinkedIn: [Your LinkedIn]
- GitHub: [@yourusername](https://github.com/yourusername)

**Project Link**: [https://github.com/yourusername/AI-Powered_Vacation_Planner](https://github.com/yourusername/AI-Powered_Vacation_Planner)

---

## Screenshots

### Planning Interface
*[Add screenshot of planning interface]*

### Itinerary Output
*[Add screenshot of generated itinerary]*

### Budget Breakdown
*[Add screenshot of budget analysis]*

---

## Demo Video

[Watch the demo on YouTube](https://youtube.com/your-demo-video)

---

## Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 📖 Improving documentation
- 🤝 Contributing code

---

<p align="center">
  <b>Built with ❤️ using Google ADK</b>
</p>

<p align="center">
  <i>Making vacation planning intelligent, secure, and effortless</i>
</p>
