"""
Booking Agents - Flight, Hotel, and Car Rental Agents
Designed for parallel execution in booking phase
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
from loguru import logger
from .base_agent import BaseAgent


class FlightBookingAgent(BaseAgent):
    """
    Flight Booking Agent for searching and comparing flights.
    Designed for parallel execution with other booking agents.
    """

    def __init__(self):
        super().__init__(
            name="flight_booking",
            description="Searches and compares flight options"
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for flight options.

        Args:
            input_data: Contains origin, destination, dates, travelers

        Returns:
            List of flight options
        """
        origin = input_data.get("origin", "")
        destination = input_data.get("destination", "")
        departure_date = input_data.get("departure_date", "")
        return_date = input_data.get("return_date", "")
        travelers = input_data.get("travelers", 1)
        cabin_class = input_data.get("cabin_class", "economy")

        # Simulate flight search results
        flights = self._search_flights(
            origin, destination, departure_date, return_date, travelers, cabin_class
        )

        # Sort by price
        flights.sort(key=lambda x: x["total_price"])

        # Get recommendation
        recommendation = self._get_recommendation(flights, input_data.get("priority", "price"))

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
            "results_count": len(flights),
            "flights": flights,
            "recommended": recommendation,
            "booking_tips": self._get_booking_tips()
        }

    def _search_flights(
        self,
        origin: str,
        destination: str,
        departure: str,
        return_date: str,
        travelers: int,
        cabin: str
    ) -> List[Dict[str, Any]]:
        """Simulate flight search results."""
        airlines = [
            ("Delta", "DL"), ("United", "UA"), ("American", "AA"),
            ("Air France", "AF"), ("British Airways", "BA"), ("Lufthansa", "LH")
        ]

        cabin_multipliers = {"economy": 1.0, "premium_economy": 1.5, "business": 3.0, "first": 5.0}
        base_price = random.randint(400, 800)

        flights = []
        for airline, code in random.sample(airlines, min(4, len(airlines))):
            price_variation = random.uniform(0.85, 1.15)
            base = base_price * price_variation * cabin_multipliers.get(cabin, 1.0)

            flight = {
                "airline": airline,
                "flight_number": f"{code}{random.randint(100, 999)}",
                "outbound": {
                    "departure": f"{departure} {random.randint(6, 20):02d}:00",
                    "arrival": f"{departure} {random.randint(10, 23):02d}:00",
                    "duration": f"{random.randint(6, 14)}h {random.randint(0, 59)}m",
                    "stops": random.choice([0, 0, 1, 1, 2])
                },
                "return": {
                    "departure": f"{return_date} {random.randint(6, 20):02d}:00",
                    "arrival": f"{return_date} {random.randint(10, 23):02d}:00",
                    "duration": f"{random.randint(6, 14)}h {random.randint(0, 59)}m",
                    "stops": random.choice([0, 0, 1, 1, 2])
                },
                "price_per_person": round(base, 2),
                "total_price": round(base * travelers, 2),
                "cabin_class": cabin,
                "baggage": "1 carry-on, 1 checked" if cabin != "economy" else "1 carry-on",
                "refundable": random.choice([True, False])
            }
            flights.append(flight)

        return flights

    def _get_recommendation(self, flights: List[Dict], priority: str) -> Dict[str, Any]:
        """Get recommended flight based on priority."""
        if not flights:
            return {"message": "No flights found"}

        if priority == "duration":
            # Sort by total stops (fewer is better)
            flights.sort(key=lambda x: x["outbound"]["stops"] + x["return"]["stops"])

        # Default to cheapest (already sorted by price)
        recommended = flights[0]

        return {
            "flight": recommended,
            "reason": f"Best {priority} option" if priority else "Lowest price"
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
    Hotel Booking Agent for searching and comparing accommodations.
    Designed for parallel execution with other booking agents.
    """

    def __init__(self):
        super().__init__(
            name="hotel_booking",
            description="Searches and compares hotel options"
        )

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for hotel options.

        Args:
            input_data: Contains destination, dates, guests, preferences

        Returns:
            List of hotel options
        """
        destination = input_data.get("destination", "")
        check_in = input_data.get("check_in", "")
        check_out = input_data.get("check_out", "")
        guests = input_data.get("guests", 2)
        rooms = input_data.get("rooms", 1)
        budget_per_night = input_data.get("budget_per_night", 200)
        star_rating = input_data.get("star_rating", 3)

        # Simulate hotel search
        hotels = self._search_hotels(
            destination, check_in, check_out, guests, rooms, budget_per_night, star_rating
        )

        # Sort by rating
        hotels.sort(key=lambda x: x["rating"], reverse=True)

        # Get recommendation
        recommendation = self._get_recommendation(hotels, input_data.get("priority", "rating"))

        return {
            "status": "success",
            "search_params": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests,
                "rooms": rooms
            },
            "results_count": len(hotels),
            "hotels": hotels,
            "recommended": recommendation,
            "booking_tips": self._get_booking_tips()
        }

    def _search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        guests: int,
        rooms: int,
        budget: float,
        stars: int
    ) -> List[Dict[str, Any]]:
        """Simulate hotel search results."""
        hotel_types = [
            ("Grand Hotel", 5, 1.5),
            ("City Center Inn", 4, 1.0),
            ("Comfort Suites", 3, 0.7),
            ("Budget Lodge", 2, 0.4),
            ("Boutique Hotel", 4, 1.2),
            ("Business Hotel", 4, 0.9)
        ]

        # Calculate nights
        try:
            d1 = datetime.strptime(check_in, "%Y-%m-%d")
            d2 = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (d2 - d1).days
        except (ValueError, TypeError):
            nights = 7

        hotels = []
        for name, star, price_mult in hotel_types:
            if star >= stars - 1:  # Include hotels within 1 star of preference
                base_price = budget * price_mult * random.uniform(0.8, 1.2)
                total = base_price * nights * rooms

                hotel = {
                    "name": f"{name} {destination.split(',')[0]}",
                    "stars": star,
                    "rating": round(random.uniform(3.5, 4.9), 1),
                    "reviews_count": random.randint(100, 2000),
                    "location": f"City Center, {destination}",
                    "price_per_night": round(base_price, 2),
                    "total_price": round(total, 2),
                    "nights": nights,
                    "rooms": rooms,
                    "amenities": self._get_amenities(star),
                    "cancellation": "Free cancellation" if random.random() > 0.3 else "Non-refundable",
                    "breakfast": random.choice([True, False])
                }
                hotels.append(hotel)

        return hotels

    def _get_amenities(self, stars: int) -> List[str]:
        """Get amenities based on star rating."""
        base = ["WiFi", "Air Conditioning"]

        if stars >= 3:
            base.extend(["Room Service", "Fitness Center"])
        if stars >= 4:
            base.extend(["Pool", "Restaurant", "Concierge"])
        if stars >= 5:
            base.extend(["Spa", "Valet Parking", "Business Center"])

        return base

    def _get_recommendation(self, hotels: List[Dict], priority: str) -> Dict[str, Any]:
        """Get recommended hotel based on priority."""
        if not hotels:
            return {"message": "No hotels found"}

        if priority == "price":
            hotels.sort(key=lambda x: x["price_per_night"])
        elif priority == "stars":
            hotels.sort(key=lambda x: x["stars"], reverse=True)
        # Default is rating (already sorted)

        return {
            "hotel": hotels[0],
            "reason": f"Best {priority} option" if priority else "Highest rated"
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
