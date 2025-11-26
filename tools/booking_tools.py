"""
Booking Tools - Flight, Hotel, and Car Rental search/estimation
Hybrid approach: Amadeus MCP (primary) → Tavily MCP (fallback)
"""

import os
import sys
from typing import Dict, Any
from pathlib import Path

# Add project root to path for MCP server imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import configuration
from config import Config

# Import Amadeus MCP servers
try:
    from mcp_servers.amadeus_hotels import search_hotels_amadeus_sync
    from mcp_servers.amadeus_flights import search_flights_amadeus_sync
    AMADEUS_AVAILABLE = True
except ImportError:
    AMADEUS_AVAILABLE = False
    print("[BOOKING_TOOLS] Warning: Amadeus MCP servers not available, using Tavily MCP fallback")

# Import Tavily MCP server
try:
    from mcp_servers.tavily_search import get_tavily_mcp
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("[BOOKING_TOOLS] Warning: Tavily MCP server not available")

# Check configuration flags
USE_AMADEUS_API = (
    Config.USE_AMADEUS_API and
    AMADEUS_AVAILABLE and
    not Config.FORCE_TAVILY_SEARCH and
    os.getenv("AMADEUS_CLIENT_ID") and
    os.getenv("AMADEUS_CLIENT_ID") != "your_amadeus_client_id"
)

print(f"[BOOKING_TOOLS] Configuration:")
print(f"  - USE_AMADEUS_API: {USE_AMADEUS_API}")
print(f"  - AMADEUS_ENV: {Config.AMADEUS_ENV}")
print(f"  - AUTO_DETECT_TEST_DATA: {Config.AUTO_DETECT_TEST_DATA}")
print(f"  - FORCE_TAVILY_SEARCH: {Config.FORCE_TAVILY_SEARCH}")
print(f"  - TAVILY_AVAILABLE: {TAVILY_AVAILABLE}")


def is_amadeus_test_data(data: Dict[str, Any]) -> bool:
    """
    Detect if Amadeus returned test/sandbox data.

    Test data indicators:
    - Booking URLs contain "amadeus.com/book"
    - Multiple options with identical prices
    - Test environment detected
    """
    if not data or not isinstance(data, dict):
        return True

    # Check if error in response
    if "error" in data:
        return True

    # Check flights for test data
    if "flights" in data:
        flights_data = data.get("flights")

        # Handle categorized flights (dict with budget/mid_range/premium)
        all_flights = []
        if isinstance(flights_data, dict):
            for category in ["budget", "mid_range", "premium"]:
                if category in flights_data:
                    all_flights.extend(flights_data[category])
        elif isinstance(flights_data, list):
            all_flights = flights_data
        else:
            return True  # Invalid structure

        if not all_flights:
            return True

        # Check for Amadeus test booking URLs
        for flight in all_flights:
            if not isinstance(flight, dict):
                continue
            url = flight.get("booking_url", "")
            if "amadeus.com/book" in url:
                print("[BOOKING_TOOLS] Detected Amadeus test data (test booking URL)")
                return True

        # Check if all prices are identical (common test data symptom)
        if len(all_flights) >= 2:
            prices = [f.get("price_per_person") for f in all_flights if isinstance(f, dict) and f.get("price_per_person")]
            if prices and len(set(prices)) == 1:
                print("[BOOKING_TOOLS] Detected Amadeus test data (identical prices)")
                return True

    # Check hotels for test data
    if "hotels" in data:
        hotels = data.get("hotels", [])
        if not hotels:
            return True

        # Check for test property names
        for hotel in hotels:
            name = hotel.get("name", "").lower()
            if "test" in name or "sample" in name or "demo" in name:
                print("[BOOKING_TOOLS] Detected Amadeus test data (test property name)")
                return True

    return False


def estimate_flight_cost(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int = 2,
    cabin_class: str = "economy"
) -> Dict[str, Any]:
    """
    Estimate flight costs using hybrid approach:
    1. Try Amadeus MCP (if enabled and not test environment)
    2. Detect test data and fallback to Tavily MCP
    3. Final fallback to LLM knowledge

    Args:
        origin: Departure city/airport
        destination: Arrival city/airport
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        travelers: Number of travelers
        cabin_class: Cabin class (economy/premium/business/first)

    Returns:
        Flight cost estimation with 3 specific airline options
    """
    print(f"[FLIGHTS] Searching: {origin} → {destination} ({departure_date} to {return_date})")

    # Step 1: Try Amadeus API first if enabled
    amadeus_data = None
    if USE_AMADEUS_API and not Config.FORCE_TAVILY_SEARCH:
        print(f"[FLIGHTS] Attempting Amadeus API ({Config.AMADEUS_ENV} environment)...")
        try:
            amadeus_result = search_flights_amadeus_sync(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                travelers=travelers
            )

            # Validate result type
            if not isinstance(amadeus_result, dict):
                print(f"[FLIGHTS] Amadeus returned invalid type: {type(amadeus_result)}, falling back to Tavily MCP")
                amadeus_result = {"error": "Invalid response type"}

            # Check if valid data received
            if "error" not in amadeus_result and "flights" in amadeus_result:
                amadeus_data = {
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

                # Step 2: Detect test data
                if Config.AUTO_DETECT_TEST_DATA and is_amadeus_test_data(amadeus_data):
                    print("[FLIGHTS] Amadeus test data detected, using Tavily MCP fallback")
                    amadeus_data = None  # Trigger Tavily fallback
                else:
                    print(f"[FLIGHTS] Using Amadeus production data")
                    return amadeus_data

        except Exception as e:
            print(f"[FLIGHTS] Amadeus API error: {e}, falling back to Tavily MCP")

    # Step 3: Fallback to Tavily MCP if available
    if TAVILY_AVAILABLE and (amadeus_data is None or Config.FORCE_TAVILY_SEARCH):
        print("[FLIGHTS] Using Tavily MCP for flight search...")
        try:
            tavily_mcp = get_tavily_mcp()
            tavily_result = tavily_mcp.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=travelers,
                cabin_class=cabin_class
            )

            if "error" not in tavily_result:
                print("[FLIGHTS] Tavily MCP search successful")
                return {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date,
                    "return_date": return_date,
                    "travelers": travelers,
                    "cabin_class": cabin_class,
                    "source": "tavily_mcp",
                    "search_results": tavily_result.get("results", []),
                    "llm_instruction": tavily_result.get("llm_instruction", "")
                }
            else:
                print(f"[FLIGHTS] Tavily MCP error: {tavily_result.get('message', 'Unknown error')}")

        except Exception as e:
            print(f"[FLIGHTS] Tavily MCP error: {e}, falling back to LLM knowledge")

    # Step 4: Final fallback to LLM knowledge
    print("[FLIGHTS] Using LLM knowledge fallback")
    return {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers,
        "cabin_class": cabin_class,
        "source": "llm_knowledge",
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
            from loguru import logger
            logger.info(f"[AMADEUS] Attempting to fetch real hotel data for {destination}")

            amadeus_result = search_hotels_amadeus_sync(
                destination=destination,
                check_in=checkin_date,
                check_out=checkout_date,
                guests=travelers,
                rooms=1 if travelers <= 2 else 2
            )

            if "error" not in amadeus_result and "hotels" in amadeus_result:
                logger.info(f"[AMADEUS] Successfully retrieved {len(amadeus_result.get('hotels', {}).get('budget', []))} hotels")
                return {
                    "destination": destination,
                    "checkin_date": checkin_date,
                    "checkout_date": checkout_date,
                    "nights": nights,
                    "travelers": travelers,
                    "hotel_class": hotel_class,
                    "source": "amadeus_api",
                    "hotels": amadeus_result["hotels"],
                    "city_info": amadeus_result.get("city_info", {}),
                    "note": "✅ Real hotel data from Amadeus API with booking links"
                }
            else:
                logger.warning(f"[AMADEUS] API returned error or no hotels: {amadeus_result.get('error', 'Unknown')}")
        except Exception as e:
            from loguru import logger
            logger.error(f"[AMADEUS] API error, falling back to Tavily MCP: {e}")

    # Step 2: Fallback to Tavily MCP web search
    if TAVILY_AVAILABLE:
        try:
            print(f"[HOTELS] Using Tavily MCP for hotel search in {destination}...")
            tavily_mcp = get_tavily_mcp()

            tavily_result = tavily_mcp.search_hotels(
                destination=destination,
                checkin=checkin_date,
                checkout=checkout_date,
                guests=travelers,
                hotel_class=hotel_class
            )

            if "error" not in tavily_result:
                print("[HOTELS] Tavily MCP search successful")
                return {
                    "destination": destination,
                    "checkin_date": checkin_date,
                    "checkout_date": checkout_date,
                    "nights": nights,
                    "travelers": travelers,
                    "hotel_class": hotel_class,
                    "source": "tavily_mcp",
                    "search_results": tavily_result.get("results", []),
                    "llm_instruction": tavily_result.get("llm_instruction", ""),
                    "note": "✅ Real hotel search results from Booking.com, Hotels.com, Expedia via Tavily"
                }
            else:
                print(f"[HOTELS] Tavily MCP error: {tavily_result.get('message')}, falling back to LLM")
        except Exception as e:
            print(f"[HOTELS] Tavily MCP error: {e}, falling back to LLM knowledge")

    # Step 3: Final fallback to LLM with detailed instructions
    print("[HOTELS] Using LLM knowledge fallback")
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
    Estimate car rental costs using Tavily MCP → LLM fallback.

    Args:
        destination: Rental location
        pickup_date: Pickup date (YYYY-MM-DD)
        dropoff_date: Drop-off date (YYYY-MM-DD)
        car_type: Car type (economy/compact/midsize/suv/luxury)

    Returns:
        Car rental cost estimation with Tavily search results or LLM instruction
    """
    # Calculate rental days
    try:
        from datetime import datetime
        pickup_dt = datetime.strptime(pickup_date, "%Y-%m-%d")
        dropoff_dt = datetime.strptime(dropoff_date, "%Y-%m-%d")
        rental_days = (dropoff_dt - pickup_dt).days
    except:
        rental_days = 5  # Default

    # Step 1: Try Tavily MCP web search first
    if TAVILY_AVAILABLE:
        try:
            print(f"[CAR_RENTAL] Using Tavily MCP for car rental search in {destination}...")
            tavily_mcp = get_tavily_mcp()

            tavily_result = tavily_mcp.search_car_rentals(
                pickup_location=destination,
                dropoff_location=destination,  # Same location for now
                pickup_date=pickup_date,
                dropoff_date=dropoff_date,
                car_type=car_type
            )

            if "error" not in tavily_result:
                print("[CAR_RENTAL] Tavily MCP search successful")
                return {
                    "destination": destination,
                    "pickup_date": pickup_date,
                    "dropoff_date": dropoff_date,
                    "rental_days": rental_days,
                    "car_type": car_type,
                    "source": "tavily_mcp",
                    "search_results": tavily_result.get("results", []),
                    "llm_instruction": tavily_result.get("llm_instruction", ""),
                    "note": "✅ Real car rental search results from Kayak, Rentalcars.com, Enterprise, Budget via Tavily"
                }
            else:
                print(f"[CAR_RENTAL] Tavily MCP error: {tavily_result.get('message')}, falling back to LLM")
        except Exception as e:
            print(f"[CAR_RENTAL] Tavily MCP error: {e}, falling back to LLM knowledge")

    # Step 2: Fallback to LLM knowledge with detailed instructions
    print("[CAR_RENTAL] Using LLM knowledge fallback")
    return {
        "destination": destination,
        "pickup_date": pickup_date,
        "dropoff_date": dropoff_date,
        "car_type": car_type,
        "source": "llm_knowledge",
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
