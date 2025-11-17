# Technical Implementation Guide

## Overview

This document provides detailed technical implementation guidance for building the AI-Powered Vacation Planner using Google ADK. It covers agent implementation, tool integration, MCP setup, memory management, and human-in-the-loop workflows.

---

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Agent Implementation](#agent-implementation)
4. [Tool and MCP Integration](#tool-and-mcp-integration)
5. [Memory Management](#memory-management)
6. [Human-in-the-Loop Implementation](#human-in-the-loop-implementation)
7. [Prompt Engineering](#prompt-engineering)
8. [Deployment Guide](#deployment-guide)

---

## Technology Stack

### Core Technologies

```yaml
Framework:
  - Google ADK (Agent Development Kit)
  - Python 3.11+
  - Model Context Protocol (MCP)

AI/ML:
  - Google Gemini Models
  - LangChain (optional for advanced workflows)
  - Sentence Transformers (for embeddings)

Data Storage:
  - PostgreSQL 15+ (persistent data)
  - Redis 7+ (session management & caching)
  - S3/GCS (document storage)

APIs & Integrations:
  - OpenWeather API (weather data)
  - Amadeus API (flights & hotels)
  - Rentalcars.com API (car rentals)
  - ExchangeRate-API (currency conversion)
  - VisaHQ API (visa information)

Security:
  - Presidio (PII detection)
  - Cryptography library (encryption)
  - Python-dotenv (secrets management)

Development Tools:
  - pytest (testing)
  - black (code formatting)
  - mypy (type checking)
  - pre-commit (git hooks)
```

---

## Project Structure

```
AI-Powered_Vacation_Planner/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Main orchestrator agent
│   │   ├── security_guardian.py     # Security & PII protection
│   │   ├── destination_agent.py     # Weather & destination analysis
│   │   ├── booking_agent.py         # Flight, hotel, car bookings
│   │   ├── experience_agent.py      # Activities & tours
│   │   ├── financial_agent.py       # Budget & currency
│   │   └── immigration_agent.py     # Visa requirements
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── weather_tool.py
│   │   ├── flight_tool.py
│   │   ├── hotel_tool.py
│   │   ├── currency_tool.py
│   │   ├── visa_tool.py
│   │   └── pii_detector_tool.py
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── weather_server.py
│   │   ├── booking_server.py
│   │   └── financial_server.py
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── conversation_store.py
│   │   └── document_store.py
│   │
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── orchestrator_prompts.py
│   │   ├── agent_prompts.py
│   │   └── tool_prompts.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── formatters.py
│   │   └── helpers.py
│   │
│   └── main.py                      # Application entry point
│
├── tests/
│   ├── test_agents/
│   ├── test_tools/
│   └── test_security/
│
├── docs/
│   ├── PROJECT_SUBMISSION.md
│   ├── ARCHITECTURE.md
│   ├── SECURITY_AND_PII_PROTECTION.md
│   └── TECHNICAL_IMPLEMENTATION.md
│
├── config/
│   ├── agents.yaml
│   ├── tools.yaml
│   └── mcp_servers.yaml
│
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Agent Implementation

### Orchestrator Agent

```python
# src/agents/orchestrator.py

from google.adk import Agent, AgentConfig
from typing import Dict, List, Any
import asyncio

class OrchestratorAgent(Agent):
    """
    Main orchestrator that coordinates all specialized agents
    """

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.security_guardian = SecurityGuardianAgent(config.security_config)
        self.destination_agent = DestinationAgent(config.destination_config)
        self.booking_agent = BookingAgent(config.booking_config)
        self.experience_agent = ExperienceAgent(config.experience_config)
        self.financial_agent = FinancialAgent(config.financial_config)
        self.immigration_agent = ImmigrationAgent(config.immigration_config)
        self.session_manager = SessionManager()

    async def plan_vacation(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for vacation planning
        """
        # Step 1: Security validation
        validated_request = await self.security_guardian.validate_input(
            user_request
        )

        if validated_request.pii_detected:
            await self.notify_user_pii_detected(validated_request.findings)

        # Step 2: Initialize session
        session = await self.session_manager.create_session(
            validated_request.cleaned_input
        )

        # Step 3: Parallel agent execution - Phase 1 (Research)
        research_tasks = [
            self.destination_agent.analyze_destination(session.destination, session.dates),
            self.immigration_agent.check_visa_requirements(
                session.citizenship, session.destination
            ),
            self.financial_agent.initialize_budget(
                session.origin_country, session.destination_country
            )
        ]

        research_results = await asyncio.gather(*research_tasks)

        # Step 4: Human-in-the-loop - Review research findings
        research_review = await self.request_user_decision(
            decision_type="research_review",
            context=research_results,
            questions=[
                "Based on weather analysis, would you like to adjust dates?",
                "Does the visa requirement affect your planning?"
            ]
        )

        # Update session with user decisions
        await session.update_context(research_review)

        # Step 5: Parallel agent execution - Phase 2 (Bookings)
        booking_tasks = [
            self.booking_agent.search_flights(session),
            self.booking_agent.search_hotels(session),
            self.booking_agent.search_car_rentals(session),
            self.experience_agent.discover_activities(session)
        ]

        booking_results = await asyncio.gather(*booking_tasks)

        # Step 6: Financial analysis
        budget_analysis = await self.financial_agent.calculate_total_cost(
            booking_results, session
        )

        # Step 7: Human-in-the-loop - Review options
        booking_decisions = await self.request_user_decision(
            decision_type="booking_selection",
            context={
                "bookings": booking_results,
                "budget": budget_analysis
            },
            questions=[
                "Which flight option do you prefer?",
                "Select your hotel preference",
                "Budget optimization suggestions - accept?"
            ]
        )

        # Step 8: Finalize itinerary
        final_itinerary = await self.generate_itinerary(
            session, booking_decisions
        )

        # Step 9: Add visa guidance
        visa_guide = await self.immigration_agent.generate_visa_guide(
            session.citizenship, session.destination
        )

        # Step 10: Save to memory and generate documents
        await session.save_final_plan({
            "itinerary": final_itinerary,
            "budget": budget_analysis,
            "visa_guide": visa_guide
        })

        return {
            "status": "success",
            "itinerary": final_itinerary,
            "budget": budget_analysis,
            "visa_guide": visa_guide,
            "session_id": session.id
        }

    async def request_user_decision(
        self,
        decision_type: str,
        context: Dict,
        questions: List[str]
    ) -> Dict[str, Any]:
        """
        Implements human-in-the-loop decision point
        """
        decision_prompt = self._create_decision_prompt(
            decision_type, context, questions
        )

        # Present to user and wait for response
        user_response = await self.present_to_user(decision_prompt)

        # Log decision
        await self.session_manager.log_decision(
            decision_type, context, user_response
        )

        return user_response

    def _create_decision_prompt(
        self,
        decision_type: str,
        context: Dict,
        questions: List[str]
    ) -> str:
        """
        Creates a well-structured prompt for user decisions
        """
        prompt = f"""
# Decision Point: {decision_type.replace('_', ' ').title()}

## Current Analysis:
{self._format_context(context)}

## Your Input Needed:
"""
        for i, question in enumerate(questions, 1):
            prompt += f"\n{i}. {question}"

        prompt += "\n\nPlease provide your preferences to help me optimize your vacation plan."

        return prompt
```

### Destination Intelligence Agent

```python
# src/agents/destination_agent.py

from google.adk import Agent
from datetime import datetime, timedelta
from typing import Dict, List

class DestinationAgent(Agent):
    """
    Analyzes destination weather, climate, and optimal travel periods
    """

    def __init__(self, config):
        super().__init__(config)
        self.weather_tool = WeatherTool()

    async def analyze_destination(
        self,
        destination: str,
        travel_dates: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Comprehensive destination analysis
        """
        # Get weather forecast
        weather_forecast = await self.weather_tool.get_forecast(
            location=destination,
            start_date=travel_dates['start'],
            end_date=travel_dates['end']
        )

        # Get historical weather data (5-year average)
        historical_weather = await self.weather_tool.get_historical_data(
            location=destination,
            month=self._extract_month(travel_dates['start']),
            years=5
        )

        # Analyze suitability
        suitability_score = self._calculate_suitability(
            weather_forecast, historical_weather
        )

        # Generate insights
        insights = await self._generate_insights(
            weather_forecast,
            historical_weather,
            suitability_score
        )

        # Check for better periods
        alternative_dates = None
        if suitability_score < 0.7:
            alternative_dates = await self._suggest_better_dates(
                destination, travel_dates
            )

        return {
            "destination": destination,
            "forecast": weather_forecast,
            "historical_average": historical_weather,
            "suitability_score": suitability_score,
            "insights": insights,
            "alternative_dates": alternative_dates,
            "recommendation": self._create_recommendation(
                suitability_score, alternative_dates
            )
        }

    async def _generate_insights(
        self,
        forecast: Dict,
        historical: Dict,
        suitability: float
    ) -> str:
        """
        Uses LLM to generate human-readable insights
        """
        prompt = f"""
Analyze the weather conditions and provide vacation planning insights.

Forecast: {forecast}
Historical Average: {historical}
Suitability Score: {suitability}

Provide:
1. Weather summary for the travel period
2. What to pack
3. Activities suited for these conditions
4. Any weather-related warnings or considerations
"""
        insights = await self.llm.generate(prompt)
        return insights

    def _calculate_suitability(
        self,
        forecast: Dict,
        historical: Dict
    ) -> float:
        """
        Calculates destination suitability score (0-1)
        """
        factors = {
            "temperature_comfort": self._temp_comfort_score(forecast),
            "precipitation": self._precipitation_score(forecast),
            "seasonal_alignment": self._seasonal_score(forecast, historical),
            "extreme_weather": self._extreme_weather_score(forecast)
        }

        weights = {
            "temperature_comfort": 0.3,
            "precipitation": 0.3,
            "seasonal_alignment": 0.2,
            "extreme_weather": 0.2
        }

        score = sum(
            factors[key] * weights[key] for key in factors
        )

        return round(score, 2)
```

### Security Guardian Agent

```python
# src/agents/security_guardian.py

from google.adk import Agent
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import re
from typing import List, Dict, Any

class SecurityGuardianAgent(Agent):
    """
    Monitors and protects against PII exposure
    """

    def __init__(self, config):
        super().__init__(config)
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.pii_patterns = self._load_pii_patterns()

    async def validate_input(self, user_input: str) -> ValidationResult:
        """
        Validates and sanitizes user input
        """
        # Step 1: Basic validation
        if not self._validate_basic(user_input):
            return ValidationResult(valid=False, error="Invalid input format")

        # Step 2: PII detection using multiple methods
        pii_findings = await self._detect_pii_multi_method(user_input)

        # Step 3: Redaction if needed
        if pii_findings:
            cleaned_input = self._redact_pii(user_input, pii_findings)

            # Log security event
            await self._log_security_event({
                "event_type": "pii_detected",
                "findings": pii_findings,
                "severity": self._assess_severity(pii_findings)
            })

            return ValidationResult(
                valid=True,
                cleaned_input=cleaned_input,
                pii_detected=True,
                findings=pii_findings
            )

        return ValidationResult(
            valid=True,
            cleaned_input=user_input,
            pii_detected=False
        )

    async def _detect_pii_multi_method(
        self,
        text: str
    ) -> List[PIIFinding]:
        """
        Multi-method PII detection combining pattern, ML, and contextual analysis
        """
        findings = []

        # Method 1: Pattern-based (Regex)
        pattern_findings = self._pattern_detection(text)
        findings.extend(pattern_findings)

        # Method 2: ML-based (Presidio)
        ml_findings = await self._presidio_detection(text)
        findings.extend(ml_findings)

        # Method 3: Contextual analysis
        context_findings = self._contextual_detection(text)
        findings.extend(context_findings)

        # Deduplicate and consolidate
        return self._consolidate_findings(findings)

    def _pattern_detection(self, text: str) -> List[PIIFinding]:
        """
        Regex-based PII detection
        """
        findings = []

        patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b",
            "passport": r"\b[A-Z]{1,2}\d{6,9}\b",
            "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "phone": r"\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        }

        for pii_type, pattern in patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append(PIIFinding(
                    pii_type=pii_type,
                    start=match.start(),
                    end=match.end(),
                    text=match.group(),
                    confidence=0.95,
                    method="pattern"
                ))

        return findings

    async def _presidio_detection(self, text: str) -> List[PIIFinding]:
        """
        ML-based PII detection using Microsoft Presidio
        """
        results = self.analyzer.analyze(
            text=text,
            language="en",
            entities=[
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
                "CREDIT_CARD", "US_SSN", "US_PASSPORT"
            ]
        )

        findings = []
        for result in results:
            findings.append(PIIFinding(
                pii_type=result.entity_type.lower(),
                start=result.start,
                end=result.end,
                text=text[result.start:result.end],
                confidence=result.score,
                method="ml"
            ))

        return findings

    def _redact_pii(self, text: str, findings: List[PIIFinding]) -> str:
        """
        Redacts PII from text
        """
        # Sort by position (reverse) for safe replacement
        sorted_findings = sorted(findings, key=lambda x: x.start, reverse=True)

        redacted = text
        for finding in sorted_findings:
            replacement = self._get_redaction_text(finding.pii_type)
            redacted = (
                redacted[:finding.start] +
                replacement +
                redacted[finding.end:]
            )

        return redacted

    def _get_redaction_text(self, pii_type: str) -> str:
        """
        Returns appropriate redaction text for PII type
        """
        redactions = {
            "ssn": "[SSN REDACTED]",
            "us_ssn": "[SSN REDACTED]",
            "passport": "[PASSPORT REDACTED]",
            "us_passport": "[PASSPORT REDACTED]",
            "credit_card": "[CREDIT CARD REDACTED]",
            "email": "[EMAIL REDACTED]",
            "phone": "[PHONE REDACTED]",
            "phone_number": "[PHONE REDACTED]"
        }

        return redactions.get(pii_type.lower(), "[REDACTED]")
```

---

## Tool and MCP Integration

### Weather Tool Implementation

```python
# src/tools/weather_tool.py

from google.adk import Tool
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List

class WeatherTool(Tool):
    """
    Tool for fetching weather forecasts and historical data
    """

    def __init__(self):
        super().__init__(
            name="weather_forecast",
            description="""
            Fetches weather forecast and historical climate data for a location.
            Provides temperature, precipitation, wind, and other weather metrics.
            """
        )
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

    async def get_forecast(
        self,
        location: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get weather forecast for specified dates
        """
        # Get coordinates for location
        coords = await self._geocode(location)

        # Fetch forecast
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/forecast"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": self.api_key,
                "units": "metric"
            }

            async with session.get(url, params=params) as response:
                data = await response.json()

        # Process and format forecast
        forecast = self._process_forecast(data, start_date, end_date)

        return forecast

    async def get_historical_data(
        self,
        location: str,
        month: int,
        years: int = 5
    ) -> Dict[str, Any]:
        """
        Get historical weather averages for a location and month
        """
        coords = await self._geocode(location)

        # Calculate historical date range
        current_year = datetime.now().year
        historical_data = []

        for year in range(current_year - years, current_year):
            date = datetime(year, month, 15)  # Mid-month
            timestamp = int(date.timestamp())

            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/onecall/timemachine"
                params = {
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "dt": timestamp,
                    "appid": self.api_key,
                    "units": "metric"
                }

                async with session.get(url, params=params) as response:
                    data = await response.json()
                    historical_data.append(data)

        # Calculate averages
        averages = self._calculate_averages(historical_data)

        return averages

    def _process_forecast(
        self,
        raw_data: Dict,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Processes raw forecast data into structured format
        """
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        daily_forecasts = []

        for item in raw_data.get("list", []):
            forecast_time = datetime.fromtimestamp(item["dt"])

            if start <= forecast_time <= end:
                daily_forecasts.append({
                    "date": forecast_time.isoformat(),
                    "temperature": {
                        "min": item["main"]["temp_min"],
                        "max": item["main"]["temp_max"],
                        "avg": item["main"]["temp"]
                    },
                    "precipitation": item.get("rain", {}).get("3h", 0),
                    "conditions": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "humidity": item["main"]["humidity"]
                })

        return {
            "location": raw_data.get("city", {}).get("name"),
            "daily_forecasts": daily_forecasts,
            "summary": self._generate_summary(daily_forecasts)
        }
```

### MCP Server Implementation

```python
# src/mcp/weather_server.py

from mcp.server import MCPServer
from mcp.types import Tool, TextContent

class WeatherMCPServer(MCPServer):
    """
    MCP Server for weather-related tools
    """

    def __init__(self):
        super().__init__("weather-server")
        self.weather_tool = WeatherTool()

    def list_tools(self) -> List[Tool]:
        """
        Lists available tools in this MCP server
        """
        return [
            Tool(
                name="get_weather_forecast",
                description="Get weather forecast for a location and date range",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"}
                    },
                    "required": ["location", "start_date", "end_date"]
                }
            ),
            Tool(
                name="get_historical_weather",
                description="Get historical weather averages",
                input_schema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "month": {"type": "integer"},
                        "years": {"type": "integer"}
                    },
                    "required": ["location", "month"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: Dict) -> List[TextContent]:
        """
        Executes tool calls
        """
        if name == "get_weather_forecast":
            result = await self.weather_tool.get_forecast(
                location=arguments["location"],
                start_date=arguments["start_date"],
                end_date=arguments["end_date"]
            )
        elif name == "get_historical_weather":
            result = await self.weather_tool.get_historical_data(
                location=arguments["location"],
                month=arguments["month"],
                years=arguments.get("years", 5)
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

# Start MCP server
if __name__ == "__main__":
    server = WeatherMCPServer()
    server.run()
```

---

## Memory Management

### Session Manager Implementation

```python
# src/memory/session_manager.py

from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import json

class SessionManager:
    """
    Manages user sessions, conversation history, and context
    """

    def __init__(self, redis_client, postgres_client):
        self.redis = redis_client  # Short-term memory
        self.db = postgres_client   # Long-term storage
        self.session_ttl = timedelta(hours=24)

    async def create_session(self, user_input: Dict) -> Session:
        """
        Creates a new planning session
        """
        session_id = str(uuid.uuid4())

        session = Session(
            id=session_id,
            created_at=datetime.utcnow(),
            user_input=user_input,
            context={},
            decisions=[],
            status="active"
        )

        # Store in Redis (short-term)
        await self._store_in_redis(session)

        # Log in PostgreSQL (long-term)
        await self._log_in_db(session)

        return session

    async def update_context(self, session_id: str, updates: Dict):
        """
        Updates session context
        """
        session = await self.get_session(session_id)
        session.context.update(updates)
        session.updated_at = datetime.utcnow()

        await self._store_in_redis(session)

    async def log_decision(
        self,
        session_id: str,
        decision_type: str,
        context: Dict,
        user_response: Dict
    ):
        """
        Logs user decisions
        """
        session = await self.get_session(session_id)

        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": decision_type,
            "context": context,
            "user_response": user_response
        }

        session.decisions.append(decision)
        await self._store_in_redis(session)

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieves session from cache or database
        """
        # Try Redis first (faster)
        session_data = await self.redis.get(f"session:{session_id}")

        if session_data:
            return Session.from_json(session_data)

        # Fallback to database
        session_data = await self.db.fetch_one(
            "SELECT * FROM sessions WHERE id = $1",
            session_id
        )

        if session_data:
            session = Session.from_db_row(session_data)
            # Re-cache in Redis
            await self._store_in_redis(session)
            return session

        return None

    async def save_final_plan(
        self,
        session_id: str,
        final_data: Dict
    ):
        """
        Saves final vacation plan
        """
        session = await self.get_session(session_id)
        session.final_plan = final_data
        session.status = "completed"
        session.completed_at = datetime.utcnow()

        # Store in database
        await self.db.execute(
            """
            UPDATE sessions
            SET final_plan = $1, status = $2, completed_at = $3
            WHERE id = $4
            """,
            json.dumps(final_data),
            "completed",
            session.completed_at,
            session_id
        )

        # Generate document
        await self._generate_document(session)

    async def _store_in_redis(self, session: Session):
        """
        Stores session in Redis with TTL
        """
        await self.redis.setex(
            f"session:{session.id}",
            self.session_ttl,
            session.to_json()
        )

    async def _generate_document(self, session: Session):
        """
        Generates final itinerary document
        """
        document = ItineraryGenerator.generate(session)

        # Store in S3/GCS
        await self.document_store.save(
            f"itineraries/{session.id}.pdf",
            document
        )
```

---

## Human-in-the-Loop Implementation

```python
# src/utils/hitl.py

from typing import Dict, List, Any, Callable
from enum import Enum

class DecisionType(Enum):
    DATE_ADJUSTMENT = "date_adjustment"
    BUDGET_OPTIMIZATION = "budget_optimization"
    BOOKING_SELECTION = "booking_selection"
    ACTIVITY_PREFERENCE = "activity_preference"

class HITLManager:
    """
    Manages human-in-the-loop decision points
    """

    def __init__(self):
        self.decision_handlers = {
            DecisionType.DATE_ADJUSTMENT: self._handle_date_adjustment,
            DecisionType.BUDGET_OPTIMIZATION: self._handle_budget_optimization,
            DecisionType.BOOKING_SELECTION: self._handle_booking_selection,
            DecisionType.ACTIVITY_PREFERENCE: self._handle_activity_preference
        }

    async def request_decision(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        callback: Callable
    ) -> Dict[str, Any]:
        """
        Requests user decision at a decision point
        """
        # Create decision prompt
        prompt = await self._create_prompt(decision_type, context)

        # Present to user
        user_input = await callback(prompt)

        # Validate and process response
        processed_response = await self._process_response(
            decision_type,
            user_input,
            context
        )

        return processed_response

    async def _create_prompt(
        self,
        decision_type: DecisionType,
        context: Dict
    ) -> str:
        """
        Creates contextual prompt for decision
        """
        handler = self.decision_handlers.get(decision_type)
        if handler:
            return await handler(context)

        return self._create_generic_prompt(decision_type, context)

    async def _handle_date_adjustment(self, context: Dict) -> str:
        """
        Creates prompt for date adjustment decisions
        """
        weather_data = context.get("weather")
        current_dates = context.get("current_dates")

        prompt = f"""
# Weather Analysis & Date Recommendation

## Current Travel Dates
- Start: {current_dates['start']}
- End: {current_dates['end']}

## Weather Forecast
{self._format_weather(weather_data)}

## Recommendation
{weather_data.get('insights')}

## Question
Based on this weather analysis:
1. Keep current dates?
2. Adjust to alternative dates: {weather_data.get('alternative_dates')}?
3. Extend trip duration?

Please select an option (1-3) or provide custom dates:
"""
        return prompt

    async def _handle_booking_selection(self, context: Dict) -> str:
        """
        Creates prompt for booking selection
        """
        flights = context.get("flights", [])
        hotels = context.get("hotels", [])
        budget = context.get("budget")

        prompt = f"""
# Booking Options Review

## Flight Options
{self._format_flight_options(flights)}

## Hotel Options
{self._format_hotel_options(hotels)}

## Budget Summary
- Estimated Total: ${budget['total']}
- Per Category: {budget['breakdown']}

## Your Selections
Please select:
1. Preferred flight (enter flight number or A/B/C)
2. Preferred hotel (enter hotel name or 1/2/3)
3. Any budget concerns or adjustments needed?
"""
        return prompt
```

---

## Prompt Engineering

### Agent Prompt Templates

```python
# src/prompts/agent_prompts.py

class AgentPrompts:
    """
    Centralized prompt templates for all agents
    """

    ORCHESTRATOR_SYSTEM = """
You are the Orchestrator Agent for an AI-Powered Vacation Planner.
Your role is to coordinate specialized agents to create comprehensive travel plans.

RESPONSIBILITIES:
- Receive and validate user vacation planning requests
- Delegate tasks to specialized sub-agents
- Synthesize information from multiple agents
- Identify decision points requiring user input
- Generate final comprehensive itineraries

SECURITY GUIDELINES:
- NEVER expose sensitive PII
- Always validate inputs through Security Guardian
- Follow data minimization principles

OUTPUT STYLE:
- Clear, structured information
- Explain reasoning when making recommendations
- Highlight key decisions and tradeoffs
- Be transparent about limitations
"""

    DESTINATION_AGENT_TASK = """
You are the Destination Intelligence Agent.

CURRENT TASK:
Analyze the following destination for vacation planning:

Destination: {destination}
Travel Dates: {start_date} to {end_date}
Duration: {duration} days

REQUIRED ANALYSIS:
1. Weather Forecast:
   - Daily temperature range
   - Precipitation probability
   - Wind conditions
   - Any extreme weather warnings

2. Climate Suitability:
   - Compare forecast to historical averages
   - Rate suitability for vacation (0-10 scale)
   - Identify any concerns

3. Seasonal Insights:
   - Tourist season (peak/off-peak)
   - Local events or festivals
   - Seasonal activities available

4. Recommendations:
   - Packing suggestions
   - Best activities for conditions
   - Any date adjustments to consider

WEATHER DATA:
{weather_data}

HISTORICAL DATA:
{historical_data}

Provide your analysis in structured format with clear recommendations.
"""

    BOOKING_AGENT_TOOL_PROMPT = """
You are the Booking Operations Agent with access to flight, hotel, and car rental tools.

TASK:
Search for travel options matching these requirements:

Origin: {origin}
Destination: {destination}
Dates: {start_date} to {end_date}
Passengers: {num_passengers}
Budget Preference: {budget_level}

TOOL USAGE:
1. Use flight_search tool to find flight options
2. Use hotel_search tool to find accommodations
3. Use car_rental_search tool if requested

SEARCH CRITERIA:
- Prioritize {priority} (cost/convenience/quality)
- Consider {num_passengers} passengers
- Budget: {budget_range}

For each category, provide:
- Top 3 options
- Price comparison
- Key features/benefits
- Recommendation with reasoning

OUTPUT FORMAT:
Return structured JSON with flight, hotel, and car options.
"""

    SECURITY_GUARDIAN_PROMPT = """
You are the Security Guardian Agent.

CRITICAL SECURITY RULES:
1. NEVER allow PII to pass through undetected
2. ALWAYS redact: SSN, passport numbers, credit cards, full names with addresses
3. LOG all security events
4. NOTIFY users when PII is detected

CURRENT INPUT TO VALIDATE:
{user_input}

ACTIONS:
1. Scan for PII patterns
2. Use ML detection for context
3. Redact any detected PII
4. Return cleaned input
5. Log security event if PII found

Be thorough - user privacy depends on you.
"""

    FINANCIAL_AGENT_PROMPT = """
You are the Financial Advisor Agent.

TASK:
Calculate comprehensive budget for this vacation:

Destination: {destination}
Origin: {origin}
Duration: {duration} days
Travelers: {num_travelers}

COMPONENTS TO ESTIMATE:
1. Flights: {flight_cost}
2. Hotels: {hotel_cost} per night × {nights} nights
3. Car Rental: {car_cost} per day × {days} days
4. Food: Estimate ${food_per_day} per person per day
5. Activities: {activity_costs}
6. Miscellaneous: 10-15% buffer

CURRENCY:
- Origin Currency: {origin_currency}
- Destination Currency: {dest_currency}
- Exchange Rate: {exchange_rate}

DELIVERABLES:
1. Total cost in both currencies
2. Daily budget breakdown
3. Category-wise expenses
4. Cost optimization suggestions
5. Budget vs actual tracking format
"""

    @staticmethod
    def create_tool_prompt(
        tool_name: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Creates dynamic tool prompt based on context
        """
        base_prompt = f"""
You have access to the {tool_name} tool.

Context: {json.dumps(context, indent=2)}

Use the tool to gather required information.
Validate all tool inputs before calling.
Handle errors gracefully.
Return structured, actionable data.
"""
        return base_prompt
```

---

## Deployment Guide

### Docker Configuration

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Environment
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Run
CMD ["python", "src/main.py"]
```

### Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/vacation_planner
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=vacation_planner
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Conclusion

This technical implementation guide provides a comprehensive foundation for building the AI-Powered Vacation Planner. The modular architecture, robust security measures, and thoughtful integration of Google ADK capabilities create a scalable, maintainable, and user-focused solution.
