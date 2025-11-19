"""
Destination Intelligence Agent - Weather Analysis and Destination Research
Uses external APIs (MCP-style) for real-time data
"""

import os
import httpx
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
from .base_agent import BaseAgent


class DestinationIntelligenceAgent(BaseAgent):
    """
    Destination Intelligence Agent for weather and destination analysis.
    Integrates with external weather APIs (MCP pattern).
    """

    def __init__(self):
        super().__init__(
            name="destination_intelligence",
            description="Analyzes weather and destination conditions"
        )

        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"

        # Register A2A message handlers
        self.register_message_handler("weather_request", self._handle_weather_request)

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze destination weather and conditions.

        Args:
            input_data: Contains 'city', 'country', and optional 'dates'

        Returns:
            Comprehensive destination analysis
        """
        city = input_data.get("city", "")
        country = input_data.get("country", "")
        dates = input_data.get("dates", {})

        if not city:
            return {
                "status": "error",
                "error": "City is required"
            }

        # Get current weather
        current_weather = await self._get_current_weather(city, country)

        # Get forecast
        forecast = await self._get_forecast(city, country)

        # Analyze conditions
        analysis = self._analyze_conditions(current_weather, forecast, dates)

        # Generate packing suggestions
        packing_list = self._generate_packing_list(current_weather, forecast)

        # Send advisory to Immigration Agent if severe weather detected
        if analysis.get("severe_weather"):
            self.send_message(
                to_agent="immigration_specialist",
                message_type="weather_advisory",
                content={
                    "destination": f"{city}, {country}",
                    "advisory_type": "severe_weather",
                    "conditions": analysis.get("warnings", []),
                    "recommendation": "Check for travel restrictions"
                },
                priority="high"
            )

        return {
            "status": "success",
            "destination": {
                "city": city,
                "country": country
            },
            "current_weather": current_weather,
            "forecast": forecast,
            "analysis": analysis,
            "packing_list": packing_list,
            "best_time_to_visit": self._get_best_time(city, country)
        }

    async def _get_current_weather(self, city: str, country: str) -> Dict[str, Any]:
        """Get current weather from OpenWeather API."""
        try:
            location = f"{city},{country}" if country else city
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "conditions": data["weather"][0]["description"],
                        "wind_speed": data["wind"]["speed"],
                        "visibility": data.get("visibility", "N/A"),
                        "source": "openweather_api"
                    }
                else:
                    logger.error(f"Weather API error: {response.status_code}")
                    return self._get_fallback_weather(city)

        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return self._get_fallback_weather(city)

    async def _get_forecast(self, city: str, country: str) -> List[Dict[str, Any]]:
        """Get 5-day weather forecast."""
        try:
            location = f"{city},{country}" if country else city
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 40  # 5 days * 8 (3-hour intervals)
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    daily_forecast = []

                    # Group by day
                    days = {}
                    for item in data["list"]:
                        date = item["dt_txt"].split(" ")[0]
                        if date not in days:
                            days[date] = {
                                "date": date,
                                "temps": [],
                                "conditions": [],
                                "humidity": []
                            }
                        days[date]["temps"].append(item["main"]["temp"])
                        days[date]["conditions"].append(item["weather"][0]["main"])
                        days[date]["humidity"].append(item["main"]["humidity"])

                    # Calculate daily summaries
                    for date, day_data in list(days.items())[:5]:
                        daily_forecast.append({
                            "date": date,
                            "temp_high": max(day_data["temps"]),
                            "temp_low": min(day_data["temps"]),
                            "conditions": max(set(day_data["conditions"]), key=day_data["conditions"].count),
                            "avg_humidity": sum(day_data["humidity"]) / len(day_data["humidity"])
                        })

                    return daily_forecast
                else:
                    return []

        except Exception as e:
            logger.error(f"Forecast fetch error: {e}")
            return []

    def _analyze_conditions(
        self,
        current: Dict[str, Any],
        forecast: List[Dict[str, Any]],
        dates: Dict[str, str]
    ) -> Dict[str, Any]:
        """Analyze weather conditions for travel."""
        warnings = []
        severe_weather = False

        temp = current.get("temperature", 20)
        conditions = current.get("conditions", "").lower()

        # Check for extreme temperatures
        if temp > 35:
            warnings.append("Extreme heat warning - stay hydrated")
            severe_weather = True
        elif temp < 0:
            warnings.append("Freezing conditions - pack warm clothing")
            severe_weather = True

        # Check for adverse conditions
        if any(w in conditions for w in ["storm", "thunder", "tornado", "hurricane"]):
            warnings.append(f"Severe weather alert: {conditions}")
            severe_weather = True
        elif "rain" in conditions:
            warnings.append("Rain expected - bring waterproof gear")
        elif "snow" in conditions:
            warnings.append("Snow conditions - check road accessibility")

        # Determine overall rating
        if severe_weather:
            rating = "poor"
        elif warnings:
            rating = "fair"
        else:
            rating = "excellent"

        return {
            "travel_conditions": rating,
            "warnings": warnings,
            "severe_weather": severe_weather,
            "recommendation": self._get_travel_recommendation(rating, warnings)
        }

    def _generate_packing_list(
        self,
        current: Dict[str, Any],
        forecast: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate packing list based on weather."""
        essentials = ["Passport", "Travel documents", "Phone charger", "Medications"]
        clothing = []
        accessories = []

        temp = current.get("temperature", 20)
        conditions = current.get("conditions", "").lower()

        # Temperature-based clothing
        if temp < 10:
            clothing.extend(["Heavy coat", "Sweaters", "Thermal underwear", "Gloves", "Scarf"])
        elif temp < 20:
            clothing.extend(["Light jacket", "Long-sleeve shirts", "Jeans", "Light sweater"])
        else:
            clothing.extend(["T-shirts", "Shorts", "Light dresses", "Sandals"])

        # Weather-based accessories
        if "rain" in conditions:
            accessories.extend(["Umbrella", "Rain jacket", "Waterproof shoes"])
        if temp > 25:
            accessories.extend(["Sunscreen", "Sunglasses", "Hat", "Reusable water bottle"])
        if "snow" in conditions:
            accessories.extend(["Snow boots", "Hand warmers"])

        # Always include
        accessories.append("Comfortable walking shoes")

        return {
            "essentials": essentials,
            "clothing": list(set(clothing)),
            "accessories": list(set(accessories))
        }

    def _get_best_time(self, city: str, country: str) -> str:
        """Get best time to visit destination."""
        # Simplified recommendations (would use historical data in production)
        best_times = {
            "France": "April to June or September to November",
            "Japan": "March to May or September to November",
            "Italy": "April to June or September to October",
            "UK": "May to September",
            "Thailand": "November to February",
            "Australia": "September to November or March to May"
        }
        return best_times.get(country, "Year-round with seasonal variations")

    def _get_fallback_weather(self, city: str) -> Dict[str, Any]:
        """Provide fallback weather data."""
        return {
            "temperature": 20,
            "feels_like": 20,
            "humidity": 60,
            "conditions": "Partly cloudy",
            "wind_speed": 10,
            "source": "fallback_estimate",
            "note": "Real-time data unavailable"
        }

    def _get_travel_recommendation(self, rating: str, warnings: List[str]) -> str:
        """Generate travel recommendation."""
        if rating == "excellent":
            return "Perfect conditions for travel. Enjoy your trip!"
        elif rating == "fair":
            return f"Good conditions with minor concerns: {', '.join(warnings)}"
        else:
            return f"Consider postponing or prepare for: {', '.join(warnings)}"

    def _handle_weather_request(self, message) -> Dict[str, Any]:
        """Handle A2A weather requests."""
        logger.info(f"[A2A] Processing weather request from {message.from_agent}")
        return {"status": "acknowledged", "will_process": True}
