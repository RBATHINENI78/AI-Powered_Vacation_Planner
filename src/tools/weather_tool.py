"""
Weather Tool - Real-time weather data from OpenWeather API
"""

import os
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather_info(city: str, country: str = "") -> Dict[str, Any]:
    """
    Get weather information for a destination using OpenWeather API.

    Args:
        city: Name of the city
        country: Country code (optional, e.g., 'FR', 'US')

    Returns:
        Weather information dictionary with temperature, conditions, etc.
    """
    try:
        location = f"{city},{country}" if country else city

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                conditions = data["weather"][0]["description"]
                wind_speed = data["wind"]["speed"]

                # Generate packing suggestions
                pack_suggestions = _generate_packing_list(temp, conditions)

                return {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "weather": {
                        "temperature": f"{temp}°C",
                        "feels_like": f"{feels_like}°C",
                        "conditions": conditions.capitalize(),
                        "humidity": f"{humidity}%",
                        "wind_speed": f"{wind_speed} m/s",
                        "pack": pack_suggestions
                    },
                    "source": "openweather_api",
                    "status": "success"
                }
            else:
                return {
                    "city": city,
                    "error": f"API error: {response.status_code}",
                    "source": "error",
                    "status": "error"
                }

    except Exception as e:
        return {
            "city": city,
            "error": str(e),
            "source": "error",
            "status": "error"
        }


def get_weather_forecast(city: str, country: str = "", days: int = 5) -> Dict[str, Any]:
    """
    Get weather forecast for multiple days.

    Args:
        city: Name of the city
        country: Country code (optional)
        days: Number of forecast days (max 5 for free tier)

    Returns:
        Weather forecast data
    """
    try:
        location = f"{city},{country}" if country else city

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": days * 8  # 8 readings per day (3-hour intervals)
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                forecasts = []
                for item in data.get("list", [])[:days * 8:8]:  # One per day
                    forecasts.append({
                        "date": item["dt_txt"],
                        "temp": f"{item['main']['temp']}°C",
                        "conditions": item["weather"][0]["description"].capitalize(),
                        "humidity": f"{item['main']['humidity']}%"
                    })

                return {
                    "city": data["city"]["name"],
                    "country": data["city"]["country"],
                    "forecasts": forecasts,
                    "source": "openweather_api",
                    "status": "success"
                }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "status": "error"
                }

    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


def _generate_packing_list(temp: float, conditions: str) -> list:
    """Generate packing suggestions based on weather"""
    suggestions = []

    if temp < 10:
        suggestions.extend(["Heavy coat", "Warm layers", "Sweater", "Gloves"])
    elif temp < 15:
        suggestions.extend(["Warm jacket", "Layers", "Sweater"])
    elif temp < 25:
        suggestions.extend(["Light jacket", "Long sleeves"])
    else:
        suggestions.extend(["Light clothing", "Sun protection", "Sunglasses"])

    if "rain" in conditions.lower():
        suggestions.extend(["Umbrella", "Waterproof jacket", "Waterproof shoes"])

    if "snow" in conditions.lower():
        suggestions.extend(["Winter boots", "Warm hat"])

    suggestions.append("Comfortable walking shoes")

    return list(set(suggestions))
