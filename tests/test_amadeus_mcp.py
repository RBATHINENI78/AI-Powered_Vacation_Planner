"""
Test Amadeus MCP Server Authentication and API Calls
Run with: python tests/test_amadeus_mcp.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from mcp_servers.amadeus_client import AmadeusClient
from loguru import logger

# Configure logger for test output
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


async def test_authentication():
    """Test 1: Amadeus OAuth2 Authentication"""
    logger.info("=" * 80)
    logger.info("TEST 1: Amadeus Authentication")
    logger.info("=" * 80)

    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")

    logger.info(f"Client ID configured: {bool(client_id and client_id != 'your_amadeus_client_id')}")
    logger.info(f"Client Secret configured: {bool(client_secret)}")

    if not client_id or client_id == "your_amadeus_client_id":
        logger.error("❌ AMADEUS_CLIENT_ID not configured in .env")
        return False

    if not client_secret:
        logger.error("❌ AMADEUS_CLIENT_SECRET not configured in .env")
        return False

    try:
        client = AmadeusClient()
        token = await client._get_token()

        if token:
            logger.success(f"✅ Authentication successful! Token: {token[:20]}...")
            logger.info(f"Token expires: {client.token_expires}")
            return True
        else:
            logger.error("❌ Authentication failed - no token received")
            return False

    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        return False


async def test_airport_code_lookup():
    """Test 2: Airport Code Lookup"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Airport Code Lookup")
    logger.info("=" * 80)

    test_cities = [
        "Charlotte, USA",
        "Salt Lake City, USA",
        "New York",
        "Paris",
        "London"
    ]

    client = AmadeusClient()
    results = {}

    for city in test_cities:
        try:
            logger.info(f"\nLooking up airport code for: {city}")
            result = await client.get_airport_code(city)

            if result.get("code"):
                logger.success(f"✅ {city} → {result['code']} ({result.get('name', 'N/A')})")
                results[city] = result
            else:
                logger.error(f"❌ {city} → No airport code found: {result.get('error', 'Unknown error')}")
                results[city] = result

        except Exception as e:
            logger.error(f"❌ Error looking up {city}: {e}")
            results[city] = {"error": str(e)}

    success_count = sum(1 for r in results.values() if r.get("code"))
    logger.info(f"\n✓ Success Rate: {success_count}/{len(test_cities)}")

    return success_count > 0


async def test_flight_search():
    """Test 3: Flight Search"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Flight Search (CLT → SLC)")
    logger.info("=" * 80)

    client = AmadeusClient()

    # Test flight search
    try:
        logger.info("Searching flights: Charlotte (CLT) → Salt Lake City (SLC)")
        logger.info("Date: 2026-03-15 to 2026-03-22")
        logger.info("Adults: 2")

        result = await client.search_flights(
            origin="CLT",
            destination="SLC",
            departure_date="2026-03-15",
            return_date="2026-03-22",
            adults=2,
            max_results=5
        )

        if "error" in result:
            logger.error(f"❌ Flight search failed: {result['error']}")
            logger.error(f"Status code: {result.get('status', 'N/A')}")
            return False

        if "data" in result and len(result["data"]) > 0:
            flight_count = len(result["data"])
            logger.success(f"✅ Found {flight_count} flight options")

            # Show first flight details
            first_flight = result["data"][0]
            price = first_flight.get("price", {})
            logger.info(f"\nSample Flight:")
            logger.info(f"  Price: {price.get('total', 'N/A')} {price.get('currency', 'USD')}")
            logger.info(f"  Number of segments: {len(first_flight.get('itineraries', [])[0].get('segments', []))}")

            return True
        else:
            logger.warning("⚠️  No flights found in response")
            return False

    except Exception as e:
        logger.error(f"❌ Flight search error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_hotel_search():
    """Test 4: Hotel Search"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Hotel Search (Salt Lake City)")
    logger.info("=" * 80)

    client = AmadeusClient()

    try:
        # First get city code
        logger.info("Step 1: Getting city code for Salt Lake City...")
        city_result = await client.get_city_code("Salt Lake City, USA")

        if not city_result.get("code"):
            logger.error(f"❌ Could not get city code: {city_result.get('error', 'Unknown error')}")
            return False

        city_code = city_result["code"]
        logger.success(f"✅ City code: {city_code}")

        # Search hotels
        logger.info(f"\nStep 2: Searching hotels in {city_code}...")
        logger.info("Check-in: 2026-03-15, Check-out: 2026-03-22")
        logger.info("Adults: 2, Rooms: 1")

        result = await client.search_hotels(
            city_code=city_code,
            check_in="2026-03-15",
            check_out="2026-03-22",
            adults=2,
            rooms=1,
            max_results=5
        )

        if "error" in result:
            logger.error(f"❌ Hotel search failed: {result['error']}")
            logger.error(f"Status code: {result.get('status', 'N/A')}")
            return False

        if "data" in result and len(result["data"]) > 0:
            hotel_count = len(result["data"])
            logger.success(f"✅ Found {hotel_count} hotel options")

            # Show first hotel details
            first_hotel = result["data"][0]
            hotel_info = first_hotel.get("hotel", {})
            offers = first_hotel.get("offers", [])

            logger.info(f"\nSample Hotel:")
            logger.info(f"  Name: {hotel_info.get('name', 'N/A')}")
            if offers:
                price = offers[0].get("price", {})
                logger.info(f"  Price: {price.get('total', 'N/A')} {price.get('currency', 'USD')}")

            return True
        else:
            logger.warning("⚠️  No hotels found in response")
            return False

    except Exception as e:
        logger.error(f"❌ Hotel search error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def test_quota_limits():
    """Test 5: Check API Quota/Rate Limiting"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Quota and Rate Limit Check")
    logger.info("=" * 80)

    logger.info("Making 3 rapid API calls to test rate limiting...")

    client = AmadeusClient()
    success_count = 0

    for i in range(3):
        try:
            logger.info(f"\nAttempt {i+1}/3...")
            result = await client.get_airport_code("New York")

            if result.get("code"):
                logger.success(f"✅ Call {i+1} successful")
                success_count += 1
            else:
                logger.error(f"❌ Call {i+1} failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                logger.warning(f"⚠️  Rate limit hit on call {i+1}")
            else:
                logger.error(f"❌ Call {i+1} error: {e}")

    logger.info(f"\n✓ Success Rate: {success_count}/3 calls")

    if success_count == 3:
        logger.success("✅ No rate limiting issues detected")
        return True
    elif success_count > 0:
        logger.warning("⚠️  Some calls failed - possible rate limiting")
        return True
    else:
        logger.error("❌ All calls failed - check credentials and quota")
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 80)
    logger.info("AMADEUS MCP SERVER TEST SUITE")
    logger.info("=" * 80)

    results = {
        "Authentication": False,
        "Airport Lookup": False,
        "Flight Search": False,
        "Hotel Search": False,
        "Rate Limits": False
    }

    # Run tests sequentially
    results["Authentication"] = await test_authentication()

    if results["Authentication"]:
        results["Airport Lookup"] = await test_airport_code_lookup()
        results["Flight Search"] = await test_flight_search()
        results["Hotel Search"] = await test_hotel_search()
        results["Rate Limits"] = await test_quota_limits()
    else:
        logger.error("\n❌ Authentication failed - skipping remaining tests")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name:20s}: {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    logger.info("=" * 80)
    logger.info(f"Overall: {passed_count}/{total_count} tests passed")
    logger.info("=" * 80)

    if passed_count == total_count:
        logger.success("\n🎉 All tests passed! Amadeus MCP is working correctly.")
        return 0
    elif passed_count > 0:
        logger.warning(f"\n⚠️  {total_count - passed_count} test(s) failed. Check logs above.")
        return 1
    else:
        logger.error("\n❌ All tests failed. Please check:")
        logger.error("  1. AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in .env")
        logger.error("  2. Amadeus test API credentials are valid")
        logger.error("  3. Internet connection")
        logger.error("  4. API quota/rate limits")
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
