"""
Flight database with booking URLs
"""

from typing import Dict, List, Any

FLIGHT_DATABASE = {
    "JFK-CDG": {  # New York to Paris
        "budget": [
            {
                "airline": "Norwegian Air",
                "flight_number": "DY7001",
                "departure": "18:00",
                "arrival": "07:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "price_per_person": 450,
                "baggage": "1 carry-on",
                "booking_url": "https://www.norwegian.com/flights/jfk-cdg"
            },
            {
                "airline": "PLAY",
                "flight_number": "OG801",
                "departure": "20:00",
                "arrival": "10:00+1",
                "duration": "8h 00m",
                "stops": 1,
                "layover": "Reykjavik (2h)",
                "price_per_person": 380,
                "baggage": "1 carry-on",
                "booking_url": "https://www.flyplay.com/flights/new-york-paris"
            },
            {
                "airline": "French Bee",
                "flight_number": "BF720",
                "departure": "22:30",
                "arrival": "12:00+1",
                "duration": "7h 30m",
                "stops": 0,
                "price_per_person": 420,
                "baggage": "1 carry-on, 1 checked",
                "booking_url": "https://www.frenchbee.com/en/flights/new-york-paris"
            }
        ],
        "mid_range": [
            {
                "airline": "Delta Air Lines",
                "flight_number": "DL264",
                "departure": "17:00",
                "arrival": "06:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "price_per_person": 750,
                "baggage": "1 carry-on, 1 checked",
                "booking_url": "https://www.delta.com/flight-search/book-a-flight"
            },
            {
                "airline": "United Airlines",
                "flight_number": "UA57",
                "departure": "18:30",
                "arrival": "08:00+1",
                "duration": "7h 30m",
                "stops": 0,
                "price_per_person": 780,
                "baggage": "1 carry-on, 1 checked",
                "booking_url": "https://www.united.com/flights/new-york-to-paris"
            },
            {
                "airline": "American Airlines",
                "flight_number": "AA44",
                "departure": "19:00",
                "arrival": "08:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "price_per_person": 720,
                "baggage": "1 carry-on, 1 checked",
                "booking_url": "https://www.aa.com/booking/flights"
            }
        ],
        "premium": [
            {
                "airline": "Air France",
                "flight_number": "AF7",
                "departure": "19:00",
                "arrival": "08:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "class": "Business",
                "price_per_person": 2800,
                "baggage": "2 carry-on, 2 checked",
                "amenities": ["Lie-flat seat", "Lounge access", "Priority boarding"],
                "booking_url": "https://www.airfrance.com/booking/business-class"
            },
            {
                "airline": "Delta Air Lines",
                "flight_number": "DL264",
                "departure": "17:00",
                "arrival": "06:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "class": "Delta One",
                "price_per_person": 3200,
                "baggage": "2 carry-on, 2 checked",
                "amenities": ["Suite", "Lounge access", "Premium dining"],
                "booking_url": "https://www.delta.com/delta-one"
            },
            {
                "airline": "La Compagnie",
                "flight_number": "B00101",
                "departure": "21:00",
                "arrival": "10:30+1",
                "duration": "7h 30m",
                "stops": 0,
                "class": "All Business",
                "price_per_person": 1800,
                "baggage": "2 carry-on, 2 checked",
                "amenities": ["Lie-flat seat", "Gourmet meals", "Premium wine"],
                "booking_url": "https://www.lacompagnie.com/book"
            }
        ]
    },
    "JFK-NRT": {  # New York to Tokyo
        "budget": [
            {
                "airline": "Zipair",
                "flight_number": "ZG52",
                "departure": "12:00",
                "arrival": "15:30+1",
                "duration": "14h 30m",
                "stops": 0,
                "price_per_person": 650,
                "baggage": "1 carry-on",
                "booking_url": "https://www.zipair.net/en/booking"
            }
        ],
        "mid_range": [
            {
                "airline": "ANA",
                "flight_number": "NH9",
                "departure": "13:30",
                "arrival": "17:00+1",
                "duration": "14h 30m",
                "stops": 0,
                "price_per_person": 1200,
                "baggage": "2 checked bags",
                "booking_url": "https://www.ana.co.jp/en/book-plan/booking/"
            }
        ],
        "premium": [
            {
                "airline": "Japan Airlines",
                "flight_number": "JL5",
                "departure": "12:30",
                "arrival": "16:00+1",
                "duration": "14h 30m",
                "stops": 0,
                "class": "Business",
                "price_per_person": 5500,
                "baggage": "3 checked bags",
                "booking_url": "https://www.jal.co.jp/en/booking/"
            }
        ]
    },
    "JFK-LHR": {  # New York to London
        "budget": [
            {
                "airline": "Norse Atlantic",
                "flight_number": "N0101",
                "departure": "21:00",
                "arrival": "09:00+1",
                "duration": "7h 00m",
                "stops": 0,
                "price_per_person": 350,
                "baggage": "1 carry-on",
                "booking_url": "https://www.flynorse.com/booking"
            }
        ],
        "mid_range": [
            {
                "airline": "British Airways",
                "flight_number": "BA178",
                "departure": "19:00",
                "arrival": "07:00+1",
                "duration": "7h 00m",
                "stops": 0,
                "price_per_person": 850,
                "baggage": "1 carry-on, 1 checked",
                "booking_url": "https://www.britishairways.com/book"
            }
        ],
        "premium": [
            {
                "airline": "British Airways",
                "flight_number": "BA178",
                "departure": "19:00",
                "arrival": "07:00+1",
                "duration": "7h 00m",
                "stops": 0,
                "class": "Club World",
                "price_per_person": 4500,
                "baggage": "2 checked bags",
                "booking_url": "https://www.britishairways.com/club-world"
            }
        ]
    }
}


def search_flights_data(origin: str, destination: str, travelers: int = 1) -> Dict[str, Any]:
    """
    Search for flights in the database.

    Args:
        origin: Origin airport code (e.g., JFK)
        destination: Destination airport code (e.g., CDG)
        travelers: Number of travelers

    Returns:
        Flight options by category with total prices
    """
    # Map city names to airport codes
    city_to_airport = {
        "New York": "JFK", "NYC": "JFK",
        "Paris": "CDG",
        "Tokyo": "NRT", "Narita": "NRT",
        "London": "LHR", "Heathrow": "LHR"
    }

    # Normalize inputs
    origin_code = city_to_airport.get(origin, origin.upper())
    dest_code = city_to_airport.get(destination, destination.upper())

    route = f"{origin_code}-{dest_code}"

    if route not in FLIGHT_DATABASE:
        return {
            "error": f"No flights found for route {route}",
            "available_routes": list(FLIGHT_DATABASE.keys())
        }

    flights = FLIGHT_DATABASE[route]
    result = {}

    for category, flight_list in flights.items():
        result[category] = []
        for flight in flight_list:
            flight_copy = flight.copy()
            flight_copy["total_price"] = flight["price_per_person"] * travelers
            flight_copy["travelers"] = travelers
            result[category].append(flight_copy)

    return {
        "route": route,
        "travelers": travelers,
        "flights": result
    }
