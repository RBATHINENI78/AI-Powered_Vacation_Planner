"""
Hotel database with booking URLs
"""

from typing import Dict, List, Any

HOTEL_DATABASE = {
    "Paris": {
        "budget": [
            {
                "name": "Generator Paris",
                "location": "10th Arrondissement, near Gare du Nord",
                "stars": 2,
                "rating": 4.2,
                "reviews": 8500,
                "price_per_night": 85,
                "amenities": ["WiFi", "Bar", "24h Reception", "Lockers"],
                "cancellation": "Free cancellation until 24h before",
                "breakfast": False,
                "booking_url": "https://www.booking.com/hotel/fr/generator-paris.html"
            },
            {
                "name": "Hotel Ibis Paris Montmartre",
                "location": "Montmartre, 18th Arrondissement",
                "stars": 3,
                "rating": 4.0,
                "reviews": 5200,
                "price_per_night": 95,
                "amenities": ["WiFi", "AC", "24h Reception"],
                "cancellation": "Free cancellation until 48h before",
                "breakfast": True,
                "breakfast_price": 12,
                "booking_url": "https://www.booking.com/hotel/fr/ibis-paris-montmartre.html"
            },
            {
                "name": "Hotel du Nord et de l'Est",
                "location": "10th Arrondissement",
                "stars": 2,
                "rating": 3.8,
                "reviews": 3100,
                "price_per_night": 75,
                "amenities": ["WiFi", "24h Reception"],
                "cancellation": "Free cancellation until 24h before",
                "breakfast": False,
                "booking_url": "https://www.booking.com/hotel/fr/du-nord-et-de-l-est.html"
            }
        ],
        "mid_range": [
            {
                "name": "Hotel Le Marais",
                "location": "Le Marais, 4th Arrondissement",
                "stars": 4,
                "rating": 4.5,
                "reviews": 4200,
                "price_per_night": 180,
                "amenities": ["WiFi", "AC", "Room Service", "Concierge", "Fitness"],
                "cancellation": "Free cancellation until 48h before",
                "breakfast": True,
                "breakfast_price": 18,
                "booking_url": "https://www.booking.com/hotel/fr/le-marais-paris.html"
            },
            {
                "name": "Hotel du Louvre",
                "location": "1st Arrondissement, near Louvre",
                "stars": 4,
                "rating": 4.6,
                "reviews": 6800,
                "price_per_night": 220,
                "amenities": ["WiFi", "AC", "Room Service", "Spa", "Restaurant"],
                "cancellation": "Free cancellation until 72h before",
                "breakfast": True,
                "breakfast_price": 25,
                "booking_url": "https://www.booking.com/hotel/fr/louvre-paris.html"
            },
            {
                "name": "Hotel Eiffel Blomet",
                "location": "15th Arrondissement, near Eiffel Tower",
                "stars": 4,
                "rating": 4.4,
                "reviews": 3500,
                "price_per_night": 195,
                "amenities": ["WiFi", "AC", "Pool", "Garden", "Bar"],
                "cancellation": "Free cancellation until 48h before",
                "breakfast": True,
                "breakfast_price": 20,
                "booking_url": "https://www.booking.com/hotel/fr/eiffel-blomet.html"
            }
        ],
        "luxury": [
            {
                "name": "The Ritz Paris",
                "location": "Place Vendôme, 1st Arrondissement",
                "stars": 5,
                "rating": 4.9,
                "reviews": 2100,
                "price_per_night": 1200,
                "amenities": ["WiFi", "Spa", "Pool", "Michelin Restaurant", "Butler", "Concierge"],
                "cancellation": "Free cancellation until 7 days before",
                "breakfast": True,
                "breakfast_price": 75,
                "booking_url": "https://www.ritzparis.com/en-GB/booking"
            },
            {
                "name": "Four Seasons Hotel George V",
                "location": "Champs-Élysées, 8th Arrondissement",
                "stars": 5,
                "rating": 4.8,
                "reviews": 3400,
                "price_per_night": 950,
                "amenities": ["WiFi", "Spa", "Pool", "3 Restaurants", "Concierge", "Fitness"],
                "cancellation": "Free cancellation until 5 days before",
                "breakfast": True,
                "breakfast_price": 65,
                "booking_url": "https://www.fourseasons.com/paris/accommodations/"
            },
            {
                "name": "Le Bristol Paris",
                "location": "Faubourg Saint-Honoré, 8th Arrondissement",
                "stars": 5,
                "rating": 4.9,
                "reviews": 2800,
                "price_per_night": 1100,
                "amenities": ["WiFi", "Rooftop Pool", "Spa", "Michelin Restaurant", "Garden"],
                "cancellation": "Free cancellation until 7 days before",
                "breakfast": True,
                "breakfast_price": 70,
                "booking_url": "https://www.oetkercollection.com/hotels/le-bristol-paris/"
            }
        ]
    },
    "Tokyo": {
        "budget": [
            {
                "name": "The Millennials Shibuya",
                "location": "Shibuya",
                "stars": 3,
                "rating": 4.3,
                "reviews": 4200,
                "price_per_night": 65,
                "amenities": ["WiFi", "Smart Pods", "Coworking", "Lounge"],
                "cancellation": "Free cancellation until 24h before",
                "breakfast": False,
                "booking_url": "https://www.booking.com/hotel/jp/the-millennials-shibuya.html"
            }
        ],
        "mid_range": [
            {
                "name": "Shinjuku Granbell Hotel",
                "location": "Shinjuku",
                "stars": 4,
                "rating": 4.5,
                "reviews": 5600,
                "price_per_night": 150,
                "amenities": ["WiFi", "AC", "Restaurant", "Rooftop Bar"],
                "cancellation": "Free cancellation until 48h before",
                "breakfast": True,
                "breakfast_price": 20,
                "booking_url": "https://www.booking.com/hotel/jp/shinjuku-granbell.html"
            }
        ],
        "luxury": [
            {
                "name": "Park Hyatt Tokyo",
                "location": "Shinjuku",
                "stars": 5,
                "rating": 4.8,
                "reviews": 3200,
                "price_per_night": 650,
                "amenities": ["WiFi", "Pool", "Spa", "Michelin Restaurant", "Fitness"],
                "cancellation": "Free cancellation until 72h before",
                "breakfast": True,
                "breakfast_price": 55,
                "booking_url": "https://www.hyatt.com/park-hyatt/tyoph-park-hyatt-tokyo"
            }
        ]
    },
    "London": {
        "budget": [
            {
                "name": "Hub by Premier Inn Westminster",
                "location": "Westminster",
                "stars": 3,
                "rating": 4.2,
                "reviews": 7800,
                "price_per_night": 95,
                "amenities": ["WiFi", "AC", "Smart TV", "App Control"],
                "cancellation": "Free cancellation until 24h before",
                "breakfast": False,
                "booking_url": "https://www.premierinn.com/hub-westminster"
            }
        ],
        "mid_range": [
            {
                "name": "The Resident Covent Garden",
                "location": "Covent Garden",
                "stars": 4,
                "rating": 4.6,
                "reviews": 4100,
                "price_per_night": 200,
                "amenities": ["WiFi", "Kitchenette", "AC", "Concierge"],
                "cancellation": "Free cancellation until 48h before",
                "breakfast": False,
                "booking_url": "https://www.booking.com/hotel/gb/resident-covent-garden.html"
            }
        ],
        "luxury": [
            {
                "name": "The Savoy",
                "location": "Strand, West End",
                "stars": 5,
                "rating": 4.8,
                "reviews": 4500,
                "price_per_night": 750,
                "amenities": ["WiFi", "Pool", "Spa", "Multiple Restaurants", "Butler"],
                "cancellation": "Free cancellation until 7 days before",
                "breakfast": True,
                "breakfast_price": 45,
                "booking_url": "https://www.thesavoylondon.com/reservations/"
            }
        ]
    },
    "Kochi": {
        "budget": [
            {"name": "Zostel Kochi", "location": "Fort Kochi", "stars": 2, "rating": 4.3, "reviews": 2100, "price_per_night": 25, "amenities": ["WiFi", "AC", "Common Kitchen"], "cancellation": "Free cancellation until 24h before", "breakfast": False, "booking_url": "https://www.zostel.com/kochi"},
            {"name": "Hotel Abad Metro", "location": "MG Road", "stars": 3, "rating": 4.1, "reviews": 3200, "price_per_night": 45, "amenities": ["WiFi", "AC", "Restaurant"], "cancellation": "Free cancellation until 24h before", "breakfast": True, "breakfast_price": 8, "booking_url": "https://www.booking.com/hotel/in/abad-metro.html"}
        ],
        "mid_range": [
            {"name": "Fragrant Nature Kochi", "location": "Marine Drive", "stars": 4, "rating": 4.5, "reviews": 2800, "price_per_night": 85, "amenities": ["WiFi", "AC", "Pool", "Spa", "Restaurant"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 12, "booking_url": "https://www.fragrantnature.com/kochi"},
            {"name": "Casino Hotel", "location": "Willingdon Island", "stars": 4, "rating": 4.4, "reviews": 3500, "price_per_night": 95, "amenities": ["WiFi", "AC", "Pool", "Restaurant", "Bar"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 15, "booking_url": "https://www.cghearth.com/casino-hotel"}
        ],
        "luxury": [
            {"name": "Taj Malabar Resort & Spa", "location": "Willingdon Island", "stars": 5, "rating": 4.7, "reviews": 4200, "price_per_night": 180, "amenities": ["WiFi", "Pool", "Spa", "Multiple Restaurants", "Butler", "Waterfront"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 25, "booking_url": "https://www.tajhotels.com/malabar"},
            {"name": "Brunton Boatyard", "location": "Fort Kochi", "stars": 5, "rating": 4.8, "reviews": 3100, "price_per_night": 200, "amenities": ["WiFi", "Pool", "Heritage Property", "Restaurant", "Waterfront"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 20, "booking_url": "https://www.cghearth.com/brunton-boatyard"}
        ]
    },
    "Dubai": {
        "budget": [
            {"name": "Rove Downtown", "location": "Downtown Dubai", "stars": 3, "rating": 4.4, "reviews": 8500, "price_per_night": 80, "amenities": ["WiFi", "AC", "Pool", "Gym"], "cancellation": "Free cancellation until 24h before", "breakfast": False, "booking_url": "https://www.rovehotels.com/downtown"},
            {"name": "Premier Inn Dubai", "location": "Al Jaddaf", "stars": 3, "rating": 4.2, "reviews": 6200, "price_per_night": 65, "amenities": ["WiFi", "AC", "Restaurant"], "cancellation": "Free cancellation until 24h before", "breakfast": True, "breakfast_price": 15, "booking_url": "https://www.premierinn.com/dubai"}
        ],
        "mid_range": [
            {"name": "Hilton Dubai Creek", "location": "Deira", "stars": 4, "rating": 4.5, "reviews": 5800, "price_per_night": 120, "amenities": ["WiFi", "AC", "Pool", "Spa", "Restaurant"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 25, "booking_url": "https://www.hilton.com/dubai-creek"},
            {"name": "Sofitel Dubai Downtown", "location": "Downtown Dubai", "stars": 5, "rating": 4.6, "reviews": 4200, "price_per_night": 180, "amenities": ["WiFi", "Pool", "Spa", "Multiple Restaurants"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 35, "booking_url": "https://www.sofitel.com/dubai-downtown"}
        ],
        "luxury": [
            {"name": "Burj Al Arab", "location": "Jumeirah", "stars": 5, "rating": 4.9, "reviews": 3200, "price_per_night": 1500, "amenities": ["WiFi", "Private Beach", "Pool", "Spa", "Butler", "Helipad"], "cancellation": "Free cancellation until 14 days before", "breakfast": True, "breakfast_price": 100, "booking_url": "https://www.jumeirah.com/burj-al-arab"},
            {"name": "Atlantis The Palm", "location": "Palm Jumeirah", "stars": 5, "rating": 4.7, "reviews": 12000, "price_per_night": 450, "amenities": ["WiFi", "Waterpark", "Aquarium", "Multiple Restaurants", "Beach"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 65, "booking_url": "https://www.atlantis.com/dubai"}
        ]
    },
    "Doha": {
        "budget": [
            {"name": "Premier Inn Doha", "location": "Old Airport", "stars": 3, "rating": 4.1, "reviews": 3200, "price_per_night": 60, "amenities": ["WiFi", "AC", "Restaurant"], "cancellation": "Free cancellation until 24h before", "breakfast": True, "breakfast_price": 12, "booking_url": "https://www.premierinn.com/doha"}
        ],
        "mid_range": [
            {"name": "Oryx Rotana", "location": "West Bay", "stars": 4, "rating": 4.4, "reviews": 4500, "price_per_night": 100, "amenities": ["WiFi", "AC", "Pool", "Spa", "Restaurant"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 20, "booking_url": "https://www.rotana.com/oryx-doha"},
            {"name": "Hilton Doha", "location": "West Bay", "stars": 5, "rating": 4.5, "reviews": 5100, "price_per_night": 150, "amenities": ["WiFi", "Pool", "Spa", "Beach", "Restaurant"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 30, "booking_url": "https://www.hilton.com/doha"}
        ],
        "luxury": [
            {"name": "St. Regis Doha", "location": "West Bay", "stars": 5, "rating": 4.8, "reviews": 2800, "price_per_night": 350, "amenities": ["WiFi", "Pool", "Spa", "Beach", "Butler", "Multiple Restaurants"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 50, "booking_url": "https://www.marriott.com/st-regis-doha"},
            {"name": "Mandarin Oriental Doha", "location": "Msheireb Downtown", "stars": 5, "rating": 4.9, "reviews": 1800, "price_per_night": 400, "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Butler"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 55, "booking_url": "https://www.mandarinoriental.com/doha"}
        ]
    },
    "Salt Lake City": {
        "budget": [
            {"name": "Motel 6 Downtown", "location": "Downtown SLC", "stars": 2, "rating": 3.8, "reviews": 2100, "price_per_night": 55, "amenities": ["WiFi", "AC", "Parking"], "cancellation": "Free cancellation until 24h before", "breakfast": False, "booking_url": "https://www.motel6.com/slc"},
            {"name": "Comfort Inn Downtown", "location": "Downtown", "stars": 3, "rating": 4.1, "reviews": 3400, "price_per_night": 85, "amenities": ["WiFi", "AC", "Pool", "Fitness"], "cancellation": "Free cancellation until 24h before", "breakfast": True, "breakfast_price": 0, "booking_url": "https://www.choicehotels.com/comfort-inn-slc"}
        ],
        "mid_range": [
            {"name": "Hilton Salt Lake City Center", "location": "Downtown", "stars": 4, "rating": 4.4, "reviews": 4800, "price_per_night": 140, "amenities": ["WiFi", "AC", "Pool", "Restaurant", "Fitness"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 18, "booking_url": "https://www.hilton.com/salt-lake-city"},
            {"name": "Little America Hotel", "location": "Downtown", "stars": 4, "rating": 4.5, "reviews": 5200, "price_per_night": 160, "amenities": ["WiFi", "Pool", "Spa", "Restaurant", "Gardens"], "cancellation": "Free cancellation until 48h before", "breakfast": True, "breakfast_price": 20, "booking_url": "https://www.littleamerica.com/salt-lake-city"}
        ],
        "luxury": [
            {"name": "Grand America Hotel", "location": "Downtown", "stars": 5, "rating": 4.8, "reviews": 3600, "price_per_night": 280, "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"], "cancellation": "Free cancellation until 7 days before", "breakfast": True, "breakfast_price": 35, "booking_url": "https://www.grandamerica.com"},
            {"name": "Montage Deer Valley", "location": "Park City", "stars": 5, "rating": 4.9, "reviews": 2100, "price_per_night": 650, "amenities": ["WiFi", "Ski-in/Ski-out", "Pool", "Spa", "Multiple Restaurants"], "cancellation": "Free cancellation until 14 days before", "breakfast": True, "breakfast_price": 45, "booking_url": "https://www.montagehotels.com/deervalley"}
        ]
    }
}


def search_hotels_data(
    destination: str,
    nights: int = 1,
    guests: int = 2,
    rooms: int = 1
) -> Dict[str, Any]:
    """
    Search for hotels in the database.

    Args:
        destination: City name
        nights: Number of nights
        guests: Number of guests
        rooms: Number of rooms

    Returns:
        Hotel options by category with total prices
    """
    # Normalize city name
    city = destination.split(",")[0].strip()

    if city not in HOTEL_DATABASE:
        return {
            "error": f"No hotels found for {city}",
            "available_cities": list(HOTEL_DATABASE.keys())
        }

    hotels = HOTEL_DATABASE[city]
    result = {}

    for category, hotel_list in hotels.items():
        result[category] = []
        for hotel in hotel_list:
            hotel_copy = hotel.copy()
            hotel_copy["total_price"] = hotel["price_per_night"] * nights * rooms
            hotel_copy["nights"] = nights
            hotel_copy["rooms"] = rooms
            hotel_copy["guests"] = guests
            result[category].append(hotel_copy)

    return {
        "destination": city,
        "nights": nights,
        "guests": guests,
        "rooms": rooms,
        "hotels": result
    }
