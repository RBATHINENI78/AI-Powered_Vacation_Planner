"""
Weather Tools - FunctionTool wrappers for weather API integration
"""

import os
import httpx
from typing import Dict, Any, List
from loguru import logger


async def get_current_weather(city: str, country: str = "") -> Dict[str, Any]:
    """
    Get current weather conditions for a destination.

    Args:
        city: City name
        country: Country name (optional, improves accuracy)

    Returns:
        Current weather data including temperature, conditions, humidity
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("[WEATHER] OPENWEATHER_API_KEY not set, using fallback data")
        return _get_fallback_weather(city)

    try:
        location = f"{city},{country}" if country else city
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "source": "openweather_api",
                    "location": f"{city}, {country}"
                }
            else:
                logger.error(f"[WEATHER] API error {response.status_code}")
                return _get_fallback_weather(city)

    except Exception as e:
        logger.error(f"[WEATHER] Error: {e}")
        return _get_fallback_weather(city)


async def get_weather_forecast(city: str, country: str = "", days: int = 5) -> List[Dict[str, Any]]:
    """
    Get weather forecast for upcoming days.

    Args:
        city: City name
        country: Country name (optional)
        days: Number of days to forecast (default 5)

    Returns:
        Daily weather forecast
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.warning("[WEATHER] OPENWEATHER_API_KEY not set, skipping forecast")
        return []

    try:
        location = f"{city},{country}" if country else city
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
            "cnt": days * 8  # 8 intervals per day (3-hour intervals)
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                daily_forecast = []

                # Group by day
                days_data = {}
                for item in data["list"]:
                    date = item["dt_txt"].split(" ")[0]
                    if date not in days_data:
                        days_data[date] = {
                            "date": date,
                            "temps": [],
                            "conditions": [],
                            "humidity": []
                        }
                    days_data[date]["temps"].append(item["main"]["temp"])
                    days_data[date]["conditions"].append(item["weather"][0]["main"])
                    days_data[date]["humidity"].append(item["main"]["humidity"])

                # Calculate daily summaries
                for date, day_data in list(days_data.items())[:days]:
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
        logger.error(f"[FORECAST] Error: {e}")
        return []


def get_best_time_to_visit(country: str) -> str:
    """
    Get recommended best time to visit a country.

    Args:
        country: Country name

    Returns:
        Best travel months/seasons
    """
    # Simplified recommendations - would use climate DB in production
    best_times = {
        "France": "April to June or September to November (mild weather, fewer tourists)",
        "Japan": "March to May (cherry blossoms) or September to November (fall colors)",
        "Italy": "April to June or September to October (pleasant temps, less crowded)",
        "United Kingdom": "May to September (warmer weather, longer days)",
        "UK": "May to September (warmer weather, longer days)",
        "Thailand": "November to February (cool and dry season)",
        "Australia": "September to November or March to May (spring/fall, mild temps)",
        "Spain": "April to June or September to October (warm but not extreme)",
        "Greece": "April to June or September to October (warm, ideal for sightseeing)",
        "Iceland": "June to August (midnight sun, warmer weather)",
        "New Zealand": "December to February (summer season)",
        "Brazil": "December to March (summer, beach season)",
        "India": "October to March (cooler, post-monsoon)",
        "China": "April to May or September to October (mild weather)",
        "Egypt": "October to April (cooler temperatures)",
        "Mexico": "December to April (dry season)",
        "Canada": "June to September (warmer weather)",
        "Norway": "May to September (midnight sun in summer)",
        "Switzerland": "June to September (hiking, pleasant weather)",
        "Germany": "May to September (warm weather, festivals)",
    }

    return best_times.get(country, "Year-round with seasonal variations - check specific region climate")


def _get_fallback_weather(city: str) -> Dict[str, Any]:
    """Provide fallback weather data when API unavailable."""
    return {
        "temperature": 20,
        "feels_like": 20,
        "humidity": 60,
        "conditions": "Partly cloudy",
        "wind_speed": 10,
        "source": "fallback_estimate",
        "location": city,
        "note": "Real-time data unavailable - using estimate"
    }
