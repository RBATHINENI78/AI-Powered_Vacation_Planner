"""
Vacation Planner Agent - Enhanced with detailed itinerary and booking features
ADK Web Interface Compatible
"""

import os
import re
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# Import data modules
from .data.hotels import search_hotels_data
from .data.activities import ACTIVITY_DATABASE

# Import MCP servers for real API calls
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.mcp_servers.amadeus_flights import search_flights_amadeus_sync
from src.mcp_servers.amadeus_hotels import search_hotels_amadeus_sync

# Flag to use real API or mock data
USE_REAL_API = os.getenv("AMADEUS_CLIENT_ID") and os.getenv("AMADEUS_CLIENT_ID") != "your_amadeus_client_id"


# ==================== Core Tools ====================

def get_weather_info(city: str, country: str = "") -> dict:
    """Get weather information for a destination."""
    try:
        location = f"{city},{country}" if country else city
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": OPENWEATHER_API_KEY, "units": "metric"}

        with httpx.Client() as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                conditions = data["weather"][0]["description"]

                pack = []
                if temp < 15:
                    pack.extend(["Warm jacket", "Layers", "Sweater"])
                elif temp < 25:
                    pack.extend(["Light jacket", "Long sleeves"])
                else:
                    pack.extend(["Light clothing", "Sunscreen", "Sunglasses"])
                if "rain" in conditions.lower():
                    pack.extend(["Umbrella", "Waterproof shoes"])

                return {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": f"{temp}°C",
                    "feels_like": f"{data['main']['feels_like']}°C",
                    "conditions": conditions.capitalize(),
                    "humidity": f"{data['main']['humidity']}%",
                    "packing_suggestions": list(set(pack))
                }
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def get_currency_exchange(origin: str, destination: str, amount: float = 1.0) -> dict:
    """
    Get currency exchange rate based on origin and destination countries/cities.

    IMPORTANT: Pass LOCATION NAMES (countries or cities), NOT currency codes.
    The tool automatically detects the correct currencies.

    Args:
        origin: Origin country or city name (e.g., "USA", "New York, USA", "Germany", "United Kingdom")
                DO NOT pass currency codes like "USD" or "EUR"
        destination: Destination country or city name (e.g., "India", "Kerala, India", "France", "Japan")
                     DO NOT pass currency codes like "INR" or "JPY"
        amount: Amount to convert in origin currency (default 1.0)

    Returns:
        Real-time exchange rate and conversion details

    Examples:
        get_currency_exchange("USA", "India", 5000) -> Converts 5000 USD to INR
        get_currency_exchange("Germany", "Qatar", 1000) -> Converts 1000 EUR to QAR
        get_currency_exchange("New York, USA", "Kerala, India", 5000) -> Converts 5000 USD to INR
    """

    def get_currency_from_restcountries(location_name: str) -> tuple:
        """
        Fetch currency info from RestCountries API.
        Returns (currency_code, currency_name, country_name) or (None, None, None) if not found.
        """
        # Extract parts from location string (e.g., "Kerala, India" -> try "India" first)
        parts = [p.strip() for p in location_name.split(",")]

        # Try each part, starting from the last (usually country)
        for part in reversed(parts):
            try:
                # First try exact match with fullText parameter
                url = f"https://restcountries.com/v3.1/name/{part}?fullText=true&fields=name,currencies"
                with httpx.Client(timeout=10) as client:
                    response = client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            country_data = data[0]
                            country_name = country_data.get("name", {}).get("common", part)
                            currencies = country_data.get("currencies", {})
                            if currencies:
                                currency_code = list(currencies.keys())[0]
                                currency_name = currencies[currency_code].get("name", currency_code)
                                return currency_code, currency_name, country_name

                    # If exact match fails, try partial match but find best result
                    url = f"https://restcountries.com/v3.1/name/{part}?fields=name,currencies"
                    response = client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            # Find the best match - prefer exact common name match
                            best_match = None
                            for country in data:
                                common_name = country.get("name", {}).get("common", "")
                                official_name = country.get("name", {}).get("official", "")
                                # Exact match on common or official name
                                if common_name.lower() == part.lower() or official_name.lower() == part.lower():
                                    best_match = country
                                    break
                                # Partial match - prefer shorter names (more likely to be the main country)
                                if best_match is None or len(common_name) < len(best_match.get("name", {}).get("common", "")):
                                    best_match = country

                            if best_match:
                                country_name = best_match.get("name", {}).get("common", part)
                                currencies = best_match.get("currencies", {})
                                if currencies:
                                    currency_code = list(currencies.keys())[0]
                                    currency_name = currencies[currency_code].get("name", currency_code)
                                    return currency_code, currency_name, country_name
            except Exception:
                continue

        # If country search failed, this might be a city - return None to trigger LLM fallback
        return None, None, None

    # Get currency for origin
    origin_currency, origin_currency_name, origin_country = get_currency_from_restcountries(origin)

    # Get currency for destination
    dest_currency, dest_currency_name, dest_country = get_currency_from_restcountries(destination)

    # If we couldn't determine origin currency, ask LLM to help
    if not origin_currency:
        return {
            "error": "currency_detection_failed",
            "location": origin,
            "message": f"Could not automatically determine the currency for '{origin}'.",
            "instruction": f"Please identify the country for '{origin}' and provide its currency code (e.g., USD for United States, EUR for France, INR for India). Then call this tool again with the country name."
        }

    # If we couldn't determine destination currency, ask LLM to help
    if not dest_currency:
        return {
            "error": "currency_detection_failed",
            "location": destination,
            "message": f"Could not automatically determine the currency for '{destination}'.",
            "instruction": f"Please identify the country for '{destination}' and provide its currency code (e.g., USD for United States, EUR for France, INR for India). Then call this tool again with the country name."
        }

    # If same currency, no conversion needed
    if origin_currency == dest_currency:
        return {
            "origin": origin,
            "origin_country": origin_country,
            "destination": destination,
            "destination_country": dest_country,
            "from_currency": origin_currency,
            "from_currency_name": origin_currency_name,
            "to_currency": dest_currency,
            "to_currency_name": dest_currency_name,
            "rate": 1.0,
            "amount": amount,
            "converted": amount,
            "message": f"Same currency - no conversion needed. Both {origin} and {destination} use {origin_currency_name} ({origin_currency})."
        }

    # Fetch real-time exchange rate
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{origin_currency}/{dest_currency}/{amount}"
        with httpx.Client(timeout=10) as client:
            response = client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "success":
                    return {
                        "origin": origin,
                        "origin_country": origin_country,
                        "destination": destination,
                        "destination_country": dest_country,
                        "from_currency": origin_currency,
                        "from_currency_name": origin_currency_name,
                        "to_currency": dest_currency,
                        "to_currency_name": dest_currency_name,
                        "rate": data["conversion_rate"],
                        "amount": amount,
                        "converted": round(data["conversion_result"], 2),
                        "formatted": f"1 {origin_currency} = {data['conversion_rate']} {dest_currency}",
                        "conversion_example": f"{amount} {origin_currency} = {round(data['conversion_result'], 2)} {dest_currency}",
                        "last_updated": data.get("time_last_update_utc", "N/A")
                    }
                else:
                    return {"error": f"Exchange rate API error: {data.get('error-type', 'Unknown error')}"}
        return {"error": f"Exchange rate API returned status {response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to fetch exchange rate: {str(e)}"}


def check_visa_requirements(citizenship: str, destination: str, duration_days: int = 30) -> dict:
    """
    Check visa and immigration requirements for travel.

    This tool validates inputs and returns structured data for the LLM to
    generate comprehensive immigration details using its knowledge.

    Args:
        citizenship: Traveler's citizenship/nationality (e.g., "US", "India", "UK")
        destination: Destination country or city (e.g., "France", "Kerala, India")
        duration_days: Planned duration of stay in days

    Returns:
        Structured data for LLM to generate detailed visa/immigration information
    """
    # Check if citizenship is provided
    if not citizenship or citizenship.strip() == "":
        return {
            "error": "citizenship_required",
            "message": "To provide accurate visa and immigration requirements, I need to know your citizenship/nationality. Please provide this information.",
            "prompt_user": True
        }

    # Extract destination country from city, state, country format
    dest_parts = destination.split(",")
    if len(dest_parts) > 1:
        dest_country = dest_parts[-1].strip()
    else:
        dest_country = destination.strip()

    # Return structured info for LLM to generate comprehensive details
    return {
        "citizenship": citizenship,
        "destination": destination,
        "destination_country": dest_country,
        "duration_days": duration_days,
        "instruction": f"""
Based on your knowledge, provide COMPREHENSIVE visa and immigration requirements for a {citizenship} citizen traveling to {destination} for {duration_days} days. Include:

1. **Visa Requirement**: Is visa required? What type?
2. **Application Process**: How to apply, where, processing time, fees
3. **Required Documents**: Complete list of documents needed
4. **Entry Requirements**: Passport validity, blank pages, etc.
5. **Travel Advisories**: Any current travel bans, restrictions, or warnings
6. **Health Requirements**: Vaccinations, COVID requirements if any
7. **Customs Regulations**: What can/cannot be brought in
8. **Duration of Stay**: Maximum allowed stay, extension options
9. **Special Notes**: Any specific requirements for {citizenship} citizens

Provide current, accurate information based on your training knowledge. If there are any travel bans or restrictions affecting {citizenship} citizens traveling to {dest_country}, clearly state them.
"""
    }


def detect_pii(text: str) -> dict:
    """Detect PII in text."""
    findings = []
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
        findings.append({"type": "SSN", "severity": "high"})
    if re.search(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', text):
        findings.append({"type": "Credit Card", "severity": "high"})
    return {
        "pii_detected": len(findings) > 0,
        "findings": findings,
        "recommendation": "Remove sensitive info" if findings else "No PII detected"
    }


# ==================== Enhanced Tools ====================

def search_flights(origin: str, destination: str, departure_date: str, return_date: str, travelers: int = 2) -> dict:
    """
    Provide flight information between origin and destination using LLM knowledge.

    This tool returns structured information that guides the LLM to provide
    typical flight details based on historical data and airline route knowledge.

    Args:
        origin: Origin city/country (e.g., "New York, USA", "Charlotte, USA")
        destination: Destination city/country (e.g., "Salt Lake City, USA", "Paris, France")
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        travelers: Number of travelers

    Returns:
        Structured data for LLM to generate detailed flight information
    """
    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers,
        "instruction_for_llm": f"""Using your knowledge of airlines, routes, and airports, provide SPECIFIC flight information for {origin} to {destination}:

**REQUIRED FORMAT - Provide 3-5 specific flight options like this:**

**Flight Option 1: [Specific Airline Name]**
- Route: [Origin Airport Code-Airport Name] → [Destination Airport Code-Airport Name]
- Flight Type: Direct / 1 stop via [Hub City] / 2 stops
- Typical Duration: X hours XX minutes
- Approximate Price: $XXX-$XXX per person (economy class, round-trip)
- Common Departure Times: Morning (6am-12pm) / Afternoon (12pm-6pm) / Evening (6pm-12am)
- Aircraft Type: [Common aircraft on this route]

**Flight Option 2:** [Continue with different airline...]

**IMPORTANT:**
- Use REAL airline names that actually operate this route (Delta, American, United, Southwest, etc. for US; Emirates, British Airways, Lufthansa for international)
- Use correct IATA airport codes (e.g., CLT for Charlotte, SLC for Salt Lake City)
- Be specific about typical hub cities for connections
- Provide realistic price ranges based on route distance and typical fares
- Include both direct flights AND connection options if applicable
- Mention if certain airlines have better schedules or pricing for this route

Do NOT say "I cannot provide" or "due to limitations" - use your knowledge to provide helpful, accurate typical flight information."""
    }


def search_hotels(destination: str, check_in: str, check_out: str, guests: int = 2, rooms: int = 1) -> dict:
    """
    Search for available hotels with booking links.

    Args:
        destination: City name (e.g., "Paris")
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        rooms: Number of rooms

    Returns:
        Top 3 hotels per category (budget, mid-range, luxury) with booking URLs
    """
    # Try real API first if credentials are available
    if USE_REAL_API:
        try:
            print(f"Calling Amadeus hotel API: {destination}, {check_in} to {check_out}, {guests} guests, {rooms} rooms")
            result = search_hotels_amadeus_sync(destination, check_in, check_out, guests, rooms)
            print(f"Amadeus hotel API response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
            if "error" not in result:
                print(f"Amadeus hotel API success! Found {len(result.get('hotels', {}).get('budget', []))} budget hotels")
                return result
            else:
                # Log the full error details
                print(f"Amadeus hotel API error: {result}")
        except Exception as e:
            import traceback
            print(f"Amadeus hotel API exception: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Fall back to mock data

    # Fall back to mock data
    try:
        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (d2 - d1).days
    except:
        nights = 7
    result = search_hotels_data(destination, nights, guests, rooms)
    if "error" in result:
        # Return more helpful error with API status
        result["api_status"] = "Amadeus API credentials configured" if USE_REAL_API else "Using mock data (no Amadeus credentials)"
        return result
    result["check_in"] = check_in
    result["check_out"] = check_out
    return result


def generate_detailed_itinerary(destination: str, start_date: str, end_date: str, interests: str, travelers: int = 2) -> dict:
    """
    Generate a detailed day-by-day itinerary with specific times.

    Args:
        destination: City name (e.g., "Paris")
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        interests: Comma-separated interests (e.g., "museums, food, architecture")
        travelers: Number of travelers

    Returns:
        Complete day-by-day itinerary with times, activities, and booking links
    """
    city = destination.split(",")[0].strip()
    if city not in ACTIVITY_DATABASE:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            num_days = (end - start).days + 1
        except:
            num_days = 7
        return {
            "limitation": f"Detailed timed itinerary data not available for {city}",
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": num_days,
            "travelers": travelers,
            "interests": interests,
            "recommendation": "Please generate a conceptual itinerary based on the destination and interests provided"
        }

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
    except:
        return {"error": "Invalid date format"}

    interest_list = [i.strip().lower() for i in interests.split(",")]
    city_activities = ACTIVITY_DATABASE[city]

    available = []
    for interest in interest_list:
        for category, activities in city_activities.items():
            if interest in category.lower() or category.lower() in interest:
                for act in activities:
                    act_copy = act.copy()
                    act_copy["category"] = category
                    available.append(act_copy)

    available.sort(key=lambda x: x["rating"], reverse=True)

    itinerary = []
    idx = 0

    for day_num in range(num_days):
        current_date = start + timedelta(days=day_num)
        day = {"day": day_num + 1, "date": current_date.strftime("%Y-%m-%d"), "day_name": current_date.strftime("%A"), "activities": []}

        if idx < len(available):
            act = available[idx]
            end_time = 9 + act["duration_hours"]
            day["activities"].append({
                "time_start": "09:00",
                "time_end": f"{int(end_time):02d}:{int((end_time % 1) * 60):02d}",
                "name": act["name"],
                "cost_per_person": act["cost"],
                "total_cost": act["cost"] * travelers,
                "booking_url": act.get("booking_url"),
                "address": act.get("address", ""),
                "tips": act.get("tips", "")
            })
            idx += 1

        day["activities"].append({"time_start": "12:30", "time_end": "14:00", "name": "Lunch", "type": "meal"})

        if idx < len(available):
            act = available[idx]
            end_time = 14 + act["duration_hours"]
            day["activities"].append({
                "time_start": "14:00",
                "time_end": f"{int(end_time):02d}:{int((end_time % 1) * 60):02d}",
                "name": act["name"],
                "cost_per_person": act["cost"],
                "total_cost": act["cost"] * travelers,
                "booking_url": act.get("booking_url"),
                "address": act.get("address", ""),
                "tips": act.get("tips", "")
            })
            idx += 1

        day["activities"].append({"time_start": "19:00", "time_end": "21:00", "name": "Dinner", "type": "meal"})
        itinerary.append(day)

    total_cost = sum(act.get("total_cost", 0) for d in itinerary for act in d["activities"] if "total_cost" in act)

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "total_days": num_days,
        "travelers": travelers,
        "itinerary": itinerary,
        "total_activity_cost": total_cost
    }


def generate_trip_document(destination: str, start_date: str, end_date: str, travelers: int, origin: str, interests: str, budget: float) -> dict:
    """
    Generate a complete downloadable trip document in Markdown format.

    Args:
        destination: Destination city
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        travelers: Number of travelers
        origin: Origin city
        interests: Comma-separated interests
        budget: Total budget in USD

    Returns:
        Complete trip document in Markdown format ready for download
    """
    city = destination.split(",")[0].strip()
    try:
        nights = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
    except:
        nights = 7

    # Get flight information (will be handled by LLM)
    flights = search_flights(origin, destination, start_date, end_date, travelers)
    hotels = search_hotels_data(city, nights, travelers, 1)
    itin = generate_detailed_itinerary(destination, start_date, end_date, interests, travelers)

    doc = f"""# {city} Vacation Plan

## Trip Overview
- **Destination:** {destination}
- **Dates:** {start_date} to {end_date} ({nights} nights)
- **Travelers:** {travelers}
- **Budget:** ${budget:,.2f}

---

## Flight Options

**Route:** {origin} → {destination}

*Please check airline websites or Google Flights, Kayak, or Skyscanner for real-time pricing and availability.*

"""

    doc += "---\n\n## Hotel Options\n\n"
    if "hotels" in hotels:
        for cat in ["budget", "mid_range", "luxury"]:
            doc += f"### {cat.replace('_', ' ').title()} Hotels\n"
            doc += "| Hotel | Location | Price | Book |\n|-------|----------|-------|------|\n"
            for h in hotels["hotels"].get(cat, [])[:3]:
                doc += f"| {h['name']} | {h['location']} | ${h['total_price']} | [Book]({h['booking_url']}) |\n"
            doc += "\n"
    else:
        doc += "*Hotel data not available for this destination. Please check Booking.com, Hotels.com, or Agoda for options.*\n\n"

    doc += "---\n\n## Daily Itinerary\n\n"
    if "itinerary" in itin:
        for day in itin["itinerary"]:
            doc += f"### Day {day['day']} - {day['date']} ({day['day_name']})\n\n"
            for act in day["activities"]:
                if act.get("type") == "meal":
                    doc += f"**{act['time_start']} - {act['time_end']}:** {act['name']}\n\n"
                else:
                    doc += f"**{act['time_start']} - {act['time_end']}:** {act['name']}\n"
                    if act.get("total_cost"):
                        doc += f"- Cost: ${act['total_cost']}\n"
                    if act.get("booking_url"):
                        doc += f"- [Book tickets]({act['booking_url']})\n"
                    if act.get("tips"):
                        doc += f"- Tip: {act['tips']}\n"
                    doc += "\n"
    else:
        doc += f"*Detailed itinerary data not available. Please see conceptual itinerary based on {interests}.*\n\n"

    # Calculate costs with fallbacks for unavailable data
    flight_cost = 1500  # Default estimate
    if "flights" in flights and flights["flights"].get("mid_range"):
        flight_cost = flights["flights"]["mid_range"][0]["total_price"]

    hotel_cost = nights * 100 * travelers  # Default estimate per night
    if "hotels" in hotels and hotels["hotels"].get("mid_range"):
        hotel_cost = hotels["hotels"]["mid_range"][0]["total_price"]

    activity_cost = itin.get("total_activity_cost", nights * 50 * travelers)  # Default estimate
    food_cost = nights * 100 * travelers
    total = flight_cost + hotel_cost + activity_cost + food_cost

    doc += f"""---

## Budget Summary

| Category | Cost |
|----------|------|
| Flights | ${flight_cost:,.2f} |
| Hotels | ${hotel_cost:,.2f} |
| Activities | ${activity_cost:,.2f} |
| Food | ${food_cost:,.2f} |
| **TOTAL** | **${total:,.2f}** |

{"✅ Within budget" if total <= budget else f"⚠️ Over budget by ${total - budget:,.2f}"}

---

*Generated by AI-Powered Vacation Planner*
"""

    return {
        "document": doc,
        "format": "markdown",
        "filename": f"{city.lower().replace(' ', '_')}_trip_{start_date}.md",
        "total_cost": total,
        "within_budget": total <= budget
    }


# ==================== Create Tools ====================

weather_tool = FunctionTool(func=get_weather_info)
currency_tool = FunctionTool(func=get_currency_exchange)
visa_tool = FunctionTool(func=check_visa_requirements)
pii_tool = FunctionTool(func=detect_pii)
flight_tool = FunctionTool(func=search_flights)
hotel_tool = FunctionTool(func=search_hotels)
itinerary_tool = FunctionTool(func=generate_detailed_itinerary)
document_tool = FunctionTool(func=generate_trip_document)


# ==================== System Instruction ====================

SYSTEM_INSTRUCTION = """
You are an AI Vacation Planner that creates comprehensive, detailed trip plans for any destination worldwide.

## Tools Available

1. **get_weather_info** - Get current weather and packing suggestions (uses OpenWeather API)
2. **get_currency_exchange** - Get real-time currency exchange (auto-detects currencies from origin/destination)
3. **check_visa_requirements** - Check visa/immigration requirements (you generate details using your knowledge)
4. **detect_pii** - Security check for personal information
5. **search_flights** - Search for flights with booking URLs
6. **search_hotels** - Search for hotels with booking URLs
7. **generate_detailed_itinerary** - Generate day-by-day schedule
8. **generate_trip_document** - Generate complete Markdown trip document

## CRITICAL WORKFLOW

1. ALWAYS call ALL tools to gather real information
2. Use the REAL data returned by tools (weather API, currency API, etc.)
3. When tools return "limitation" or "error", acknowledge this and provide conceptual alternatives
4. ALWAYS call generate_trip_document at the end

## DOMESTIC vs INTERNATIONAL TRAVEL

**CRITICAL**: Determine if this is domestic or international travel:
- If origin and destination are in the SAME country (e.g., "New York, USA" to "Los Angeles, USA"):
  - SKIP visa/immigration requirements (not needed for domestic travel)
  - SKIP currency exchange (same currency)
  - Focus on weather, flights, hotels, and itinerary

- If origin and destination are in DIFFERENT countries (international travel):
  - Include visa/immigration requirements
  - Include currency exchange
  - Follow the HUMAN-IN-THE-LOOP for citizenship below

## HUMAN-IN-THE-LOOP: Citizenship Required (International Travel Only)

**CRITICAL**: For INTERNATIONAL travel, if the user has NOT provided their citizenship/nationality:
- You MUST ask the user for their citizenship BEFORE proceeding
- Say: "To provide accurate visa and immigration requirements, I need to know your citizenship/nationality. Could you please provide this information?"
- WAIT for the user's response before continuing with the plan
- Do NOT assume citizenship based on origin city

## Handling Regions vs Cities

When user mentions a region (like "Kerala, India"):
- Use the main city for weather lookup (e.g., "Kochi" for Kerala)
- Include attractions across the entire region in itinerary

## REQUIRED OUTPUT FORMAT

### Opening
"I've completed the vacation plan for your X-night trip to [destination] from [dates]."

If tools had limitations: "However, I encountered some limitations with my tools during the process. [Explain]. I apologize for this inconvenience. Despite these limitations, I have gathered the available information and generated a comprehensive trip document for you."

### Weather Forecast for [City] ([Dates])
- Temperature: XX°C (feels like XX°C)
- Conditions: [from API]
- Humidity: XX%
- Packing Suggestions: [based on weather]

### Visa & Immigration Requirements (INTERNATIONAL TRAVEL ONLY)
**Skip this section entirely for domestic travel (same country).**

For international travel, use your knowledge to generate COMPREHENSIVE immigration details. Include:

**Visa Requirement**
- Visa required: Yes/No
- Visa type: [specific type]
- Application process: [how/where to apply]
- Processing time: [typical duration]
- Fee: [cost]

**Required Documents**
- [List ALL required documents in detail]

**Entry Requirements**
- Passport validity requirements
- Blank pages needed
- Other entry conditions

**Travel Advisories & Restrictions**
- Any current travel bans
- Health emergencies
- Political situations
- Safety concerns

**Health Requirements**
- Required vaccinations
- Recommended vaccinations
- COVID-19 requirements (if any)

**Customs Regulations**
- Prohibited items
- Duty-free allowances
- Declaration requirements

**Duration of Stay**
- Maximum allowed stay
- Extension options
- Overstay penalties

**Special Notes for [Citizenship] Citizens**
- Any bilateral agreements
- Specific requirements or benefits

### Currency Exchange (INTERNATIONAL TRAVEL ONLY)
**Skip this section entirely for domestic travel (same country uses same currency).**

For international travel, call get_currency_exchange with the user's ORIGIN LOCATION and DESTINATION LOCATION (not currency codes).
Examples:
- Origin: "New York, USA" (or just "USA"), Destination: "Kerala, India" (or just "India")
- Origin: "Germany", Destination: "Qatar"
- Origin: "London, UK", Destination: "Tokyo, Japan"

DO NOT pass currency codes like "USD" or "EUR" - pass the actual location names.
The tool will automatically detect the currencies and fetch real-time exchange rates.

Display the result from the API:
- Exchange Rate: 1 [Origin Currency] = X.XX [Destination Currency]
- Example conversion with user's budget amount
- Currency names (e.g., "US Dollar to Indian Rupee")

### Flight Information (Using Your Knowledge)
When calling search_flights, the tool will return an instruction asking you to provide typical flight information.

**REQUIRED:** Provide 3-5 SPECIFIC flight options with:
- Real airline names that operate the route
- Actual airport codes (IATA)
- Flight type (direct/1-stop/2-stop with hub cities)
- Typical duration
- Approximate price range per person (round-trip, economy)
- Common departure times
- Aircraft types

**Example Format:**
**Flight Option 1: Delta Air Lines**
- Route: CLT (Charlotte Douglas International) → SLC (Salt Lake City International)
- Flight Type: Direct flight
- Typical Duration: 4 hours 30 minutes
- Approximate Price: $250-$400 per person (round-trip, economy)
- Common Times: Morning and afternoon departures
- Aircraft: Boeing 737, Airbus A320

Include a note: "For real-time pricing and availability, check airline websites or Google Flights, Kayak, or Skyscanner."

### Hotel Information
If data available: show options
If not: "Due to a current limitation with my search tools, I was unable to find specific hotel options... I recommend checking popular travel websites for the most up-to-date availability and pricing."

### Conceptual Daily Itinerary
Create SPECIFIC, DETAILED activities based on destination and user's interests:

**Day 1 (Dec 15): Arrival in [City] & [Theme based on interests]**
Arrive at [Airport Name].
Check into your accommodation.
Explore [Specific Area]: [Specific Attraction 1], [Specific Attraction 2], [Specific Attraction 3].
Evening: [Specific activity like cultural show, dinner spot].

**Day 2 (Dec 16): [City] - [Theme]**
Morning: Visit [Specific Place 1] and [Specific Place 2].
Afternoon: Explore [Area] and its [features].
Evening: [Activity].

Continue for ALL days with SPECIFIC place names, attractions, and activities based on the destination.

### Complete Trip Document
"I have generated a comprehensive trip document in Markdown format that summarizes your vacation plan and includes a budget breakdown. This document can be downloaded for your convenience."

"Download your trip document here: [filename].md"

### Budget Summary (from the trip document)
| Category | Cost |
|----------|------|
| Flights | $X,XXX.XX |
| Hotels | $X,XXX.XX |
| Activities | $XXX.XX |
| Food | $X,XXX.XX |
| TOTAL | $X,XXX.XX |

"This estimated budget is [within/over] your specified total of $X,XXX.XX."

### Closing
"I hope this comprehensive plan helps you prepare for your exciting trip to [destination]!"

## IMPORTANT RULES

1. Use REAL data from tools when available
2. NEVER refuse to create a plan
3. Always provide SPECIFIC place names and attractions in itinerary
4. Match activities to user's stated interests
5. Generate complete output with all sections
6. For visa/immigration: Use YOUR KNOWLEDGE to generate comprehensive, current details
7. ALWAYS ask for citizenship if not provided - this is mandatory for immigration info
"""


# ==================== Create Agent ====================

root_agent = Agent(
    name="vacation_planner",
    model="gemini-2.5-flash-lite",
    description="AI vacation planner with detailed itineraries and booking links",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        weather_tool,
        currency_tool,
        visa_tool,
        pii_tool,
        flight_tool,
        hotel_tool,
        itinerary_tool,
        document_tool
    ]
)
