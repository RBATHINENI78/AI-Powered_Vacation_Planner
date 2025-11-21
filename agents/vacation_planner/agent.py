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
from src.agents.travel_advisory import TravelAdvisoryAgent

# Import callbacks for tool execution tracking
from src.callbacks import with_callbacks

# Initialize the orchestrator (which manages all other agents)
orchestrator = OrchestratorAgent()

# Initialize specialized agents for direct tool access
travel_advisory = TravelAdvisoryAgent()
financial_advisor = FinancialAdvisorAgent()
immigration_specialist = ImmigrationSpecialistAgent()
flight_booking = FlightBookingAgent()
hotel_booking = HotelBookingAgent()
destination_intelligence = DestinationIntelligenceAgent()
document_generator = DocumentGeneratorAgent()


# ==================== Lightweight Tool Wrappers ====================
# These delegate to the specialized agents

@with_callbacks
async def check_travel_advisory(
    origin_country: str,
    destination_country: str,
    start_date: str = "",
    end_date: str = ""
) -> dict:
    """
    Check travel advisories and restrictions BEFORE planning a trip.
    This should be called FIRST to verify travel is possible.

    Args:
        origin_country: Traveler's citizenship/origin country (e.g., "United States", "Iran", "Cuba")
        destination_country: Destination country (e.g., "France", "United States", "Yemen")
        start_date: Travel start date (optional, YYYY-MM-DD format)
        end_date: Travel end date (optional, YYYY-MM-DD format)

    Returns:
        Advisory result with can_proceed flag, warnings, and blockers.
        If can_proceed is False, DO NOT proceed with trip planning.

    IMPORTANT:
    - For US citizens traveling abroad: Checks State Dept advisories (Level 1-4)
    - For foreign nationals traveling TO USA: Checks USA travel ban list
    - Level 4 or travel ban = BLOCKED (cannot proceed)
    - Level 3 = WARNING (proceed with caution)
    """
    result = await travel_advisory.execute({
        "origin_country": origin_country,
        "destination_country": destination_country,
        "travel_dates": {
            "start": start_date,
            "end": end_date
        }
    })

    if result.get("status") == "success":
        return {
            "can_proceed": result.get("can_proceed", True),
            "travel_type": result.get("travel_type", "international"),
            "origin": result.get("origin", origin_country),
            "destination": result.get("destination", destination_country),
            "advisories": result.get("advisories", []),
            "warnings": result.get("warnings", []),
            "blockers": result.get("blockers", []),
            "global_events": result.get("global_events", []),
            "recommendation": result.get("recommendation", "")
        }

    return {"error": "Travel advisory check failed", "can_proceed": True}


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
        destination: Destination country (e.g., "India", "France", "Japan") or "City, Country"
        duration_days: Length of stay in days
        origin: Origin location (e.g., "Charlotte, USA") - REQUIRED for domestic travel detection

    IMPORTANT:
    - Always extract citizenship from the user's prompt if provided.
    - Always provide origin parameter to detect domestic travel correctly.
    - For domestic travel (origin and destination in same country), visa requirements don't apply.
    """

    # Extract country names from origin and destination to detect domestic travel
    def extract_country(location: str) -> str:
        """Extract country from 'City, Country' format or return as-is if just country."""
        if not location:
            return ""
        # Normalize common country names
        location = location.strip()
        usa_variants = ["usa", "us", "united states", "america"]
        if location.lower() in usa_variants:
            return "USA"

        parts = [p.strip() for p in location.split(",")]
        # Return the last part as it's usually the country
        country = parts[-1] if len(parts) > 1 else parts[0]
        # Normalize USA variants
        if country.lower() in usa_variants:
            return "USA"
        return country

    origin_country = extract_country(origin)
    dest_country = extract_country(destination)

    # Check if this is domestic travel (same country)
    # This applies regardless of citizenship - if traveling within the same country,
    # no additional visa is needed for THIS TRIP (person already has valid status there)
    if origin_country and dest_country and origin_country.lower() == dest_country.lower():
        return {
            "travel_type": "domestic",
            "origin_country": origin_country,
            "destination_country": dest_country,
            "visa_required": False,
            "message": f"This is domestic travel within {dest_country}. No visa required for traveling between cities in the same country.",
            "note": "Domestic travel does not require visa processing. Your existing legal status in the country applies."
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
async def assess_budget_fit(
    user_budget: float,
    estimated_flights_cost: float,
    estimated_hotels_cost: float,
    estimated_activities_cost: float = 500.0,
    estimated_food_cost: float = 300.0
) -> dict:
    """
    🚨 MANDATORY BUDGET CHECKPOINT - Human-in-the-Loop (HITL) 🚨

    Call this AFTER getting flight and hotel estimates but BEFORE generating itinerary.
    This tool enforces budget assessment and forces you to STOP when user input is needed.

    Args:
        user_budget: User's stated budget in dollars
        estimated_flights_cost: Total flight cost from search_flights
        estimated_hotels_cost: Total hotel cost from search_hotels
        estimated_activities_cost: Estimated activities (default: $500)
        estimated_food_cost: Estimated food/dining (default: $300)

    Returns:
        {
            "status": "proceed" | "needs_user_input",  # IF "needs_user_input" -> STOP!
            "scenario": "budget_reasonable" | "budget_too_low" | "budget_excess",
            "message": str,
            "breakdown": {...},
            "recommendation": str  # Present this to user if needs_user_input
        }

    CRITICAL BEHAVIOR:
    - If status == "needs_user_input": You MUST display the message and recommendation,
      then STOP and WAIT for user response. DO NOT continue with itinerary.
    - If status == "proceed": Continue automatically with full trip planning.
    """
    total_estimated = (estimated_flights_cost + estimated_hotels_cost +
                      estimated_activities_cost + estimated_food_cost)

    breakdown = {
        "flights": f"${estimated_flights_cost:,.2f}",
        "hotels": f"${estimated_hotels_cost:,.2f}",
        "activities": f"${estimated_activities_cost:,.2f}",
        "food_dining": f"${estimated_food_cost:,.2f}",
        "total_estimated": f"${total_estimated:,.2f}",
        "user_budget": f"${user_budget:,.2f}",
        "difference": f"${user_budget - total_estimated:,.2f}",
        "difference_pct": f"{((user_budget - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0:.1f}%"
    }

    # SCENARIO A: Budget too low (costs exceed budget by >50%)
    if total_estimated > user_budget * 1.5:
        shortage = total_estimated - user_budget
        return {
            "status": "needs_user_input",
            "scenario": "budget_too_low",
            "breakdown": breakdown,
            "message": f"⚠️ BUDGET ALERT: Estimated costs (${total_estimated:,.2f}) exceed your budget (${user_budget:,.2f}) by ${shortage:,.2f}.",
            "recommendation": (
                "🛑 STOP HERE and present these numbered options to the user:\n\n"
                f"1. Proceed anyway (will need additional funding of ~${shortage:,.2f})\n"
                f"2. Adjust budget to ${total_estimated:,.2f} (recommended minimum)\n"
                "3. Reduce scope: shorter trip, budget hotels, fewer activities\n"
                "4. Suggest alternative destinations within your budget\n\n"
                "⛔ DO NOT CONTINUE until user chooses an option."
            )
        }

    # SCENARIO B: Budget much higher than needed (budget exceeds costs by >100%)
    elif user_budget > total_estimated * 2.0:
        excess = user_budget - total_estimated
        return {
            "status": "needs_user_input",
            "scenario": "budget_excess",
            "breakdown": breakdown,
            "message": f"💰 GOOD NEWS: Your ${user_budget:,.2f} budget exceeds estimated costs (${total_estimated:,.2f}) by ${excess:,.2f}!",
            "recommendation": (
                "🛑 STOP HERE and present these numbered upgrade options to the user:\n\n"
                f"1. Upgrade accommodations: Luxury 5-star hotels/resorts (+${excess * 0.4:,.2f})\n"
                "2. Extend trip: Add more days, explore nearby destinations\n"
                f"3. Premium experiences: Private tours, fine dining, spa treatments (+${excess * 0.3:,.2f})\n"
                "4. Multi-destination: Add another city/country to your itinerary\n"
                "5. Keep current plan and save the difference\n\n"
                "⛔ DO NOT CONTINUE until user chooses an option."
            )
        }

    # SCENARIO C: Budget reasonable (within ±50%)
    else:
        return {
            "status": "proceed",
            "scenario": "budget_reasonable",
            "breakdown": breakdown,
            "message": f"✅ Budget Assessment: Your ${user_budget:,.2f} budget is reasonable for estimated costs of ${total_estimated:,.2f}.",
            "recommendation": "✓ Proceed automatically with full trip planning."
        }


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

⚠️ **EXCEPTION**: The ONLY time you MUST pause is when the `assess_budget_fit` tool returns status="needs_user_input".
In that case, you MUST display the options and WAIT for user response before continuing.

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

   a) **FIRST**: Call check_travel_advisory(origin_country, destination_country, start_date, end_date)
      - This checks US State Department travel advisories and USA travel bans
      - If can_proceed is FALSE, STOP and inform the user about the travel restriction
      - If there are warnings (Level 3), inform the user but continue if they wish
      - For US citizens traveling abroad: Shows advisory levels 1-4
      - For foreign nationals traveling TO USA: Checks travel ban list

   b) ALWAYS call get_weather_info(city, country) - DO NOT generate weather from your knowledge

   c) ALWAYS call check_visa_requirements(citizenship, destination, duration_days, origin)
      - **CRITICAL**: Always pass the origin parameter to detect domestic travel!
      - For domestic travel (origin and destination in same country), the tool returns "visa_required: false"
      - Do NOT show visa requirements for domestic travel even if citizenship differs from destination
      - Example: Charlotte, USA to SaltlakeCity, USA = domestic travel, no visa section needed

   d) For international travel, ALWAYS call:
      - get_currency_exchange(origin, destination, amount=budget, travelers=X, nights=X)
        This returns BOTH currency exchange rates AND complete budget breakdown
      DO NOT use your knowledge - ALWAYS use the tools to get real-time data

   e) ALWAYS call search_flights(origin, destination, departure_date, return_date, travelers)
      DO NOT generate flight information from your knowledge

   f) ALWAYS call search_hotels(destination, check_in, check_out, guests, rooms)
      DO NOT generate hotel information from your knowledge

   g) 🚨 MANDATORY BUDGET CHECKPOINT 🚨
      ALWAYS call assess_budget_fit(user_budget, estimated_flights_cost, estimated_hotels_cost)
      - Extract costs from search_flights and search_hotels results
      - If result["status"] == "needs_user_input":
        * Display result["message"] and result["recommendation"] to user
        * STOP and WAIT for user to choose an option
        * DO NOT continue with itinerary generation
      - If result["status"] == "proceed":
        * Continue automatically with itinerary generation

   h) Call generate_detailed_itinerary(destination, start_date, end_date, interests, travelers)
      and USE THE RETURNED DATA to create the day-by-day plan

   i) Present the COMPLETE vacation plan with ALL sections:
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
        FunctionTool(check_travel_advisory),  # FIRST - Check travel restrictions before planning
        FunctionTool(get_weather_info),
        FunctionTool(check_visa_requirements),
        FunctionTool(get_currency_exchange),
        FunctionTool(search_flights),
        FunctionTool(search_hotels),
        FunctionTool(assess_budget_fit),  # MANDATORY HITL checkpoint - call after flights & hotels
        FunctionTool(generate_detailed_itinerary),
    ]
)

# Alias for ADK web interface compatibility
root_agent = default_api
