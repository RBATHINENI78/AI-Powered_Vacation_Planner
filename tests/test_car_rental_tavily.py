"""
Quick test for car rental Tavily MCP integration
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mcp_servers.tavily_search import get_tavily_mcp
from tools.booking_tools import estimate_car_rental_cost


def test_car_rental_tavily_search():
    """Test car rental Tavily MCP search"""
    print("\n" + "="*80)
    print("TEST: Car Rental Tavily MCP Search")
    print("="*80)

    try:
        tavily_mcp = get_tavily_mcp()

        if tavily_mcp.client is None:
            print("❌ FAIL: Tavily client not initialized")
            print("   Check TAVILY_API_KEY in .env")
            return False

        print("\nSearching: Car rental in Salt Lake City")
        print("Dates: December 15-20, 2025")

        result = tavily_mcp.search_car_rentals(
            pickup_location="Salt Lake City",
            dropoff_location="Salt Lake City",
            pickup_date="2025-12-15",
            dropoff_date="2025-12-20",
            car_type="economy"
        )

        if "error" in result:
            print(f"❌ FAIL: Search error - {result.get('message', 'Unknown error')}")
            return False

        print("✅ PASS: Tavily car rental search successful")

        # Check search results
        search_results = result.get("results", [])
        print(f"\nSearch Results:")
        print(f"  - Found {len(search_results)} results")

        if search_results:
            print(f"\nSample result:")
            sample = search_results[0]
            print(f"  - Title: {sample.get('title', 'N/A')}")
            print(f"  - URL: {sample.get('url', 'N/A')[:60]}...")

        # Check LLM instruction includes URLs
        llm_instruction = result.get("llm_instruction", "")
        if "Booking URL:" in llm_instruction:
            print(f"\n✅ LLM instruction includes booking URL template")
        else:
            print(f"\n⚠️  WARNING: LLM instruction may not include booking URLs")

        # Extract URLs
        search_urls = [r.get("url", "") for r in search_results if r.get("url")]
        if search_urls:
            print(f"\n✅ URLs extracted from search results:")
            for url in search_urls[:3]:
                print(f"  - {url}")
        else:
            print(f"\n⚠️  No URLs found in search results")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_car_rental_estimate_function():
    """Test estimate_car_rental_cost() with Tavily fallback"""
    print("\n" + "="*80)
    print("TEST: estimate_car_rental_cost() Function")
    print("="*80)

    try:
        print("\nTesting: Salt Lake City, Dec 15-20, 2025")

        result = estimate_car_rental_cost(
            destination="Salt Lake City",
            pickup_date="2025-12-15",
            dropoff_date="2025-12-20",
            car_type="economy"
        )

        source = result.get("source", "unknown")
        print(f"\nData Source: {source}")

        if source == "tavily_mcp":
            print("✅ PASS: Using Tavily MCP search")

            # Check for URLs in LLM instruction
            llm_instruction = result.get("llm_instruction", "")
            if "kayak.com" in llm_instruction or "rentalcars.com" in llm_instruction:
                print("✅ PASS: Booking URLs included in LLM instruction")
            else:
                print("⚠️  WARNING: Booking URLs may not be included")

        elif source == "llm_knowledge":
            print("⚠️  Fell back to LLM knowledge (Tavily may have failed)")
            print("   Check TAVILY_API_KEY or network connection")
        else:
            print(f"❌ FAIL: Unknown data source: {source}")
            return False

        # Display result structure
        print(f"\nResult Structure:")
        print(f"  - Destination: {result.get('destination')}")
        print(f"  - Pickup: {result.get('pickup_date')}")
        print(f"  - Drop-off: {result.get('dropoff_date')}")
        print(f"  - Car Type: {result.get('car_type')}")
        print(f"  - Source: {result.get('source')}")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all car rental tests"""
    print("\n" + "="*80)
    print("CAR RENTAL TAVILY MCP INTEGRATION TESTS")
    print("="*80)

    results = {
        "Tavily MCP Car Rental Search": test_car_rental_tavily_search(),
        "estimate_car_rental_cost() Function": test_car_rental_estimate_function()
    }

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "="*80)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  Some tests failed")

    print("="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
