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
from src.agents.document_generator import DocumentGeneratorAgent

# Import callbacks for tool execution tracking
from src.callbacks import with_callbacks

# Initialize the orchestrator (which manages all other agents)
orchestrator = OrchestratorAgent()

# Initialize specialized agents for direct tool access
financial_advisor = FinancialAdvisorAgent()
immigration_specialist = ImmigrationSpecialistAgent()
flight_booking = FlightBookingAgent()
hotel_booking = HotelBookingAgent()
destination_intelligence = DestinationIntelligenceAgent()
document_generator = DocumentGeneratorAgent()


# ==================== Lightweight Tool Wrappers ====================
# These delegate to the specialized agents

@with_callbacks
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


@with_callbacks
async def check_visa_requirements(citizenship: str, destination: str, duration_days: int = 30, origin: str = "") -> dict:
    """
    Check visa requirements using Immigration Specialist agent.

    Args:
        citizenship: Traveler's citizenship country (e.g., "India", "USA", "UK")
                    Extract from user's prompt if mentioned (e.g., "Citizenship: India")
        destination: Destination country (e.g., "India", "France", "Japan")
        duration_days: Length of stay in days
        origin: Origin location (e.g., "Charlotte, USA") - used to detect domestic travel

    IMPORTANT: Always extract citizenship from the user's prompt if provided.
    Look for patterns like "Citizenship: [country]" or "citizen of [country]".
    """

    # Extract country names from origin and destination to detect domestic travel
    def extract_country(location: str) -> str:
        """Extract country from 'City, Country' format."""
        if not location:
            return ""
        parts = [p.strip() for p in location.split(",")]
        # Return the last part as it's usually the country
        return parts[-1] if parts else location

    origin_country = extract_country(origin)
    dest_country = extract_country(destination)

    # Check if this is domestic travel (same country)
    if origin_country and dest_country and origin_country.lower() == dest_country.lower():
        return {
            "travel_type": "domestic",
            "origin_country": origin_country,
            "destination_country": dest_country,
            "visa_required": False,
            "message": f"This is domestic travel within {dest_country}. No additional visa required for this trip.",
            "note": f"Ensure you have valid documentation to be in {dest_country} (existing visa/residency if applicable)."
        }

    # For international travel, consult the immigration specialist
    result = await immigration_specialist.execute({
        "citizenship": citizenship,
        "destination": destination,
        "duration_days": duration_days
    })

    # Immigration specialist returns the visa_requirements directly in the result
    if result.get("status") == "success":
        visa_req = result.get("visa_requirements", {})
        visa_req["travel_type"] = "international"
        return visa_req
    return result.get("visa_requirements", {"error": "Visa data unavailable"})


@with_callbacks
async def get_currency_exchange(origin: str, destination: str, amount: float = 1.0, travelers: int = 2, nights: int = 7) -> dict:
    """Get currency exchange rates AND budget breakdown using Financial Advisor agent."""

    # Extract country names to check if domestic travel
    def extract_country(location: str) -> str:
        """Extract country from 'City, Country' format."""
        if not location:
            return ""
        parts = [p.strip() for p in location.split(",")]
        return parts[-1] if parts else location

    origin_country = extract_country(origin)
    dest_country = extract_country(destination)

    # Skip currency exchange for domestic travel (same country)
    if origin_country and dest_country and origin_country.lower() == dest_country.lower():
        return {
            "travel_type": "domestic",
            "message": f"Domestic travel within {dest_country}. Same currency used.",
            "currency_exchange_needed": False
        }

    # For international travel, get currency exchange AND budget breakdown
    result = await financial_advisor.execute({
        "origin": origin,
        "destination": destination,
        "budget": amount,
        "travelers": travelers,
        "nights": nights,
        "travel_style": "moderate"
    })

    # Financial advisor returns currency_info AND budget_breakdown
    if result.get("status") == "success":
        return {
            "currency_info": result.get("currency_info", {}),
            "budget_breakdown": result.get("budget_breakdown", {}),
            "saving_tips": result.get("saving_tips", []),
            "payment_recommendations": result.get("payment_recommendations", {})
        }
    return {"error": "Currency and budget data unavailable"}


@with_callbacks
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


@with_callbacks
async def search_hotels(destination: str, check_in: str, check_out: str, guests: int = 2, rooms: int = 1) -> dict:
    """Search for hotels using Hotel Booking agent."""
    result = await hotel_booking.execute({
        "destination": destination,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "rooms": rooms
    })

    # Return hotel data from the result
    # Amadeus API returns 'hotels', LLM fallback returns 'hotel_info'
    if result.get("status") == "success":
        # Check for Amadeus API result first (has 'hotels' key)
        if "hotels" in result:
            return {
                "source": result.get("source", "amadeus_api"),
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "hotels": result["hotels"],
                "booking_tips": result.get("booking_tips", [])
            }
        # Fall back to hotel_info for LLM-generated data
        return result.get("hotel_info", {})
    return {"error": "Hotel data unavailable"}


@with_callbacks
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
    """
    Generate complete trip planning document using DocumentGenerator agent.

    This should be called AFTER all other tools to compile the results.
    The document generator will format all the collected trip data.
    """
    result = await document_generator.execute({
        "destination": destination,
        "origin": origin,
        "start_date": start_date,
        "end_date": end_date,
        "travelers": travelers,
        "budget": budget,
        "interests": interests
    })

    if result.get("status") == "success":
        return result.get("document", {})
    return {"error": "Document generation failed"}


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

CRITICAL BEHAVIOR INSTRUCTIONS:

**BE PROACTIVE AND AUTO-COMPLETE**: When the user provides vacation details (destination, dates, budget, travelers),
AUTOMATICALLY call ALL relevant tools and generate the COMPLETE vacation plan including detailed itinerary.
DO NOT ask "Would you like me to proceed?" or "Should I generate the itinerary?" - JUST DO IT.
Your job is to deliver complete, actionable vacation plans, not to ask permission at every step.

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
   - IMPORTANT: Pass origin to check_visa_requirements() and get_currency_exchange() to detect domestic travel

4. BUDGET:
   - Extract from "$5000 total", "Budget: $X", etc.

5. DOMESTIC vs INTERNATIONAL TRAVEL:
   - If origin and destination are in the SAME country (e.g., "Charlotte, USA" to "Salt Lake City, USA"), it's DOMESTIC
   - For domestic travel, visa and currency exchange are NOT needed for the trip itself
   - For international travel (different countries), always check visa and currency

6. WORKFLOW EXECUTION - MANDATORY TOOL CALLS:
   **YOU MUST CALL THESE TOOLS - DO NOT GENERATE INFORMATION FROM YOUR KNOWLEDGE BASE**

   For EVERY vacation request, you MUST call these tools in order:

   a) ALWAYS call get_weather_info(city, country) - DO NOT generate weather from your knowledge

   b) For international travel, ALWAYS call:
      - check_visa_requirements(citizenship, destination, duration_days, origin)
      - get_currency_exchange(origin, destination, amount=budget, travelers=X, nights=X)
        This returns BOTH currency exchange rates AND complete budget breakdown
      DO NOT use your knowledge - ALWAYS use the tools to get real-time data

   c) ALWAYS call search_flights(origin, destination, departure_date, return_date, travelers)
      DO NOT generate flight information from your knowledge

   d) ALWAYS call search_hotels(destination, check_in, check_out, guests, rooms)
      DO NOT generate hotel information from your knowledge

   e) Call generate_detailed_itinerary(destination, start_date, end_date, interests, travelers)
      and USE THE RETURNED DATA to create the day-by-day plan

   f) FINALLY, call generate_trip_document(destination, start_date, end_date, travelers, origin, interests, budget)
      - This generates the final document structure for presenting the trip plan
      - Runs fast with no duplicate work

   g) Present the COMPLETE vacation plan with ALL sections:
      - Weather & Packing
      - Visa Requirements (international only)
      - Currency Exchange & Budget Breakdown (include saving tips!)
      - Flight Options
      - Hotel Options (with actual names and prices)
      - Day-by-Day Itinerary
      - Trip Summary

   **CRITICAL**: You must use ACTUAL tool call results, not your training data.
   If a tool returns data, use that exact data in your response.
   Include the budget breakdown with estimated costs for flights, hotels, activities, food, and transportation.

Always use information explicitly provided by the user. Only ask for clarification if critical information is genuinely missing.""",
    tools=[
        FunctionTool(get_weather_info),
        FunctionTool(check_visa_requirements),
        FunctionTool(get_currency_exchange),
        FunctionTool(search_flights),
        FunctionTool(search_hotels),
        FunctionTool(generate_detailed_itinerary),
        FunctionTool(generate_trip_document),  # Final step - compiles all data into document
    ]
)

# Alias for ADK web interface compatibility
root_agent = default_api
