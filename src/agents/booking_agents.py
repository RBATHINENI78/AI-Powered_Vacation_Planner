"""
Booking Agents - Flight, Hotel, and Car Rental Agents
Designed for parallel execution in booking phase
Uses LLM knowledge for flights and Amadeus API for hotels
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from loguru import logger
from .base_agent import BaseAgent

# Import MCP servers for real API calls
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_servers.amadeus_hotels import search_hotels_amadeus_sync

# Flag to use real API or mock data
USE_REAL_API = os.getenv("AMADEUS_CLIENT_ID") and os.getenv("AMADEUS_CLIENT_ID") != "your_amadeus_client_id"


class FlightBookingAgent(BaseAgent):
    """
    Flight Booking Agent using LLM knowledge for flight information.
    Designed for parallel execution with other booking agents.
    """

    def __init__(self):
        super().__init__(
            name="flight_booking",
            description="Provides flight information using LLM knowledge"
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide flight information using LLM knowledge.

        Args:
            input_data: Contains origin, destination, dates, travelers

        Returns:
            Structured data for LLM to generate flight information
        """
        origin = input_data.get("origin", "")
        destination = input_data.get("destination", "")
        departure_date = input_data.get("departure_date", "")
        return_date = input_data.get("return_date", "")
        travelers = input_data.get("travelers", 1)
        cabin_class = input_data.get("cabin_class", "economy")

        # Get LLM-powered flight information
        flight_info = self._search_flights_llm(
            origin, destination, departure_date, return_date, travelers, cabin_class
        )

        return {
            "status": "success",
            "search_params": {
                "origin": origin,
                "destination": destination,
                "departure": departure_date,
                "return": return_date,
                "travelers": travelers,
                "class": cabin_class
            },
            "flight_info": flight_info,
            "booking_tips": self._get_booking_tips()
        }

    def _search_flights_llm(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str,
        travelers: int,
        cabin_class: str = "economy"
    ) -> Dict[str, Any]:
        """
        Provide LLM-powered flight information.

        Returns structured data for LLM to generate typical flight details.
        """
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "travelers": travelers,
            "cabin_class": cabin_class,
            "instruction_for_llm": f"""Using your knowledge of airlines, routes, and airports, provide SPECIFIC flight information for {origin} to {destination}:

**REQUIRED FORMAT - Provide 3-5 specific flight options like this:**

**Flight Option 1: [Specific Airline Name]**
- Route: [Origin Airport Code-Airport Name] → [Destination Airport Code-Airport Name]
- Flight Type: Direct / 1 stop via [Hub City] / 2 stops
- Typical Duration: X hours XX minutes
- Approximate Price: $XXX-$XXX per person ({cabin_class} class, round-trip)
- Common Departure Times: Morning (6am-12pm) / Afternoon (12pm-6pm) / Evening (6pm-12am)
- Aircraft Type: [Common aircraft on this route]
- Baggage: [Typical baggage allowance]

**Flight Option 2:** [Continue with different airline...]

**IMPORTANT:**
- Use REAL airline names that actually operate this route
- Use correct IATA airport codes (e.g., JFK for New York, LAX for Los Angeles)
- Be specific about typical hub cities for connections
- Provide realistic price ranges based on route distance and typical fares for {cabin_class} class
- Include both direct flights AND connection options if applicable
- Mention if certain airlines have better schedules or pricing for this route
- Consider {travelers} travelers in pricing
- Reference departure date: {departure_date} and return date: {return_date}

**Booking Recommendation:**
Include a note: "For real-time pricing and availability, check airline websites or Google Flights, Kayak, or Skyscanner."

Do NOT say "I cannot provide" or "due to limitations" - use your knowledge to provide helpful, accurate typical flight information."""
        }

    def _get_booking_tips(self) -> List[str]:
        """Get flight booking tips."""
        return [
            "Book 6-8 weeks in advance for best prices",
            "Tuesday and Wednesday usually have lower fares",
            "Check nearby airports for better deals",
            "Set price alerts for your route"
        ]


class HotelBookingAgent(BaseAgent):
    """
    Hotel Booking Agent using Amadeus API for real hotel data.
    Designed for parallel execution with other booking agents.
    """

    def __init__(self):
        super().__init__(
            name="hotel_booking",
            description="Searches hotels using Amadeus API"
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for hotel options using Amadeus API.

        Args:
            input_data: Contains destination, dates, guests, preferences

        Returns:
            List of hotel options from Amadeus API or fallback data
        """
        destination = input_data.get("destination", "")
        check_in = input_data.get("check_in", "")
        check_out = input_data.get("check_out", "")
        guests = input_data.get("guests", 2)
        rooms = input_data.get("rooms", 1)

        # Try real Amadeus API first if credentials are available
        if USE_REAL_API:
            try:
                logger.info(f"Calling Amadeus hotel API: {destination}, {check_in} to {check_out}, {guests} guests, {rooms} rooms")
                result = search_hotels_amadeus_sync(destination, check_in, check_out, guests, rooms)
                logger.info(f"Amadeus hotel API response keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
                if "error" not in result:
                    logger.info(f"Amadeus hotel API success!")
                    return {
                        "status": "success",
                        "source": "amadeus_api",
                        "search_params": {
                            "destination": destination,
                            "check_in": check_in,
                            "check_out": check_out,
                            "guests": guests,
                            "rooms": rooms
                        },
                        "hotels": result.get("hotels", {}),
                        "booking_tips": self._get_booking_tips()
                    }
                else:
                    logger.error(f"Amadeus hotel API error: {result}")
            except Exception as e:
                logger.error(f"Amadeus hotel API exception: {str(e)}")

        # Fall back to LLM-powered hotel information
        logger.info("Using LLM-powered hotel information (Amadeus API not available)")
        hotel_info = self._get_hotels_llm(destination, check_in, check_out, guests, rooms)

        return {
            "status": "success",
            "source": "llm_knowledge",
            "search_params": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms
            },
            "hotel_info": hotel_info,
            "booking_tips": self._get_booking_tips()
        }

    def _get_hotels_llm(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int,
        rooms: int
    ) -> Dict[str, Any]:
        """
        Provide LLM-powered hotel information as fallback.

        Returns structured data for LLM to generate hotel recommendations.
        """
        try:
            d1 = datetime.strptime(check_in, "%Y-%m-%d")
            d2 = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (d2 - d1).days
        except (ValueError, TypeError):
            nights = 7

        return {
            "destination": destination,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "guests": guests,
            "rooms": rooms,
            "instruction_for_llm": f"""Since real-time hotel data is not available, provide REALISTIC hotel recommendations for {destination} based on your knowledge:

**REQUIRED: Provide 3-4 hotel options in each category (Budget, Mid-Range, Luxury):**

**Budget Hotels (under $100/night):**
For each hotel include:
- Hotel name (real chain or typical name for the area)
- Location/neighborhood in {destination}
- Star rating (2-3 stars)
- Typical price per night
- Total for {nights} nights, {rooms} room(s)
- Amenities
- Cancellation policy
- How to book (Booking.com, Hotels.com, direct, etc.)

**Mid-Range Hotels ($100-250/night):**
[Same format as above, 3-4 stars]

**Luxury Hotels (over $250/night):**
[Same format as above, 4-5 stars]

**IMPORTANT:**
- Use REAL hotel names or chains that actually operate in {destination}
- Provide realistic prices based on {destination}'s typical hotel costs
- Include specific neighborhoods/areas in {destination}
- Consider dates: {check_in} to {check_out}
- Calculate total cost for {nights} nights and {rooms} room(s)
- Include typical amenities for each category
- Provide practical booking recommendations

**Note to user:**
"These are typical hotel options for {destination}. For real-time availability and booking, please check Booking.com, Hotels.com, Expedia, or the hotel's direct website."

Do NOT say "I cannot provide" - use your knowledge of typical hotels in {destination}."""
        }

    def _get_booking_tips(self) -> List[str]:
        """Get hotel booking tips."""
        return [
            "Book directly with hotel for potential upgrades",
            "Check for package deals (flight + hotel)",
            "Read recent reviews for current conditions",
            "Consider location vs. price trade-offs"
        ]


class CarRentalAgent(BaseAgent):
    """
    Car Rental Agent for searching vehicle rentals.
    Designed for parallel execution with other booking agents.
    """

    def __init__(self):
        super().__init__(
            name="car_rental",
            description="Searches car rental options"
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for car rental options.

        Args:
            input_data: Contains location, dates, preferences

        Returns:
            List of rental options
        """
        pickup_location = input_data.get("pickup_location", "")
        pickup_date = input_data.get("pickup_date", "")
        return_date = input_data.get("return_date", "")
        car_type = input_data.get("car_type", "compact")

        # Check if car rental is needed
        if not input_data.get("needs_car", True):
            return {
                "status": "success",
                "message": "Car rental not required for this trip",
                "alternatives": [
                    "Public transportation",
                    "Ride-sharing apps",
                    "Taxis"
                ]
            }

        # Simulate car rental search
        rentals = self._search_rentals(
            pickup_location, pickup_date, return_date, car_type
        )

        # Sort by price
        rentals.sort(key=lambda x: x["total_price"])

        return {
            "status": "success",
            "search_params": {
                "location": pickup_location,
                "pickup": pickup_date,
                "return": return_date,
                "type": car_type
            },
            "results_count": len(rentals),
            "rentals": rentals,
            "recommended": rentals[0] if rentals else None,
            "booking_tips": self._get_booking_tips()
        }

    def _search_rentals(
        self,
        location: str,
        pickup: str,
        return_date: str,
        car_type: str
    ) -> List[Dict[str, Any]]:
        """Simulate car rental search results."""
        companies = ["Hertz", "Avis", "Enterprise", "Budget", "Europcar"]

        car_types = {
            "economy": {"name": "Economy", "base": 30, "passengers": 4},
            "compact": {"name": "Compact", "base": 40, "passengers": 5},
            "midsize": {"name": "Midsize", "base": 50, "passengers": 5},
            "suv": {"name": "SUV", "base": 70, "passengers": 7},
            "luxury": {"name": "Luxury", "base": 100, "passengers": 5}
        }

        # Calculate days
        try:
            d1 = datetime.strptime(pickup, "%Y-%m-%d")
            d2 = datetime.strptime(return_date, "%Y-%m-%d")
            days = (d2 - d1).days
        except (ValueError, TypeError):
            days = 7

        car_info = car_types.get(car_type, car_types["compact"])
        rentals = []

        for company in random.sample(companies, min(4, len(companies))):
            daily_rate = car_info["base"] * random.uniform(0.85, 1.15)
            total = daily_rate * days

            rental = {
                "company": company,
                "car_type": car_info["name"],
                "example_car": f"{random.choice(['Toyota', 'Honda', 'Ford', 'VW'])} {random.choice(['Corolla', 'Civic', 'Focus', 'Golf'])}",
                "passengers": car_info["passengers"],
                "daily_rate": round(daily_rate, 2),
                "total_price": round(total, 2),
                "days": days,
                "features": ["AC", "Automatic", "GPS"] + (["Bluetooth"] if random.random() > 0.5 else []),
                "insurance": random.choice(["Basic included", "Full coverage available"]),
                "mileage": random.choice(["Unlimited", "Limited (200km/day)"])
            }
            rentals.append(rental)

        return rentals

    def _get_booking_tips(self) -> List[str]:
        """Get car rental tips."""
        return [
            "Book in advance for better rates",
            "Check if you need international driving permit",
            "Review insurance options carefully",
            "Take photos of car before and after"
        ]
