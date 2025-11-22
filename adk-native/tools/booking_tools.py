"""
Booking Tools - Flight, Hotel, and Car Rental search/estimation
Uses LLM knowledge for flights and Amadeus API for real hotel data
"""

import os
import sys
from typing import Dict, Any
from pathlib import Path

# Add project root to path for MCP server imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Amadeus MCP servers
try:
    from mcp_servers.amadeus_hotels import search_hotels_amadeus_sync
    from mcp_servers.amadeus_flights import search_flights_amadeus_sync
    AMADEUS_AVAILABLE = True
except ImportError:
    AMADEUS_AVAILABLE = False
    print("Warning: Amadeus MCP servers not available, falling back to LLM estimates")

# Check if Amadeus API credentials are configured
USE_AMADEUS_API = AMADEUS_AVAILABLE and os.getenv("AMADEUS_CLIENT_ID") and os.getenv("AMADEUS_CLIENT_ID") != "your_amadeus_client_id"


def estimate_flight_cost(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int = 2,
    cabin_class: str = "economy"
) -> Dict[str, Any]:
    """
    Estimate flight costs using LLM knowledge with SPECIFIC airline recommendations.

    Args:
        origin: Departure city/airport
        destination: Arrival city/airport
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        travelers: Number of travelers
        cabin_class: Cabin class (economy/premium/business/first)

    Returns:
        Flight cost estimation with 3-5 specific airline options
    """
    # Try Amadeus API first if available
    if USE_AMADEUS_API:
        try:
            amadeus_result = search_flights_amadeus_sync(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                travelers=travelers
            )
            if "error" not in amadeus_result and "flights" in amadeus_result:
                return {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "travelers": travelers,
                    "cabin_class": cabin_class,
                    "source": "amadeus_api",
                    "flights": amadeus_result["flights"],
                    "route": amadeus_result.get("route", ""),
                    "origin_airport": amadeus_result.get("origin_airport", {}),
                    "destination_airport": amadeus_result.get("destination_airport", {})
                }
        except Exception as e:
            print(f"Amadeus API error, falling back to LLM: {e}")

    # Fallback to LLM with detailed instructions for specific airlines
    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers,
        "cabin_class": cabin_class,
        "llm_instruction": f"""Using your knowledge of airlines, routes, and airports, provide SPECIFIC flight information for {origin} to {destination}:

**REQUIRED FORMAT - Provide 3-5 specific flight options like this:**

**Flight Option 1: [Specific Airline Name]**
- Route: [Origin Airport Code-Airport Name] → [Destination Airport Code-Airport Name]
  Example: CLT (Charlotte Douglas International Airport) → SLC (Salt Lake City International Airport)
- Flight Type: Direct / 1 stop via [Hub City] / 2 stops
- Typical Duration: X hours XX minutes
- Approximate Price: $XXX-$XXX per person ({cabin_class} class, round-trip)
- Common Departure Times: Morning (6am-12pm) / Afternoon (12pm-6pm) / Evening (6pm-12am)
- Aircraft Type: [Common aircraft on this route - e.g., Boeing 737, Airbus A320]
- Baggage: [Typical baggage allowance - e.g., "1 personal item + 1 carry-on included. Checked bags typically $30-$40 each."]

**Flight Option 2:** [Continue with different airline...]

**Flight Option 3:** [Continue with third airline option...]

**IMPORTANT INSTRUCTIONS:**
- Use REAL airline names that actually operate between {origin} and {destination}
- Use correct IATA airport codes (e.g., JFK for New York, LAX for Los Angeles, CLT for Charlotte, SLC for Salt Lake City)
- Be specific about typical hub cities for connections (e.g., ATL for Delta, DFW for American, DEN for United)
- Provide realistic price ranges based on route distance and typical fares for {cabin_class} class
- Include BOTH direct flights (if available) AND connection options
- Mention which airlines have better schedules or pricing for this specific route
- Consider {travelers} travelers in total pricing
- Reference departure date: {departure_date} and return date: {return_date}
- For each option, specify the connecting city if it's not a direct flight

**Example for Charlotte to Salt Lake City:**
- Delta Air Lines via ATL (Hartsfield-Jackson Atlanta International Airport)
- American Airlines via DFW (Dallas/Fort Worth International Airport)
- United Airlines via DEN (Denver International Airport)

**Booking Recommendation:**
Include: "For real-time pricing and availability, check airline websites or Google Flights, Kayak, or Skyscanner."

**DO NOT:**
- Say "I cannot provide" or "due to limitations"
- Give generic answers without specific airlines
- Skip airport codes or hub cities
- Provide vague price ranges

**DO:**
- Use your knowledge to provide helpful, accurate typical flight information
- Name specific airlines that operate this route
- Include realistic pricing for the route distance and {cabin_class} class
- Specify common aircraft types used on this route"""
    }


def estimate_hotel_cost(
    destination: str,
    checkin_date: str,
    checkout_date: str,
    travelers: int = 2,
    hotel_class: str = "3-star"
) -> Dict[str, Any]:
    """
    Search for hotels using Amadeus API (if available) or LLM estimation.

    Args:
        destination: Destination city
        checkin_date: Check-in date (YYYY-MM-DD)
        checkout_date: Check-out date (YYYY-MM-DD)
        travelers: Number of travelers
        hotel_class: Hotel class (budget/3-star/4-star/5-star/luxury)

    Returns:
        Hotel options with booking links (Amadeus API) or cost estimation (LLM)
    """
    # Calculate nights
    from datetime import datetime
    try:
        d1 = datetime.strptime(checkin_date, "%Y-%m-%d")
        d2 = datetime.strptime(checkout_date, "%Y-%m-%d")
        nights = (d2 - d1).days
    except:
        nights = 7

    # Try Amadeus API first if available
    if USE_AMADEUS_API:
        try:
            amadeus_result = search_hotels_amadeus_sync(
                destination=destination,
                check_in=checkin_date,
                check_out=checkout_date,
                guests=travelers,
                rooms=1 if travelers <= 2 else 2
            )
            if "error" not in amadeus_result and "hotels" in amadeus_result:
                return {
                    "destination": destination,
                    "checkin_date": checkin_date,
                    "checkout_date": checkout_date,
                    "nights": nights,
                    "travelers": travelers,
                    "hotel_class": hotel_class,
                    "source": "amadeus_api",
                    "hotels": amadeus_result["hotels"],
                    "city_info": amadeus_result.get("city_info", {})
                }
        except Exception as e:
            print(f"Amadeus API error, falling back to LLM: {e}")

    # Fallback to LLM with detailed instructions
    return {
        "destination": destination,
        "checkin_date": checkin_date,
        "checkout_date": checkout_date,
        "nights": nights,
        "travelers": travelers,
        "hotel_class": hotel_class,
        "llm_instruction": f"""Provide SPECIFIC hotel recommendations in {destination} for {travelers} travelers from {checkin_date} to {checkout_date} ({nights} nights).

**REQUIRED FORMAT - Provide 3-5 specific hotel options:**

**Hotel Option 1: [Specific Hotel Name]**
- Description: [Brief description of the hotel and its amenities]
- Location: [Specific neighborhood or area in {destination}]
- Price: $XXX per night (Total: $XXX for {nights} nights)
- Features:
  * [List key amenities like: Free WiFi, Breakfast included, Pool, Gym, Kitchen, etc.]
- Best For: [Type of traveler - e.g., Business, Families, Budget, Luxury]
- Booking: [Suggest booking site or mention if part of a chain]

**Hotel Option 2:** [Continue with different hotel...]

**Hotel Option 3:** [Continue with third option...]

**IMPORTANT INSTRUCTIONS:**
- Use REAL hotel names or chains that exist in {destination}
- For extended stays ({nights} nights), recommend hotels with kitchenettes or serviced apartments
- Provide realistic per-night and total costs for {hotel_class} level
- Specify the neighborhood/area (e.g., "Downtown", "Near Airport", specific district names)
- Include practical amenities that matter for {nights}-night stays
- Suggest hotels at different price points (budget, mid-range, luxury)
- For long stays, mention if the hotel offers weekly/monthly rates or discounts

**Example Format for Extended Stays:**
"Residence Inn by Marriott [City] Downtown - $154.49/night. Apartment-style suites with full kitchen, good for month-long stays to save on food costs."

**Booking Tips:**
- For extended stays, contact hotel directly for long-term discounts
- Look for hotels with complimentary breakfast
- Consider apartments with kitchens for longer stays
- Check cancellation policies

**DO NOT:**
- Give generic "Hotel A, Hotel B" names
- Provide vague price ranges without specifics
- Skip neighborhood information

**DO:**
- Name real hotels or hotel chains
- Provide specific nightly and total costs
- Mention if breakfast or other meals are included
- Highlight features useful for {nights}-night stays"""
    }


def estimate_car_rental_cost(
    destination: str,
    pickup_date: str,
    dropoff_date: str,
    car_type: str = "compact"
) -> Dict[str, Any]:
    """
    Estimate car rental costs using LLM knowledge.

    Args:
        destination: Rental location
        pickup_date: Pickup date (YYYY-MM-DD)
        dropoff_date: Drop-off date (YYYY-MM-DD)
        car_type: Car type (economy/compact/midsize/suv/luxury)

    Returns:
        Car rental cost estimation via LLM instruction
    """
    return {
        "destination": destination,
        "pickup_date": pickup_date,
        "dropoff_date": dropoff_date,
        "car_type": car_type,
        "llm_instruction": f"""Estimate car rental costs in {destination} from {pickup_date} to {dropoff_date} for a {car_type} vehicle.

**Car Rental Cost Estimation:**

**Rental Analysis:**
- Rental duration: Calculate days
- Car type: {car_type}
- Location: {destination}

**Cost Breakdown:**

1. **Daily Rates** ({car_type})
   - Economy: $XX-XX per day
   - {car_type.title()}: $XX-XX per day
   - SUV/Luxury: $XX-XX per day

2. **Total Rental Cost:**
   - Base rate (days × daily rate)
   - Insurance options:
     * Basic (included)
     * Full coverage (+$15-30/day)
   - Additional fees:
     * Airport pickup fee
     * Young driver fee (if under 25)
     * Additional driver fee
     * GPS rental
   - Taxes (~10-20%)

3. **Fuel Policy:**
   - Full-to-full (recommended)
   - Prepaid fuel option
   - Estimated fuel cost for typical usage

4. **Rental Companies:**
   - International chains (Hertz, Enterprise, Budget)
   - Local companies (often cheaper)
   - Best value in {destination}

5. **Driving Considerations in {destination}:**
   - Do you need a car? (public transport alternative)
   - International Driving Permit required?
   - Parking costs and availability
   - Traffic and road conditions
   - Toll roads
   - Speed limits and traffic rules

**Recommendation:**
- Is renting a car recommended for {destination}?
- Alternative: Uber/Taxi daily cost comparison

**Estimated Total:** Provide realistic range including insurance and fees for {car_type} in {destination}."""
    }


def search_activities(destination: str, interests: list = None) -> Dict[str, Any]:
    """
    Search for activities and attractions at a destination.

    Args:
        destination: Destination city/country
        interests: List of interests (culture, adventure, food, etc.)

    Returns:
        Activities recommendations via LLM instruction
    """
    interests_str = ", ".join(interests) if interests else "general sightseeing"

    return {
        "destination": destination,
        "interests": interests_str,
        "llm_instruction": f"""Recommend activities and attractions in {destination} based on interests: {interests_str}.

**Activities & Attractions in {destination}:**

**1. Must-See Attractions:**
- Top 5 iconic landmarks/sites
- Estimated cost for each
- Time needed for visit
- Best time to visit (avoid crowds)

**2. {interests_str.title()} Activities:**
Specific to the stated interests:
- Recommended tours/experiences
- Cost range
- Duration
- Booking requirements

**3. Day Trip Options:**
- Nearby cities/attractions worth visiting
- Transportation options
- Estimated costs
- Full-day vs half-day options

**4. Free/Budget Activities:**
- Parks and gardens
- Walking tours
- Free museums/galleries
- Local markets
- Viewpoints

**5. Food & Dining Experiences:**
- Must-try local dishes
- Recommended restaurants (budget to fine dining)
- Food tours available
- Street food areas

**6. Evening/Nightlife:**
- Entertainment options
- Cultural shows
- Bars/clubs (if interested)
- Night markets

**7. Booking Information:**
- Which attractions need advance booking
- Skip-the-line tickets worth buying
- City passes/tourist cards value analysis
- Guided tours vs self-guided

**Estimated Activity Budget:**
Provide daily budget for activities (low/medium/high) to help travelers plan.

Tailor recommendations to {interests_str} preferences."""
    }
