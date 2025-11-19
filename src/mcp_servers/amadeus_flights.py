"""
Amadeus Flights MCP Server
Real-time flight search with booking links
"""

import asyncio
from typing import Dict, Any
from .amadeus_client import AmadeusClient


async def search_flights_amadeus(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int = 2
) -> Dict[str, Any]:
    """
    Search for real flights using Amadeus API

    Args:
        origin: Origin city name (e.g., "New York")
        destination: Destination city name (e.g., "Paris")
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        travelers: Number of travelers

    Returns:
        Flight options organized by category with booking links
    """
    client = AmadeusClient()

    # Get airport codes
    origin_code = await client.get_airport_code(origin)
    dest_code = await client.get_airport_code(destination)

    # Search flights
    result = await client.search_flights(
        origin=origin_code,
        destination=dest_code,
        departure_date=departure_date,
        return_date=return_date,
        adults=travelers,
        max_results=15
    )

    if "error" in result:
        return result

    # Parse and categorize results
    flights = result.get("data", [])
    if not flights:
        return {"error": "No flights found", "route": f"{origin_code}-{dest_code}"}

    # Sort by price
    flights.sort(key=lambda x: float(x["price"]["total"]))

    # Categorize into budget, mid-range, premium
    categorized = {
        "budget": [],
        "mid_range": [],
        "premium": []
    }

    for i, flight in enumerate(flights):
        parsed = _parse_flight(flight, travelers)

        if i < 3:
            categorized["budget"].append(parsed)
        elif i < 6:
            categorized["mid_range"].append(parsed)
        else:
            categorized["premium"].append(parsed)

        if len(categorized["premium"]) >= 3:
            break

    return {
        "route": f"{origin_code}-{dest_code}",
        "departure_date": departure_date,
        "return_date": return_date,
        "travelers": travelers,
        "flights": categorized,
        "source": "amadeus_api"
    }


def _parse_flight(flight: Dict, travelers: int) -> Dict[str, Any]:
    """Parse Amadeus flight offer into readable format"""
    price = float(flight["price"]["total"])
    segments = flight["itineraries"][0]["segments"]

    # Get first segment info
    first_seg = segments[0]
    last_seg = segments[-1]

    carrier_codes = {
        "AA": "American Airlines",
        "DL": "Delta Air Lines",
        "UA": "United Airlines",
        "AF": "Air France",
        "BA": "British Airways",
        "LH": "Lufthansa",
        "EK": "Emirates",
        "QR": "Qatar Airways"
    }

    carrier = first_seg["carrierCode"]
    airline = carrier_codes.get(carrier, carrier)

    # Calculate duration
    duration = flight["itineraries"][0]["duration"]
    # Parse ISO duration (PT7H30M)
    hours = 0
    minutes = 0
    if "H" in duration:
        hours = int(duration.split("H")[0].replace("PT", ""))
        if "M" in duration:
            minutes = int(duration.split("H")[1].replace("M", ""))
    elif "M" in duration:
        minutes = int(duration.replace("PT", "").replace("M", ""))

    return {
        "airline": airline,
        "flight_number": f"{carrier}{first_seg['number']}",
        "departure": first_seg["departure"]["at"].split("T")[1][:5],
        "arrival": last_seg["arrival"]["at"].split("T")[1][:5],
        "duration": f"{hours}h {minutes}m",
        "stops": len(segments) - 1,
        "price_per_person": round(price / travelers, 2),
        "total_price": round(price, 2),
        "cabin_class": flight["travelerPricings"][0]["fareDetailsBySegment"][0]["cabin"],
        "booking_url": f"https://www.amadeus.com/book?offer={flight['id']}"
    }


# Synchronous wrapper for non-async contexts
def search_flights_amadeus_sync(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str,
    travelers: int = 2
) -> Dict[str, Any]:
    """Synchronous version of search_flights_amadeus"""
    return asyncio.run(search_flights_amadeus(
        origin, destination, departure_date, return_date, travelers
    ))
