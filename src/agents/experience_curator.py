"""
Experience Curator Agent - Activities, Attractions, and Local Experiences
"""

from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent


class ExperienceCuratorAgent(BaseAgent):
    """
    Experience Curator Agent for activities and attractions.
    Personalizes recommendations based on interests and constraints.
    """

    def __init__(self):
        super().__init__(
            name="experience_curator",
            description="Curates activities and local experiences"
        )

        # Activity database by destination
        self.activities_db = {
            "Paris": {
                "landmarks": [
                    {"name": "Eiffel Tower", "duration": "2-3 hours", "cost": 25, "rating": 4.7},
                    {"name": "Louvre Museum", "duration": "3-4 hours", "cost": 17, "rating": 4.8},
                    {"name": "Notre-Dame Cathedral", "duration": "1-2 hours", "cost": 0, "rating": 4.6},
                    {"name": "Arc de Triomphe", "duration": "1-2 hours", "cost": 13, "rating": 4.5},
                    {"name": "Sacré-Cœur", "duration": "1-2 hours", "cost": 0, "rating": 4.6}
                ],
                "culture": [
                    {"name": "Musée d'Orsay", "duration": "2-3 hours", "cost": 16, "rating": 4.8},
                    {"name": "Palace of Versailles", "duration": "4-5 hours", "cost": 20, "rating": 4.7},
                    {"name": "Rodin Museum", "duration": "2 hours", "cost": 13, "rating": 4.6}
                ],
                "food": [
                    {"name": "French Cooking Class", "duration": "3 hours", "cost": 100, "rating": 4.9},
                    {"name": "Wine Tasting Tour", "duration": "3 hours", "cost": 80, "rating": 4.7},
                    {"name": "Market Food Tour", "duration": "3 hours", "cost": 60, "rating": 4.8}
                ],
                "entertainment": [
                    {"name": "Seine River Cruise", "duration": "1 hour", "cost": 15, "rating": 4.5},
                    {"name": "Moulin Rouge Show", "duration": "2 hours", "cost": 100, "rating": 4.6},
                    {"name": "Paris Catacombs", "duration": "1-2 hours", "cost": 15, "rating": 4.4}
                ]
            },
            "Tokyo": {
                "landmarks": [
                    {"name": "Senso-ji Temple", "duration": "1-2 hours", "cost": 0, "rating": 4.6},
                    {"name": "Tokyo Skytree", "duration": "2 hours", "cost": 20, "rating": 4.5},
                    {"name": "Meiji Shrine", "duration": "1-2 hours", "cost": 0, "rating": 4.7},
                    {"name": "Imperial Palace", "duration": "2 hours", "cost": 0, "rating": 4.4}
                ],
                "culture": [
                    {"name": "teamLab Borderless", "duration": "2-3 hours", "cost": 30, "rating": 4.8},
                    {"name": "Sumo Tournament", "duration": "4 hours", "cost": 50, "rating": 4.9},
                    {"name": "Traditional Tea Ceremony", "duration": "1 hour", "cost": 40, "rating": 4.7}
                ],
                "food": [
                    {"name": "Tsukiji Outer Market Tour", "duration": "2 hours", "cost": 0, "rating": 4.6},
                    {"name": "Ramen Tasting Tour", "duration": "3 hours", "cost": 70, "rating": 4.8},
                    {"name": "Sushi Making Class", "duration": "2 hours", "cost": 80, "rating": 4.9}
                ],
                "entertainment": [
                    {"name": "Robot Restaurant", "duration": "1.5 hours", "cost": 80, "rating": 4.3},
                    {"name": "Karaoke Night", "duration": "2 hours", "cost": 30, "rating": 4.5},
                    {"name": "Anime District Tour", "duration": "3 hours", "cost": 40, "rating": 4.6}
                ]
            },
            "London": {
                "landmarks": [
                    {"name": "Tower of London", "duration": "3 hours", "cost": 30, "rating": 4.7},
                    {"name": "Westminster Abbey", "duration": "2 hours", "cost": 25, "rating": 4.6},
                    {"name": "Buckingham Palace", "duration": "2 hours", "cost": 30, "rating": 4.5},
                    {"name": "Big Ben & Parliament", "duration": "1 hour", "cost": 0, "rating": 4.6}
                ],
                "culture": [
                    {"name": "British Museum", "duration": "3-4 hours", "cost": 0, "rating": 4.8},
                    {"name": "Tate Modern", "duration": "2-3 hours", "cost": 0, "rating": 4.6},
                    {"name": "National Gallery", "duration": "2-3 hours", "cost": 0, "rating": 4.7}
                ],
                "food": [
                    {"name": "Borough Market Tour", "duration": "2 hours", "cost": 0, "rating": 4.7},
                    {"name": "Afternoon Tea", "duration": "2 hours", "cost": 50, "rating": 4.8},
                    {"name": "Pub Crawl", "duration": "3 hours", "cost": 40, "rating": 4.5}
                ],
                "entertainment": [
                    {"name": "West End Show", "duration": "2.5 hours", "cost": 80, "rating": 4.8},
                    {"name": "Harry Potter Studio Tour", "duration": "4 hours", "cost": 50, "rating": 4.9},
                    {"name": "Thames River Cruise", "duration": "1 hour", "cost": 15, "rating": 4.5}
                ]
            }
        }

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Curate personalized experiences for the trip.

        Args:
            input_data: Contains destination, interests, budget, duration

        Returns:
            Curated list of activities and itinerary suggestions
        """
        destination = input_data.get("destination", "")
        interests = input_data.get("interests", [])
        budget_per_day = input_data.get("activity_budget_per_day", 50)
        nights = input_data.get("nights", 7)
        travelers = input_data.get("travelers", 2)

        # Get city from destination
        city = destination.split(",")[0].strip() if "," in destination else destination

        # Get available activities
        city_activities = self.activities_db.get(city, {})

        if not city_activities:
            return {
                "status": "success",
                "destination": destination,
                "message": f"Limited activity data for {city}",
                "recommendations": self._get_generic_recommendations(interests)
            }

        # Filter and rank activities based on interests
        recommended = self._filter_by_interests(city_activities, interests)

        # Create daily itinerary
        itinerary = self._create_itinerary(recommended, nights, budget_per_day)

        # Calculate total activity cost
        total_cost = self._calculate_total_cost(itinerary, travelers)

        # Get local tips
        local_tips = self._get_local_tips(city)

        return {
            "status": "success",
            "destination": destination,
            "city": city,
            "top_recommendations": recommended[:10],
            "suggested_itinerary": itinerary,
            "total_activity_cost": total_cost,
            "local_tips": local_tips,
            "booking_links": self._get_booking_info(city)
        }

    def _filter_by_interests(
        self,
        activities: Dict[str, List],
        interests: List[str]
    ) -> List[Dict[str, Any]]:
        """Filter activities based on user interests."""
        interest_mapping = {
            "museums": ["culture", "landmarks"],
            "art": ["culture"],
            "history": ["landmarks", "culture"],
            "food": ["food"],
            "cuisine": ["food"],
            "wine": ["food"],
            "nightlife": ["entertainment"],
            "shows": ["entertainment"],
            "architecture": ["landmarks"],
            "nature": ["landmarks"],
            "shopping": ["entertainment"]
        }

        # Get relevant categories
        relevant_categories = set()
        for interest in interests:
            interest_lower = interest.lower()
            for key, categories in interest_mapping.items():
                if key in interest_lower:
                    relevant_categories.update(categories)

        # If no matching interests, include all
        if not relevant_categories:
            relevant_categories = set(activities.keys())

        # Collect and rank activities
        all_activities = []
        for category in relevant_categories:
            if category in activities:
                for activity in activities[category]:
                    activity_copy = activity.copy()
                    activity_copy["category"] = category
                    all_activities.append(activity_copy)

        # Sort by rating
        all_activities.sort(key=lambda x: x.get("rating", 0), reverse=True)

        return all_activities

    def _create_itinerary(
        self,
        activities: List[Dict[str, Any]],
        nights: int,
        budget_per_day: float
    ) -> List[Dict[str, Any]]:
        """Create a day-by-day itinerary."""
        itinerary = []
        used_activities = set()
        days = nights + 1  # Include arrival and departure days partially

        for day in range(1, days + 1):
            day_activities = []
            day_cost = 0
            day_hours = 0
            max_hours = 8 if 1 < day < days else 4  # Less time on arrival/departure

            for activity in activities:
                if activity["name"] in used_activities:
                    continue

                # Parse duration
                duration_str = activity.get("duration", "2 hours")
                try:
                    duration = float(duration_str.split()[0].split("-")[-1])
                except (ValueError, IndexError):
                    duration = 2

                cost = activity.get("cost", 0)

                # Check if activity fits in day
                if (day_hours + duration <= max_hours and
                        day_cost + cost <= budget_per_day):
                    day_activities.append({
                        "name": activity["name"],
                        "duration": activity["duration"],
                        "cost": cost,
                        "category": activity.get("category", "general")
                    })
                    day_hours += duration
                    day_cost += cost
                    used_activities.add(activity["name"])

                if day_hours >= max_hours:
                    break

            if day_activities:
                itinerary.append({
                    "day": day,
                    "activities": day_activities,
                    "total_cost": day_cost,
                    "total_hours": day_hours
                })

        return itinerary

    def _calculate_total_cost(
        self,
        itinerary: List[Dict[str, Any]],
        travelers: int
    ) -> Dict[str, Any]:
        """Calculate total activity costs."""
        total = sum(day.get("total_cost", 0) for day in itinerary)

        return {
            "per_person": total,
            "total_group": total * travelers,
            "currency": "USD",
            "note": "Prices are estimates and may vary"
        }

    def _get_local_tips(self, city: str) -> List[str]:
        """Get local tips for the city."""
        tips = {
            "Paris": [
                "Most museums are free on the first Sunday of each month",
                "Avoid tourist restaurants near major attractions",
                "The metro is the fastest way to get around",
                "Tipping is not expected but appreciated"
            ],
            "Tokyo": [
                "Get a Suica or Pasmo card for easy transport",
                "Convenience store food is excellent and cheap",
                "Bow when greeting locals",
                "Remove shoes when entering homes and some restaurants"
            ],
            "London": [
                "Get an Oyster card for the Tube",
                "Many top museums are free",
                "Look right when crossing streets",
                "Tipping 10-15% is customary in restaurants"
            ]
        }

        return tips.get(city, [
            "Research local customs before visiting",
            "Learn a few phrases in the local language",
            "Keep copies of important documents",
            "Stay aware of your surroundings"
        ])

    def _get_booking_info(self, city: str) -> Dict[str, str]:
        """Get booking information for activities."""
        return {
            "general": "Book popular attractions 1-2 weeks in advance",
            "skip_line": "Consider skip-the-line tickets for major attractions",
            "tours": "Local guided tours often provide better experiences",
            "note": "Check official websites for accurate pricing"
        }

    def _get_generic_recommendations(self, interests: List[str]) -> List[str]:
        """Get generic recommendations when city data is limited."""
        return [
            "Visit the main historical sites",
            "Try local cuisine at recommended restaurants",
            "Explore local markets and neighborhoods",
            "Consider a guided city tour on the first day",
            "Check for local events during your visit"
        ]
