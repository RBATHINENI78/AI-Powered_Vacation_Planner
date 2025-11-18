"""
Budget Tool - Calculate vacation budget estimates
"""

from typing import Dict, Any


def calculate_budget(
    flights: float,
    hotels_per_night: float,
    nights: int,
    daily_food: float,
    activities: float,
    misc_percent: float = 15.0
) -> Dict[str, Any]:
    """
    Calculate total vacation budget with detailed breakdown.

    Args:
        flights: Total flight cost
        hotels_per_night: Hotel cost per night
        nights: Number of nights
        daily_food: Daily food budget
        activities: Total activities budget
        misc_percent: Miscellaneous expenses percentage

    Returns:
        Detailed budget breakdown
    """
    hotel_total = hotels_per_night * nights
    food_total = daily_food * nights
    subtotal = flights + hotel_total + food_total + activities
    misc = subtotal * (misc_percent / 100)
    total = subtotal + misc

    return {
        "breakdown": {
            "flights": round(flights, 2),
            "accommodation": round(hotel_total, 2),
            "food": round(food_total, 2),
            "activities": round(activities, 2),
            "miscellaneous": round(misc, 2)
        },
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
        "per_night_average": round(total / nights, 2) if nights > 0 else 0,
        "per_day_average": round(total / (nights + 1), 2) if nights >= 0 else 0,
        "source": "budget_calculator",
        "status": "success"
    }


def estimate_daily_costs(destination: str, travel_style: str = "moderate") -> Dict[str, Any]:
    """
    Estimate daily costs based on destination and travel style.

    Args:
        destination: City or country name
        travel_style: budget, moderate, or luxury

    Returns:
        Estimated daily costs
    """
    # Base estimates (in USD) - would be expanded with real data
    cost_matrix = {
        "Paris": {"budget": 100, "moderate": 200, "luxury": 500},
        "London": {"budget": 120, "moderate": 220, "luxury": 550},
        "Tokyo": {"budget": 80, "moderate": 180, "luxury": 450},
        "New York": {"budget": 150, "moderate": 250, "luxury": 600},
        "default": {"budget": 80, "moderate": 150, "luxury": 400}
    }

    # Extract city name
    city = destination.split(",")[0].strip()
    costs = cost_matrix.get(city, cost_matrix["default"])
    daily_cost = costs.get(travel_style, costs["moderate"])

    return {
        "destination": destination,
        "travel_style": travel_style,
        "estimated_daily_cost_usd": daily_cost,
        "includes": [
            "Accommodation",
            "Meals (3 per day)",
            "Local transportation",
            "Basic activities"
        ],
        "excludes": [
            "International flights",
            "Special tours",
            "Shopping",
            "Visa fees"
        ],
        "source": "cost_estimator",
        "status": "success"
    }


def create_budget_plan(
    destination: str,
    nights: int,
    travelers: int,
    travel_style: str = "moderate",
    include_flights: float = 0
) -> Dict[str, Any]:
    """
    Create a complete budget plan for a trip.

    Args:
        destination: Destination city
        nights: Number of nights
        travelers: Number of travelers
        travel_style: budget, moderate, or luxury
        include_flights: Flight cost if known (0 to estimate)

    Returns:
        Complete budget plan
    """
    # Get daily cost estimate
    daily_estimate = estimate_daily_costs(destination, travel_style)
    daily_cost = daily_estimate["estimated_daily_cost_usd"]

    # Estimate flight costs if not provided
    if include_flights <= 0:
        flight_estimates = {
            "Paris": 800,
            "London": 750,
            "Tokyo": 1200,
            "New York": 400,
            "default": 600
        }
        city = destination.split(",")[0].strip()
        flight_cost = flight_estimates.get(city, flight_estimates["default"]) * travelers
    else:
        flight_cost = include_flights

    # Calculate totals
    accommodation = daily_cost * 0.4 * nights * travelers
    food = daily_cost * 0.3 * nights * travelers
    transport = daily_cost * 0.15 * nights * travelers
    activities = daily_cost * 0.15 * nights * travelers
    misc = (accommodation + food + transport + activities) * 0.1

    total = flight_cost + accommodation + food + transport + activities + misc

    return {
        "destination": destination,
        "duration": f"{nights} nights / {nights + 1} days",
        "travelers": travelers,
        "travel_style": travel_style,
        "budget_breakdown": {
            "flights": round(flight_cost, 2),
            "accommodation": round(accommodation, 2),
            "food_and_dining": round(food, 2),
            "local_transport": round(transport, 2),
            "activities_and_tours": round(activities, 2),
            "miscellaneous": round(misc, 2)
        },
        "total_estimated_budget": round(total, 2),
        "per_person": round(total / travelers, 2),
        "per_night": round(total / nights, 2) if nights > 0 else 0,
        "currency": "USD",
        "source": "budget_planner",
        "status": "success"
    }
