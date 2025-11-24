"""
Amadeus Hotels MCP Server
Real-time hotel search with booking links
"""

import asyncio
from typing import Dict, Any
from .amadeus_client import AmadeusClient


async def search_hotels_amadeus(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1
) -> Dict[str, Any]:
    """
    Search for real hotels using Amadeus API

    Args:
        destination: City name (e.g., "Paris")
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        rooms: Number of rooms

    Returns:
        Hotel options organized by category with booking links
    """
    client = AmadeusClient()

    # Get city code dynamically from Amadeus API
    city_info = await client.get_city_code(destination)

    # Check if city code was found
    if not city_info.get("code"):
        return {
            "error": f"Could not find city code for: {destination}",
            "details": city_info.get("error", "Unknown error"),
            "suggestion": "Please specify a major city name"
        }

    city_code = city_info["code"]

    # Search hotels
    result = await client.search_hotels(
        city_code=city_code,
        check_in=check_in,
        check_out=check_out,
        adults=guests,
        rooms=rooms,
        max_results=15
    )

    if "error" in result:
        return result

    # Add city info to result
    result["city_info"] = city_info

    # Parse and categorize results
    hotels = result.get("data", [])
    if not hotels:
        return {
            "error": f"No hotels found in Amadeus test environment for {destination}",
            "destination": destination,
            "city_info": city_info,
            "note": "The Amadeus test API has limited sample data. Try cities like Paris, London, New York for test data, or use production API for real data."
        }

    # Sort by price
    hotels.sort(key=lambda x: float(x.get("offers", [{}])[0].get("price", {}).get("total", 99999)))

    # Categorize into budget, mid-range, luxury
    categorized = {
        "budget": [],
        "mid_range": [],
        "luxury": []
    }

    for i, hotel in enumerate(hotels):
        parsed = _parse_hotel(hotel, check_in, check_out, guests, rooms)
        if not parsed:
            continue

        # Skip test properties
        hotel_name = parsed.get("name", "").lower()
        if "test" in hotel_name or "test property" in hotel_name:
            continue

        if i < 3:
            categorized["budget"].append(parsed)
        elif i < 6:
            categorized["mid_range"].append(parsed)
        else:
            categorized["luxury"].append(parsed)

        if len(categorized["luxury"]) >= 3:
            break

    # Calculate nights
    from datetime import datetime
    d1 = datetime.strptime(check_in, "%Y-%m-%d")
    d2 = datetime.strptime(check_out, "%Y-%m-%d")
    nights = (d2 - d1).days

    return {
        "destination": destination,
        "check_in": check_in,
        "check_out": check_out,
        "nights": nights,
        "guests": guests,
        "rooms": rooms,
        "hotels": categorized,
        "source": "amadeus_api"
    }


def _parse_hotel(hotel: Dict, check_in: str, check_out: str, guests: int, rooms: int) -> Dict[str, Any]:
    """Parse Amadeus hotel offer into readable format"""
    try:
        offer = hotel.get("offers", [{}])[0]
        price = float(offer.get("price", {}).get("total", 0))

        if price == 0:
            return None

        # Calculate nights
        from datetime import datetime
        d1 = datetime.strptime(check_in, "%Y-%m-%d")
        d2 = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (d2 - d1).days

        hotel_info = hotel.get("hotel", {})

        return {
            "name": hotel_info.get("name", "Unknown Hotel"),
            "hotel_id": hotel_info.get("hotelId", ""),
            "location": hotel_info.get("address", {}).get("cityName", ""),
            "rating": hotel_info.get("rating", "N/A"),
            "price_per_night": round(price / nights, 2) if nights > 0 else price,
            "total_price": round(price, 2),
            "nights": nights,
            "rooms": rooms,
            "guests": guests,
            "room_type": offer.get("room", {}).get("typeEstimated", {}).get("category", "Standard"),
            "cancellation": offer.get("policies", {}).get("cancellation", {}).get("description", {}).get("text", "Check policy"),
            "booking_url": f"https://www.amadeus.com/hotel/book?id={hotel_info.get('hotelId', '')}&check_in={check_in}&check_out={check_out}"
        }
    except Exception:
        return None


# Synchronous wrapper
def search_hotels_amadeus_sync(
    destination: str,
    check_in: str,
    check_out: str,
    guests: int = 2,
    rooms: int = 1
) -> Dict[str, Any]:
    """Synchronous version of search_hotels_amadeus"""
    import nest_asyncio
    nest_asyncio.apply()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in an event loop, create a new task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    search_hotels_amadeus(destination, check_in, check_out, guests, rooms)
                )
                return future.result(timeout=30)
        else:
            return asyncio.run(search_hotels_amadeus(
                destination, check_in, check_out, guests, rooms
            ))
    except Exception as e:
        return {"error": str(e)}
