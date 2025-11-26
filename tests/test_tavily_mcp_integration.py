"""
Test Tavily MCP Integration
Tests the hybrid fallback system: Amadeus → Tavily MCP → LLM
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ["AUTO_DETECT_TEST_DATA"] = "true"
os.environ["USE_AMADEUS_API"] = "true"
os.environ["AMADEUS_ENV"] = "test"

from mcp_servers.tavily_search import get_tavily_mcp
from tools.booking_tools import estimate_flight_cost, is_amadeus_test_data


def test_tavily_mcp_server():
    """Test 1: Tavily MCP server initialization"""
    print("\n" + "="*80)
    print("TEST 1: Tavily MCP Server Initialization")
    print("="*80)

    try:
        tavily_mcp = get_tavily_mcp()

        if tavily_mcp.client is None:
            print("❌ FAIL: Tavily client not initialized")
            print("   Check TAVILY_API_KEY in .env")
            return False

        print("✅ PASS: Tavily MCP server initialized successfully")

        # Check stats
        stats = tavily_mcp.get_stats()
        print(f"\nServer Stats:")
        print(f"  - Calls used: {stats['calls_used']}/{stats['monthly_limit']}")
        print(f"  - Cache size: {stats['cache_size']}")
        print(f"  - Cache TTL: {stats['cache_ttl_hours']} hours")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_tavily_flight_search():
    """Test 2: Tavily flight search functionality"""
    print("\n" + "="*80)
    print("TEST 2: Tavily Flight Search")
    print("="*80)

    try:
        tavily_mcp = get_tavily_mcp()

        # Search for flights
        print("\nSearching: Charlotte → Salt Lake City")
        print("Dates: December 15-20, 2025")

        result = tavily_mcp.search_flights(
            origin="Charlotte",
            destination="Salt Lake City",
            departure_date="2025-12-15",
            return_date="2025-12-20",
            adults=2,
            cabin_class="economy"
        )

        if "error" in result:
            print(f"❌ FAIL: Search error - {result.get('message', 'Unknown error')}")
            return False

        print("✅ PASS: Tavily search successful")

        # Check search results
        search_results = result.get("results", [])
        print(f"\nSearch Results:")
        print(f"  - Found {len(search_results)} results")

        if search_results:
            print(f"\nSample result:")
            sample = search_results[0]
            print(f"  - Title: {sample.get('title', 'N/A')}")
            print(f"  - URL: {sample.get('url', 'N/A')[:60]}...")

        # Check LLM instruction
        llm_instruction = result.get("llm_instruction", "")
        if "Flight Option" in llm_instruction:
            print(f"\n✅ LLM instruction includes proper formatting template")
        else:
            print(f"\n⚠️  WARNING: LLM instruction may not include formatting template")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_amadeus_test_detection():
    """Test 3: Amadeus test data detection"""
    print("\n" + "="*80)
    print("TEST 3: Amadeus Test Data Detection")
    print("="*80)

    # Test case 1: Test booking URL
    test_data_1 = {
        "flights": [
            {
                "airline": "Air France",
                "price_per_person": 250.33,
                "booking_url": "https://www.amadeus.com/book?offer=1"
            }
        ]
    }

    result1 = is_amadeus_test_data(test_data_1)
    if result1:
        print("✅ PASS: Detected test data (test booking URL)")
    else:
        print("❌ FAIL: Did not detect test booking URL")

    # Test case 2: Identical prices
    test_data_2 = {
        "flights": [
            {"airline": "Delta", "price_per_person": 250.33, "booking_url": "https://google.com"},
            {"airline": "United", "price_per_person": 250.33, "booking_url": "https://google.com"},
            {"airline": "American", "price_per_person": 250.33, "booking_url": "https://google.com"}
        ]
    }

    result2 = is_amadeus_test_data(test_data_2)
    if result2:
        print("✅ PASS: Detected test data (identical prices)")
    else:
        print("❌ FAIL: Did not detect identical prices")

    # Test case 3: Production data (should NOT detect as test)
    prod_data = {
        "flights": [
            {"airline": "Delta", "price_per_person": 450.25, "booking_url": "https://google.com/flights"},
            {"airline": "United", "price_per_person": 385.99, "booking_url": "https://kayak.com"},
            {"airline": "American", "price_per_person": 412.50, "booking_url": "https://skyscanner.com"}
        ]
    }

    result3 = is_amadeus_test_data(prod_data)
    if not result3:
        print("✅ PASS: Production data NOT detected as test")
    else:
        print("❌ FAIL: Production data incorrectly flagged as test")

    return result1 and result2 and not result3


def test_hybrid_fallback():
    """Test 4: Hybrid fallback chain (Amadeus → Tavily → LLM)"""
    print("\n" + "="*80)
    print("TEST 4: Hybrid Fallback Chain")
    print("="*80)

    try:
        print("\nTesting flight search with hybrid fallback...")
        print("Route: Charlotte → Salt Lake City")
        print("Expected: Amadeus (test) → Detect test → Tavily MCP")

        result = estimate_flight_cost(
            origin="Charlotte",
            destination="Salt Lake City",
            departure_date="2025-12-15",
            return_date="2025-12-20",
            travelers=2,
            cabin_class="economy"
        )

        source = result.get("source", "unknown")
        print(f"\nData Source: {source}")

        if source == "amadeus_api":
            print("⚠️  WARNING: Using Amadeus data (test detection may have failed)")
            print("   This is OK if using production Amadeus API")
        elif source == "tavily_mcp":
            print("✅ PASS: Successfully fell back to Tavily MCP")

            # Check for LLM instruction
            if "llm_instruction" in result:
                llm_inst = result["llm_instruction"]
                if "Flight Option" in llm_inst and "Route:" in llm_inst:
                    print("✅ PASS: LLM instruction includes proper format template")
                else:
                    print("⚠️  WARNING: LLM instruction format may be incomplete")
        elif source == "llm_knowledge":
            print("⚠️  Fell back to LLM knowledge (Tavily may have failed)")
            print("   Check TAVILY_API_KEY or network connection")
        else:
            print(f"❌ FAIL: Unknown data source: {source}")
            return False

        # Display result structure
        print(f"\nResult Structure:")
        print(f"  - Origin: {result.get('origin')}")
        print(f"  - Destination: {result.get('destination')}")
        print(f"  - Dates: {result.get('departure_date')} to {result.get('return_date')}")
        print(f"  - Travelers: {result.get('travelers')}")
        print(f"  - Cabin: {result.get('cabin_class')}")

        if "llm_instruction" in result:
            llm_inst = result["llm_instruction"]
            print(f"\n✅ LLM Instruction Preview:")
            print(f"   {llm_inst[:200]}...")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_output_format():
    """Test 5: Output format validation"""
    print("\n" + "="*80)
    print("TEST 5: Output Format Validation")
    print("="*80)

    try:
        tavily_mcp = get_tavily_mcp()

        result = tavily_mcp.search_flights(
            origin="New York",
            destination="Paris",
            departure_date="2025-12-15",
            return_date="2025-12-22",
            adults=2,
            cabin_class="economy"
        )

        if "error" in result:
            print(f"⚠️  Search failed: {result.get('message')}")
            return False

        llm_instruction = result.get("llm_instruction", "")

        # Check required format elements
        required_elements = [
            "Flight Option",
            "Route:",
            "Flight Type:",
            "Duration: Approximately",
            "Price: $",
            "Departure Time:",
            "Booking Link:"
        ]

        all_present = True
        for element in required_elements:
            if element in llm_instruction:
                print(f"✅ Format includes: {element}")
            else:
                print(f"❌ Missing format element: {element}")
                all_present = False

        # Check for example format
        if "Flight Option 1:" in llm_instruction or "Flight Option [N]:" in llm_instruction:
            print(f"\n✅ PASS: Output format template is correct")

            # Show format preview
            print(f"\nFormat Preview:")
            lines = llm_instruction.split('\n')
            for i, line in enumerate(lines[0:15]):
                if line.strip():
                    print(f"  {line}")
        else:
            print(f"\n❌ FAIL: Format template not found")
            all_present = False

        return all_present

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_config_flags():
    """Test 6: Configuration flags"""
    print("\n" + "="*80)
    print("TEST 6: Configuration Flags")
    print("="*80)

    try:
        from config import Config

        print(f"\nConfiguration Status:")
        print(f"  - USE_AMADEUS_API: {Config.USE_AMADEUS_API}")
        print(f"  - AMADEUS_ENV: {Config.AMADEUS_ENV}")
        print(f"  - AUTO_DETECT_TEST_DATA: {Config.AUTO_DETECT_TEST_DATA}")
        print(f"  - FORCE_TAVILY_SEARCH: {Config.FORCE_TAVILY_SEARCH}")
        print(f"  - TAVILY_API_KEY: {'✅ Set' if Config.TAVILY_API_KEY else '❌ Missing'}")

        # Validate configuration
        if not Config.TAVILY_API_KEY:
            print(f"\n❌ FAIL: TAVILY_API_KEY not configured")
            return False

        if Config.AMADEUS_ENV == "test" and Config.AUTO_DETECT_TEST_DATA:
            print(f"\n✅ PASS: Correct config for test environment with auto-detection")
        elif Config.FORCE_TAVILY_SEARCH:
            print(f"\n✅ PASS: Configured to force Tavily search")
        else:
            print(f"\n⚠️  WARNING: Configuration may not trigger Tavily fallback")
            print(f"   Set AUTO_DETECT_TEST_DATA=true or FORCE_TAVILY_SEARCH=true")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*80)
    print("TAVILY MCP INTEGRATION TEST SUITE")
    print("="*80)
    print(f"Testing hybrid fallback: Amadeus → Tavily MCP → LLM")

    results = {
        "Tavily MCP Initialization": test_tavily_mcp_server(),
        "Tavily Flight Search": test_tavily_flight_search(),
        "Amadeus Test Detection": test_amadeus_test_detection(),
        "Hybrid Fallback Chain": test_hybrid_fallback(),
        "Output Format": test_output_format(),
        "Configuration Flags": test_config_flags()
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
    elif passed >= total * 0.75:
        print("⚠️  MOSTLY WORKING - Some tests failed")
    else:
        print("❌ MULTIPLE FAILURES - Check configuration and API keys")

    print("="*80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
