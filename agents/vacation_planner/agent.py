"""
Vacation Planner Agent - ADK Web Interface Compatible
Main agent definition for Google ADK
"""

import os
import re
import httpx
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")

# Define tools for the agent

def get_weather_info(city: str, country: str = "") -> dict:
    """
    Get weather information for a destination using OpenWeather API.

    Args:
        city: Name of the city
        country: Country code (optional)

    Returns:
        Weather information dictionary
    """
    try:
        # Build location query
        location = f"{city},{country}" if country else city

        # Call OpenWeather API
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }

        with httpx.Client() as client:
            response = client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Extract weather info
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                conditions = data["weather"][0]["description"]
                wind_speed = data["wind"]["speed"]

                # Generate packing suggestions based on weather
                pack_suggestions = []
                if temp < 15:
                    pack_suggestions.extend(["Warm jacket", "Layers", "Sweater"])
                elif temp < 25:
                    pack_suggestions.extend(["Light jacket", "Long sleeves"])
                else:
                    pack_suggestions.extend(["Light clothing", "Sun protection"])

                if "rain" in conditions.lower():
                    pack_suggestions.append("Umbrella")
                    pack_suggestions.append("Waterproof shoes")

                pack_suggestions.append("Comfortable walking shoes")

                return {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "weather": {
                        "temperature": f"{temp}°C",
                        "feels_like": f"{feels_like}°C",
                        "conditions": conditions.capitalize(),
                        "humidity": f"{humidity}%",
                        "wind_speed": f"{wind_speed} m/s",
                        "pack": list(set(pack_suggestions))  # Remove duplicates
                    },
                    "source": "openweather_api"
                }
            else:
                return {
                    "city": city,
                    "error": f"API error: {response.status_code}",
                    "source": "error"
                }

    except Exception as e:
        return {
            "city": city,
            "error": str(e),
            "source": "error"
        }


def get_currency_exchange(from_currency: str, to_currency: str, amount: float = 1.0) -> dict:
    """
    Get currency exchange rate and convert amount using ExchangeRate API.

    Args:
        from_currency: Source currency code (e.g., USD)
        to_currency: Target currency code (e.g., EUR)
        amount: Amount to convert

    Returns:
        Currency conversion information
    """
    try:
        # Call ExchangeRate API
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

        with httpx.Client() as client:
            response = client.get(url)

            if response.status_code == 200:
                data = response.json()

                if data.get("result") == "success":
                    rate = data["conversion_rate"]
                    converted = data["conversion_result"]

                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "exchange_rate": rate,
                        "original_amount": amount,
                        "converted_amount": round(converted, 2),
                        "formatted": f"{amount} {from_currency} = {round(converted, 2)} {to_currency}",
                        "last_updated": data.get("time_last_update_utc", "N/A"),
                        "source": "exchangerate_api"
                    }
                else:
                    return {
                        "error": data.get("error-type", "Unknown error"),
                        "source": "error"
                    }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "source": "error"
                }

    except Exception as e:
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "error": str(e),
            "source": "error"
        }


def check_visa_requirements(citizenship: str, destination: str) -> dict:
    """
    Check visa requirements for travel.

    Args:
        citizenship: Country of citizenship (e.g., United States)
        destination: Destination country

    Returns:
        Visa requirement information
    """
    # Simulated visa info for demo
    visa_info = {
        "France": {
            "us_citizens": {
                "visa_required": False,
                "max_stay": "90 days within 180-day period",
                "requirements": ["Valid passport (6 months validity)", "Return ticket", "Proof of accommodation"],
                "notes": "Part of Schengen Area"
            }
        },
        "UK": {
            "us_citizens": {
                "visa_required": False,
                "max_stay": "6 months",
                "requirements": ["Valid passport", "Return ticket", "Proof of funds"],
                "notes": "Electronic Travel Authorization (ETA) may be required"
            }
        },
        "Japan": {
            "us_citizens": {
                "visa_required": False,
                "max_stay": "90 days",
                "requirements": ["Valid passport", "Return ticket", "Proof of funds"],
                "notes": "Visit Japan Web registration recommended"
            }
        }
    }

    # Extract country from destination
    dest_country = destination.split(",")[-1].strip() if "," in destination else destination

    if dest_country in visa_info:
        return {
            "destination": destination,
            "citizenship": citizenship,
            "visa_info": visa_info[dest_country]["us_citizens"],
            "source": "visa_tool"
        }

    return {
        "destination": destination,
        "citizenship": citizenship,
        "visa_info": {
            "visa_required": "Check with embassy",
            "max_stay": "Varies",
            "requirements": ["Valid passport", "Check official sources"],
            "notes": "Please verify with the destination country's embassy"
        },
        "source": "default"
    }


def calculate_budget(
    flights: float,
    hotels_per_night: float,
    nights: int,
    daily_food: float,
    activities: float,
    misc_percent: float = 15.0
) -> dict:
    """
    Calculate total vacation budget.

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
            "flights": flights,
            "accommodation": hotel_total,
            "food": food_total,
            "activities": activities,
            "miscellaneous": round(misc, 2)
        },
        "subtotal": round(subtotal, 2),
        "total": round(total, 2),
        "per_night_average": round(total / nights, 2) if nights > 0 else 0,
        "source": "budget_tool"
    }


def detect_pii(text: str) -> dict:
    """
    Detect and report PII in text (does not modify text).

    Args:
        text: Text to check for PII

    Returns:
        PII detection results
    """
    findings = []

    # Check for SSN
    if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
        findings.append({"type": "SSN", "severity": "high"})

    # Check for credit cards
    if re.search(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', text):
        findings.append({"type": "Credit Card", "severity": "high"})

    # Check for passport numbers
    if re.search(r'\b[A-Z]{1,2}\d{6,9}\b', text):
        findings.append({"type": "Passport Number", "severity": "high"})

    # Check for email
    if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        findings.append({"type": "Email", "severity": "medium"})

    return {
        "pii_detected": len(findings) > 0,
        "findings_count": len(findings),
        "findings": findings,
        "recommendation": "Please avoid sharing sensitive personal information" if findings else "No PII detected"
    }


# Create function tools
weather_tool = FunctionTool(func=get_weather_info)
currency_tool = FunctionTool(func=get_currency_exchange)
visa_tool = FunctionTool(func=check_visa_requirements)
budget_tool = FunctionTool(func=calculate_budget)
pii_tool = FunctionTool(func=detect_pii)

# System instruction for the agent
SYSTEM_INSTRUCTION = """
You are an AI-powered Vacation Planner agent. Your role is to help users plan comprehensive vacations by:

1. **Understanding their needs**: Destination, dates, budget, interests, and travel requirements
2. **Providing weather information**: Use the get_weather_info tool to check destination weather
3. **Currency guidance**: Use get_currency_exchange tool for currency conversion
4. **Visa requirements**: Use check_visa_requirements tool for immigration info
5. **Budget planning**: Use calculate_budget tool for detailed cost estimates
6. **Security**: Use detect_pii tool to check for sensitive information

## Your Approach

When a user asks for vacation planning help:

1. **First**, greet them and ask for key details if not provided:
   - Destination
   - Travel dates
   - Number of travelers
   - Budget range
   - Interests/preferences

2. **Then**, use your tools to gather information:
   - Check weather for the destination
   - Get currency exchange rates
   - Verify visa requirements
   - Calculate estimated budget

3. **Finally**, provide a comprehensive plan including:
   - Destination overview
   - Weather and packing suggestions
   - Accommodation recommendations (budget/mid/luxury)
   - Top activities and attractions
   - Detailed budget breakdown
   - Visa and documentation requirements
   - Practical travel tips

## Important Guidelines

- Always be helpful, friendly, and thorough
- Use tools to provide accurate, specific information
- If users share sensitive info (SSN, credit cards), use detect_pii and advise them to avoid sharing such data
- Provide specific, actionable recommendations
- Include local tips and cultural insights
- Organize information clearly with headings

## Example Interaction

User: "I want to plan a trip to Paris"

You should:
1. Ask about dates, budget, interests if not provided
2. Use get_weather_info("Paris", "France")
3. Use get_currency_exchange("USD", "EUR", 1000)
4. Use check_visa_requirements("United States", "France")
5. Use calculate_budget(...) with estimated costs
6. Provide a complete vacation plan

Remember: You're not just providing information, you're creating an exciting, well-organized travel experience!
"""

# Create the root agent
root_agent = Agent(
    name="vacation_planner",
    model="gemini-2.5-flash-preview-05-20",
    description="AI-powered vacation planning assistant that helps users plan comprehensive trips with weather, currency, visa, and budget information",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        weather_tool,
        currency_tool,
        visa_tool,
        budget_tool,
        pii_tool
    ]
)
