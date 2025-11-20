"""
Vacation Planner Agent - Lightweight ADK Web Interface Entry Point
Delegates all work to the Orchestrator and specialized agents in src/agents/
"""

import sys
import os
from pathlib import Path

# Add src directory to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the orchestrator and all specialized agents
from src.agents.orchestrator import OrchestratorAgent
from src.agents.financial_advisor import FinancialAdvisorAgent
from src.agents.immigration_specialist import ImmigrationSpecialistAgent
from src.agents.booking_agents import FlightBookingAgent, HotelBookingAgent
from src.agents.destination_intelligence import DestinationIntelligenceAgent

# Initialize the orchestrator (which manages all other agents)
orchestrator = OrchestratorAgent()

# Initialize specialized agents for direct tool access
financial_advisor = FinancialAdvisorAgent()
immigration_specialist = ImmigrationSpecialistAgent()
flight_booking = FlightBookingAgent()
hotel_booking = HotelBookingAgent()
destination_intelligence = DestinationIntelligenceAgent()


# ==================== Lightweight Tool Wrappers ====================
# These delegate to the specialized agents

async def get_weather_info(city: str, country: str = "") -> dict:
    """Get weather information for a destination using DestinationIntelligence agent."""
    result = await destination_intelligence.execute({
        "city": city,
        "country": country
    })

    # Extract weather data from the agent response
    if result.get("status") == "success" and "current_weather" in result:
        weather = result["current_weather"]
        packing = result.get("packing_list", [])
        return {
            "city": weather.get("location", city),
            "country": weather.get("country", country),
            "temperature": f"{weather.get('temperature', 'N/A')}°C",
            "feels_like": f"{weather.get('feels_like', 'N/A')}°C",
            "conditions": weather.get("description", "N/A"),
            "humidity": f"{weather.get('humidity', 'N/A')}%",
            "packing_suggestions": packing
        }
    return {"error": "Weather data unavailable"}


async def check_visa_requirements(citizenship: str, destination: str, duration_days: int = 30) -> dict:
    """
    Check visa requirements using Immigration Specialist agent.

    Args:
        citizenship: Traveler's citizenship country (e.g., "India", "USA", "UK")
                    Extract from user's prompt if mentioned (e.g., "Citizenship: India")
        destination: Destination country (e.g., "India", "France", "Japan")
        duration_days: Length of stay in days

    IMPORTANT: Always extract citizenship from the user's prompt if provided.
    Look for patterns like "Citizenship: [country]" or "citizen of [country]".
    """
    result = await immigration_specialist.execute({
        "citizenship": citizenship,
        "destination": destination,
        "duration_days": duration_days
    })

    # Immigration specialist returns the visa_requirements directly in the result
    if result.get("status") == "success":
        return result.get("visa_requirements", {})
    return result.get("visa_requirements", {"error": "Visa data unavailable"})


async def get_currency_exchange(origin: str, destination: str, amount: float = 1.0) -> dict:
    """Get currency exchange rates using Financial Advisor agent."""
    result = await financial_advisor.execute({
        "task": "currency_exchange",
        "origin": origin,
        "destination": destination,
        "amount": amount
    })

    # Financial advisor returns currency_info in the result
    if result.get("status") == "success":
        return result.get("currency_info", {})
    return {"error": "Currency data unavailable"}


async def search_flights(origin: str, destination: str, departure_date: str, return_date: str = "", travelers: int = 1) -> dict:
    """Search for flights using Flight Booking agent."""
    result = await flight_booking.execute({
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers
    })

    # Return the flight_info from the result
    if result.get("status") == "success":
        return result.get("flight_info", {})
    return result.get("flight_info", {"error": "Flight data unavailable"})


async def search_hotels(destination: str, check_in: str, check_out: str, guests: int = 2, rooms: int = 1) -> dict:
    """Search for hotels using Hotel Booking agent."""
    result = await hotel_booking.execute({
        "destination": destination,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "rooms": rooms
    })

    # Return the hotel_info from the result
    if result.get("status") == "success":
        return result.get("hotel_info", {})
    return result.get("hotel_info", {"error": "Hotel data unavailable"})


async def generate_detailed_itinerary(destination: str, start_date: str, end_date: str, interests: str, travelers: int = 2) -> dict:
    """Generate detailed day-by-day itinerary using Destination Intelligence agent."""
    # For itinerary, the DestinationIntelligence agent needs different task
    # Let's return an instruction for the LLM to generate the itinerary
    from datetime import datetime
    try:
        d1 = datetime.strptime(start_date, "%Y-%m-%d")
        d2 = datetime.strptime(end_date, "%Y-%m-%d")
        days = (d2 - d1).days + 1
    except:
        days = 7

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "days": days,
        "travelers": travelers,
        "interests": interests,
        "instruction": f"Generate a detailed {days}-day itinerary for {destination} focusing on: {interests}"
    }


async def generate_trip_document(destination: str, start_date: str, end_date: str, travelers: int, origin: str = "", interests: str = "", budget: float = 0.0) -> dict:
    """Generate complete trip planning document using Orchestrator."""
    result = await orchestrator.plan_vacation(
        f"Plan a trip from {origin} to {destination} from {start_date} to {end_date} for {travelers} travelers "
        f"with interests in {interests} and budget ${budget}"
    )
    return {
        "document": result.get("plan", {}).get("itinerary", ""),
        "format": "markdown",
        "filename": f"{destination.lower().replace(' ', '_')}_trip_{start_date}.md"
    }


# ==================== ADK Agent Definition ====================

# Create the main agent with tool wrappers
default_api = Agent(
    model="gemini-2.5-flash",
    name="vacation_planner",
    description="""AI-powered vacation planning assistant using multi-agent orchestration.

Coordinates specialized agents to help users plan comprehensive vacations:
- Destination Intelligence: Weather, attractions, itineraries
- Immigration Specialist: Visa requirements, travel documents
- Financial Advisor: Currency exchange, budgeting
- Booking Agents: Flights and hotels search
- Orchestrator: Complete trip planning workflow

IMPORTANT INSTRUCTIONS FOR EXTRACTING USER INFORMATION:

1. CITIZENSHIP EXTRACTION:
   - Look for explicit mentions: "Citizenship: [country]", "citizen of [country]", "I am from [country]"
   - If found, IMMEDIATELY use it when calling check_visa_requirements()
   - DO NOT ask for confirmation if citizenship is clearly stated
   - Example: "Citizenship: India" → use citizenship="India"

2. DATES AND DURATION:
   - Extract from patterns like "December 15-25, 2025" or "10-night vacation"
   - Calculate duration_days from date ranges

3. ORIGIN AND DESTINATION:
   - Origin: Look for "from [city/country]" or "Origin: [location]"
   - Destination: Look for "to [city/country]" or destination city names

4. BUDGET:
   - Extract from "$5000 total", "Budget: $X", etc.

Always use information explicitly provided by the user. Only ask for clarification if critical information is genuinely missing.""",
    tools=[
        FunctionTool(get_weather_info),
        FunctionTool(check_visa_requirements),
        FunctionTool(get_currency_exchange),
        FunctionTool(search_flights),
        FunctionTool(search_hotels),
        FunctionTool(generate_detailed_itinerary),
        FunctionTool(generate_trip_document),
    ]
)

# Alias for ADK web interface compatibility
root_agent = default_api
