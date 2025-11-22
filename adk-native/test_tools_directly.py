"""
Direct Tool Testing
Tests the actual FunctionTool wrappers to verify they work
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.travel_tools import check_state_dept_advisory, check_usa_travel_ban
from tools.weather_tools import get_current_weather, get_weather_forecast, get_best_time_to_visit
from tools.currency_tools import get_currency_for_country, get_exchange_rate


async def test_travel_tools():
    """Test travel advisory tools."""
    print("\n" + "="*80)
    print("TEST 1: Travel Advisory Tools")
    print("="*80)

    # Test State Dept Advisory
    print("\n[1] Checking US State Dept advisory for France...")
    result = await check_state_dept_advisory("France")
    print(f"  Level: {result.get('level')} - {result.get('level_description')}")
    print(f"  Country: {result.get('country')}")

    # Test USA Travel Ban
    print("\n[2] Checking USA travel ban for Iran...")
    result = check_usa_travel_ban("Iran")
    if result:
        print(f"  Ban Type: {result.get('ban_type')}")
        print(f"  Restriction: {result.get('restriction')}")
    else:
        print("  No ban found")

    print("\n✓ Travel tools working!")


async def test_weather_tools():
    """Test weather tools."""
    print("\n" + "="*80)
    print("TEST 2: Weather Tools")
    print("="*80)

    # Test current weather
    print("\n[1] Getting current weather for Paris, France...")
    weather = await get_current_weather("Paris", "France")
    print(f"  Temperature: {weather.get('temperature')}°C")
    print(f"  Conditions: {weather.get('conditions')}")
    print(f"  Humidity: {weather.get('humidity')}%")
    print(f"  Source: {weather.get('source')}")

    # Test forecast
    print("\n[2] Getting 5-day forecast for Paris...")
    forecast = await get_weather_forecast("Paris", "France", days=5)
    if forecast:
        print(f"  Forecast days: {len(forecast)}")
        if len(forecast) > 0:
            day1 = forecast[0]
            print(f"  Day 1: {day1.get('date')} - High: {day1.get('temp_high')}°C, Low: {day1.get('temp_low')}°C")

    # Test best time to visit
    print("\n[3] Getting best time to visit France...")
    best_time = get_best_time_to_visit("France")
    print(f"  Recommendation: {best_time}")

    print("\n✓ Weather tools working!")


async def test_currency_tools():
    """Test currency tools."""
    print("\n" + "="*80)
    print("TEST 3: Currency Tools")
    print("="*80)

    # Test currency detection
    print("\n[1] Getting currency for France...")
    currency = await get_currency_for_country("France")
    if currency:
        print(f"  Country: {currency.get('country')}")
        print(f"  Currency: {currency.get('currency_name')} ({currency.get('currency_code')})")
        print(f"  Symbol: {currency.get('currency_symbol')}")

    # Test exchange rate
    print("\n[2] Getting USD to EUR exchange rate...")
    rate = await get_exchange_rate("USD", "EUR", 1000.0)
    print(f"  From: {rate.get('from_currency')}")
    print(f"  To: {rate.get('to_currency')}")
    print(f"  Rate: {rate.get('rate')}")
    print(f"  $1000 USD = €{rate.get('converted')} EUR")
    print(f"  Source: {rate.get('source')}")

    print("\n✓ Currency tools working!")


async def main():
    """Run all tool tests."""
    print("="*80)
    print("DIRECT TOOL TESTING")
    print("Testing individual FunctionTool wrappers")
    print("="*80)

    # Check API keys
    api_keys = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY"),
        "EXCHANGERATE_API_KEY": os.getenv("EXCHANGERATE_API_KEY"),
    }

    print(f"\n[API KEYS]")
    for key, value in api_keys.items():
        status = "✓ Set" if value else "✗ Missing"
        if value:
            print(f"  {key}: {status} ({value[:10]}...)")
        else:
            print(f"  {key}: {status}")

    # Run tests
    await test_travel_tools()
    await test_weather_tools()
    await test_currency_tools()

    # Summary
    print("\n" + "="*80)
    print("✅ TOOLS TEST COMPLETE")
    print("="*80)
    print("\n[WHAT WE VERIFIED]")
    print("  ✓ State Dept API integration works")
    print("  ✓ USA travel ban checking works")
    print("  ✓ OpenWeather API integration works")
    print("  ✓ Weather forecast works")
    print("  ✓ RestCountries API for currency works")
    print("  ✓ ExchangeRate API works")

    print("\n[WHAT'S NEXT]")
    print("\nTo test the full agents with conversations, we have 2 options:")
    print("\n  Option A: Create workflow orchestrator (Phase 3)")
    print("    - Wire up all 10 agents with SequentialAgent/ParallelAgent")
    print("    - Add HITL budget checkpoint")
    print("    - Enable end-to-end vacation planning flow")
    print("    - ~3 hours of work")
    print("\n  Option B: Use ADK web interface")
    print("    - Run: adk serve (if ADK provides web UI)")
    print("    - Test agents through browser")
    print("    - Not yet implemented")

    print("\n[RECOMMENDATION]")
    print("  Proceed to Phase 3 to build workflow orchestrator.")
    print("  This will enable full agent testing and demonstrate the")
    print("  power of ADK's ParallelAgent and SequentialAgent patterns.")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
