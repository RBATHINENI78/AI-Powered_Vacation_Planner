"""
Weather Tools - Date-aware weather forecasting for travel dates
Uses OpenWeather API to fetch weather conditions for specific travel dates
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger


async def get_weather_for_travel_dates(
    city: str,
    country: str = "",
    start_date: str = "",
    end_date: str = ""
) -> Dict[str, Any]:
    """
    Get weather forecast for specific travel dates.

    IMPORTANT: Only call this for FUTURE travel dates within the next 16 days.
    Do NOT fetch current weather or generic forecasts.

    Args:
        city: Destination city name
        country: Country name (optional, improves accuracy)
        start_date: Travel start date in YYYY-MM-DD format
        end_date: Travel end date in YYYY-MM-DD format

    Returns:
        Weather forecast for the travel period with:
        - Daily temperature ranges
        - Weather conditions
        - Packing recommendations
        - Weather warnings
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    location = f"{city},{country}" if country else city

    # Parse travel dates
    try:
        if start_date:
            travel_start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            # If no date provided, use LLM knowledge
            logger.warning(f"[WEATHER] No start_date provided for {city}, will use LLM knowledge")
            return {
                "location": location,
                "travel_dates": "Not specified",
                "source": "llm_knowledge",
                "note": "No travel dates provided - LLM will estimate based on destination and season"
            }

        if end_date:
            travel_end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            travel_end = travel_start + timedelta(days=7)  # Default 1 week

        days_until_trip = (travel_start - datetime.now()).days

        logger.info(f"[WEATHER] Fetching forecast for {city}: {start_date} to {end_date} ({days_until_trip} days away)")

    except ValueError as e:
        logger.error(f"[WEATHER] Invalid date format: {e}")
        return {
            "location": location,
            "error": "Invalid date format. Use YYYY-MM-DD",
            "source": "error"
        }

    # OpenWeather free tier: 5-day/3-hour forecast (up to 5 days ahead)
    # For dates beyond 5 days, use historical climate data + LLM knowledge
    if days_until_trip > 5:
        logger.info(f"[WEATHER] Travel is {days_until_trip} days away, using climate data + LLM knowledge")
        return {
            "location": location,
            "travel_dates": f"{start_date} to {end_date}",
            "days_until_trip": days_until_trip,
            "source": "climate_knowledge",
            "note": f"Travel is {days_until_trip} days away. Using historical climate data for {city} in {travel_start.strftime('%B')}",
            "llm_instruction": f"""
Provide typical weather conditions for {city}, {country} in {travel_start.strftime('%B %Y')}.

Include:
- Typical temperature range for this month
- Common weather conditions (rain, snow, sun, etc.)
- Packing recommendations
- Any seasonal considerations
"""
        }

    # For trips within 5 days, fetch actual forecast
    if not api_key:
        logger.warning("[WEATHER] OPENWEATHER_API_KEY not set, using LLM knowledge")
        return {
            "location": location,
            "travel_dates": f"{start_date} to {end_date}",
            "source": "llm_knowledge",
            "note": "API key not set - LLM will estimate"
        }

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",
            "cnt": 40  # 5 days * 8 (3-hour intervals)
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Filter forecast to travel dates only
                travel_forecast = []
                for item in data["list"]:
                    forecast_date = datetime.fromtimestamp(item["dt"])
                    if travel_start <= forecast_date <= travel_end:
                        travel_forecast.append({
                            "date": forecast_date.strftime("%Y-%m-%d"),
                            "time": forecast_date.strftime("%H:%M"),
                            "temp": item["main"]["temp"],
                            "feels_like": item["main"]["feels_like"],
                            "temp_min": item["main"]["temp_min"],
                            "temp_max": item["main"]["temp_max"],
                            "conditions": item["weather"][0]["description"],
                            "humidity": item["main"]["humidity"],
                            "wind_speed": item["wind"]["speed"]
                        })

                # Summarize by day
                daily_summary = {}
                for entry in travel_forecast:
                    date = entry["date"]
                    if date not in daily_summary:
                        daily_summary[date] = {
                            "date": date,
                            "temps": [],
                            "conditions": [],
                            "humidity": []
                        }
                    daily_summary[date]["temps"].append(entry["temp"])
                    daily_summary[date]["conditions"].append(entry["conditions"])
                    daily_summary[date]["humidity"].append(entry["humidity"])

                daily_forecast = []
                for date, data in daily_summary.items():
                    daily_forecast.append({
                        "date": date,
                        "temp_high": max(data["temps"]),
                        "temp_low": min(data["temps"]),
                        "conditions": max(set(data["conditions"]), key=data["conditions"].count),
                        "avg_humidity": sum(data["humidity"]) / len(data["humidity"])
                    })

                logger.info(f"[WEATHER] Forecast for {city}: {len(daily_forecast)} days")

                return {
                    "location": location,
                    "travel_dates": f"{start_date} to {end_date}",
                    "days_until_trip": days_until_trip,
                    "daily_forecast": daily_forecast,
                    "source": "openweather_api",
                    "forecast_type": "5-day_actual"
                }
            else:
                logger.error(f"[WEATHER] API error {response.status_code}")
                return _get_fallback_weather_for_dates(city, start_date, end_date)

    except Exception as e:
        logger.error(f"[WEATHER] Error: {e}")
        return _get_fallback_weather_for_dates(city, start_date, end_date)


def _get_fallback_weather_for_dates(city: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Provide fallback weather data when API unavailable."""
    try:
        travel_start = datetime.strptime(start_date, "%Y-%m-%d")
        month = travel_start.strftime("%B")
    except:
        month = "the travel month"

    return {
        "location": city,
        "travel_dates": f"{start_date} to {end_date}",
        "source": "llm_knowledge",
        "note": f"Weather API unavailable - LLM will estimate typical conditions for {city} in {month}",
        "llm_instruction": f"""
Provide typical weather conditions for {city} in {month}.

Include:
- Typical temperature range
- Common weather patterns
- Packing recommendations
- Seasonal considerations
"""
    }
