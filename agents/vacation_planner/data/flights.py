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
    },
    "JFK-COK": {  # New York to Kochi (Kerala, India)
        "budget": [
            {"airline": "Air India", "flight_number": "AI102", "departure": "22:00", "arrival": "23:30+1", "duration": "17h 30m", "stops": 1, "layover": "Delhi (2h)", "price_per_person": 850, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.airindia.com/book"},
            {"airline": "Emirates", "flight_number": "EK202", "departure": "23:30", "arrival": "08:00+2", "duration": "20h 30m", "stops": 1, "layover": "Dubai (4h)", "price_per_person": 920, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.emirates.com/book"},
            {"airline": "Qatar Airways", "flight_number": "QR702", "departure": "20:00", "arrival": "06:30+2", "duration": "22h 30m", "stops": 1, "layover": "Doha (5h)", "price_per_person": 880, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.qatarairways.com/book"}
        ],
        "mid_range": [
            {"airline": "Emirates", "flight_number": "EK201", "departure": "22:00", "arrival": "05:00+2", "duration": "19h 00m", "stops": 1, "layover": "Dubai (3h)", "price_per_person": 1200, "baggage": "2 checked bags", "booking_url": "https://www.emirates.com/book"},
            {"airline": "Etihad", "flight_number": "EY101", "departure": "21:00", "arrival": "04:30+2", "duration": "19h 30m", "stops": 1, "layover": "Abu Dhabi (3h)", "price_per_person": 1150, "baggage": "2 checked bags", "booking_url": "https://www.etihad.com/book"},
            {"airline": "Air India", "flight_number": "AI101", "departure": "19:00", "arrival": "20:30+1", "duration": "17h 30m", "stops": 1, "price_per_person": 1100, "baggage": "2 checked bags", "booking_url": "https://www.airindia.com/book"}
        ],
        "premium": [
            {"airline": "Emirates", "flight_number": "EK201", "departure": "22:00", "arrival": "05:00+2", "duration": "19h 00m", "stops": 1, "class": "Business", "price_per_person": 4500, "baggage": "2 checked bags", "amenities": ["Lie-flat seat", "Lounge access", "Premium dining"], "booking_url": "https://www.emirates.com/business"},
            {"airline": "Qatar Airways", "flight_number": "QR701", "departure": "19:00", "arrival": "03:00+2", "duration": "20h 00m", "stops": 1, "class": "Business", "price_per_person": 4800, "baggage": "2 checked bags", "amenities": ["QSuite", "Lounge access", "Gourmet meals"], "booking_url": "https://www.qatarairways.com/business"}
        ]
    },
    "JFK-DOH": {  # New York to Doha (Qatar)
        "budget": [
            {"airline": "Qatar Airways", "flight_number": "QR702", "departure": "20:00", "arrival": "16:00+1", "duration": "12h 00m", "stops": 0, "price_per_person": 750, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.qatarairways.com/book"}
        ],
        "mid_range": [
            {"airline": "Qatar Airways", "flight_number": "QR701", "departure": "19:00", "arrival": "15:00+1", "duration": "12h 00m", "stops": 0, "price_per_person": 1100, "baggage": "2 checked bags", "booking_url": "https://www.qatarairways.com/book"}
        ],
        "premium": [
            {"airline": "Qatar Airways", "flight_number": "QR701", "departure": "19:00", "arrival": "15:00+1", "duration": "12h 00m", "stops": 0, "class": "QSuite Business", "price_per_person": 5500, "baggage": "2 checked bags", "amenities": ["QSuite", "Lounge access", "Fine dining"], "booking_url": "https://www.qatarairways.com/qsuite"}
        ]
    },
    "JFK-DXB": {  # New York to Dubai
        "budget": [
            {"airline": "Emirates", "flight_number": "EK202", "departure": "23:30", "arrival": "19:30+1", "duration": "12h 00m", "stops": 0, "price_per_person": 700, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.emirates.com/book"},
            {"airline": "Etihad", "flight_number": "EY103", "departure": "22:00", "arrival": "18:30+1", "duration": "12h 30m", "stops": 1, "layover": "Abu Dhabi (1h)", "price_per_person": 680, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.etihad.com/book"}
        ],
        "mid_range": [
            {"airline": "Emirates", "flight_number": "EK201", "departure": "22:00", "arrival": "18:00+1", "duration": "12h 00m", "stops": 0, "price_per_person": 1050, "baggage": "2 checked bags", "booking_url": "https://www.emirates.com/book"}
        ],
        "premium": [
            {"airline": "Emirates", "flight_number": "EK201", "departure": "22:00", "arrival": "18:00+1", "duration": "12h 00m", "stops": 0, "class": "Business", "price_per_person": 5200, "baggage": "2 checked bags", "amenities": ["Lie-flat seat", "Lounge access", "Premium dining"], "booking_url": "https://www.emirates.com/business"}
        ]
    },
    "JFK-DEL": {  # New York to Delhi
        "budget": [
            {"airline": "Air India", "flight_number": "AI102", "departure": "22:00", "arrival": "21:00+1", "duration": "15h 00m", "stops": 0, "price_per_person": 800, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.airindia.com/book"}
        ],
        "mid_range": [
            {"airline": "Air India", "flight_number": "AI101", "departure": "19:00", "arrival": "18:00+1", "duration": "15h 00m", "stops": 0, "price_per_person": 1100, "baggage": "2 checked bags", "booking_url": "https://www.airindia.com/book"},
            {"airline": "United Airlines", "flight_number": "UA48", "departure": "20:00", "arrival": "19:30+1", "duration": "15h 30m", "stops": 0, "price_per_person": 1200, "baggage": "2 checked bags", "booking_url": "https://www.united.com/book"}
        ],
        "premium": [
            {"airline": "Air India", "flight_number": "AI101", "departure": "19:00", "arrival": "18:00+1", "duration": "15h 00m", "stops": 0, "class": "Business", "price_per_person": 4200, "baggage": "2 checked bags", "amenities": ["Lie-flat seat", "Lounge access"], "booking_url": "https://www.airindia.com/business"}
        ]
    },
    "CLT-SLC": {  # Charlotte to Salt Lake City
        "budget": [
            {"airline": "Frontier", "flight_number": "F9234", "departure": "06:00", "arrival": "08:30", "duration": "4h 30m", "stops": 1, "price_per_person": 150, "baggage": "1 personal item", "booking_url": "https://www.flyfrontier.com/book"},
            {"airline": "Southwest", "flight_number": "WN456", "departure": "10:00", "arrival": "12:00", "duration": "4h 00m", "stops": 1, "price_per_person": 180, "baggage": "2 checked free", "booking_url": "https://www.southwest.com/book"}
        ],
        "mid_range": [
            {"airline": "Delta", "flight_number": "DL1234", "departure": "08:00", "arrival": "10:15", "duration": "4h 15m", "stops": 0, "price_per_person": 320, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.delta.com/book"},
            {"airline": "United", "flight_number": "UA567", "departure": "14:00", "arrival": "16:30", "duration": "4h 30m", "stops": 1, "price_per_person": 290, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.united.com/book"}
        ],
        "premium": [
            {"airline": "Delta", "flight_number": "DL1234", "departure": "08:00", "arrival": "10:15", "duration": "4h 15m", "stops": 0, "class": "First Class", "price_per_person": 650, "baggage": "2 checked bags", "amenities": ["Priority boarding", "Extra legroom"], "booking_url": "https://www.delta.com/first"}
        ]
    },
    "LAX-SYD": {  # Los Angeles to Sydney
        "budget": [
            {"airline": "Qantas", "flight_number": "QF12", "departure": "22:00", "arrival": "07:30+2", "duration": "15h 30m", "stops": 0, "price_per_person": 950, "baggage": "1 carry-on, 1 checked", "booking_url": "https://www.qantas.com/book"}
        ],
        "mid_range": [
            {"airline": "Qantas", "flight_number": "QF11", "departure": "21:00", "arrival": "06:30+2", "duration": "15h 30m", "stops": 0, "price_per_person": 1400, "baggage": "2 checked bags", "booking_url": "https://www.qantas.com/book"}
        ],
        "premium": [
            {"airline": "Qantas", "flight_number": "QF11", "departure": "21:00", "arrival": "06:30+2", "duration": "15h 30m", "stops": 0, "class": "Business", "price_per_person": 6500, "baggage": "2 checked bags", "amenities": ["Lie-flat seat", "Lounge"], "booking_url": "https://www.qantas.com/business"}
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
        "London": "LHR", "Heathrow": "LHR",
        "Kochi": "COK", "Kerala": "COK", "Cochin": "COK",
        "Delhi": "DEL", "New Delhi": "DEL",
        "Mumbai": "BOM", "Bombay": "BOM",
        "Dubai": "DXB",
        "Doha": "DOH", "Qatar": "DOH",
        "Charlotte": "CLT",
        "Salt Lake City": "SLC", "SLC": "SLC",
        "Los Angeles": "LAX", "LA": "LAX",
        "Sydney": "SYD"
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
