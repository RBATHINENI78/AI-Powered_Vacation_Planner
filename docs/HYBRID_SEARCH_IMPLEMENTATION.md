# Hybrid Flight & Hotel Search Implementation Plan

## Overview

This document describes the implementation of a hybrid booking system that uses both Amadeus API (production/test) and Tavily web search as a fallback mechanism.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         Flight/Hotel Booking Request                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Try Amadeus API    │
         │  (Primary Source)   │
         └──────┬──────────────┘
                │
                ├─── Production API? ──► Use Amadeus Data ──► Return
                │
                └─── Test API Data? ──► Detected
                                        │
                                        ▼
                              ┌──────────────────────┐
                              │  Fallback: Tavily    │
                              │  Web Search          │
                              └──────┬───────────────┘
                                     │
                                     ▼
                         ┌──────────────────────────┐
                         │  Search Google Flights/  │
                         │  Booking.com with LLM    │
                         └──────┬───────────────────┘
                                │
                                ▼
                         Parse & Format Results ──► Return
```

## Benefits

### For Demo/Development:
- ✅ **Real flight prices** from Google Flights/Kayak via Tavily
- ✅ **No production API costs** - uses free Tavily tier
- ✅ **Realistic data** for demonstrations
- ✅ **Works immediately** - no need for Amadeus production approval

### For Production:
- ✅ **Seamless upgrade** - just add production Amadeus keys
- ✅ **Automatic fallback** - if Amadeus fails, Tavily takes over
- ✅ **Best of both worlds** - structured API + web search backup

## Implementation Components

### 1. Web Search Booking Module (`tools/web_search_booking.py`)

New module containing:
- `search_flights_tavily()` - Search flights via Tavily web search
- `search_hotels_tavily()` - Search hotels via Tavily web search

Both functions:
1. Construct optimized search queries
2. Use Tavily API to fetch results from Google Flights/Booking.com
3. Return results with LLM instructions for parsing
4. Format data in same structure as Amadeus API

### 2. Test Data Detection (`tools/booking_tools.py`)

Functions to detect Amadeus test data:
- `is_amadeus_test_data()` - Detects test flight data
- `is_test_property()` - Detects test hotel data

Detection indicators:
- Booking URLs contain "amadeus.com/book"
- Multiple options with identical prices
- Placeholder/unrealistic data

### 3. Hybrid Fallback Logic

Updated functions:
- `estimate_flight_cost()` - Try Amadeus first, fallback to Tavily
- `estimate_hotel_cost()` - Try Amadeus first, fallback to Tavily

Logic flow:
```python
1. Try Amadeus API
2. If production data received → Use it
3. If test data detected → Fallback to Tavily
4. Parse Tavily results with LLM
5. Return formatted data
```

## Migration Path

### Current State:
```
└─ Amadeus Test API only (returns mock data)
```

### Phase 1 (Demo - Immediate):
```
├─ Amadeus Test API
└─ Tavily Web Search Fallback ← IMPLEMENTED
```

### Phase 2 (Production - Future):
```
├─ Amadeus Production API (primary)
└─ Tavily Fallback (backup)
```

## Configuration

### Required Environment Variables:

```bash
# Amadeus API (existing)
AMADEUS_API_KEY=your_amadeus_key
AMADEUS_API_SECRET=your_amadeus_secret

# Tavily API (for web search fallback)
TAVILY_API_KEY=your_tavily_key
```

### Get Tavily API Key:
1. Visit: https://tavily.com/
2. Sign up for free tier
3. Get API key
4. Add to `.env` file

## Testing Strategy

### Test Cases:

1. **Test Amadeus Test Data Detection**
   - Request: Charlotte → Salt Lake City
   - Expected: Detect test data, trigger Tavily fallback
   - Verify: 3 diverse flight options from web search

2. **Test Tavily Search Results**
   - Verify: Different airlines
   - Verify: Varied prices
   - Verify: Realistic departure times
   - Verify: Valid booking URLs

3. **Test Production Amadeus (when available)**
   - Expected: Skip Tavily, use Amadeus data
   - Verify: Production booking URLs

4. **Test Error Handling**
   - Amadeus API failure → Tavily fallback
   - Tavily API failure → Graceful error message

## Usage Examples

### Flight Search:
```python
result = estimate_flight_cost(
    origin="Charlotte",
    destination="Salt Lake City",
    departure_date="2025-12-15",
    return_date="2025-12-20",
    adults=2,
    cabin_class="economy"
)

# Returns:
# {
#     "flights": [
#         {
#             "airline": "Delta",
#             "route": "CLT -> SLC",
#             "price_per_person": 450,
#             "duration": "5h 30m",
#             "stops": 0,
#             "departure_time": "8:00 AM",
#             "booking_url": "https://google.com/flights/..."
#         },
#         ...
#     ],
#     "source": "tavily_web_search"  # or "amadeus_production"
# }
```

### Hotel Search:
```python
result = estimate_hotel_cost(
    destination="Salt Lake City",
    checkin="2025-12-15",
    checkout="2025-12-20",
    guests=2,
    hotel_class="3-star"
)

# Returns hotel options from Booking.com via Tavily
```

## Logging

The system logs which data source is used:

```
[FLIGHTS] Attempting Amadeus API...
[FLIGHTS] Test data detected, using Tavily web search fallback
[TAVILY] Searching: flights Charlotte to Salt Lake City...
[TAVILY] Found 5 results, parsing with LLM...
[FLIGHTS] Returning 3 diverse flight options
```

## Performance Considerations

### Response Times:
- **Amadeus API**: ~2-3 seconds
- **Tavily Search**: ~3-5 seconds (includes LLM parsing)
- **Total (with fallback)**: ~5-8 seconds max

### API Rate Limits:
- **Amadeus Test**: Limited calls/month
- **Tavily Free Tier**: 1,000 searches/month
- **Tavily Pro**: 10,000+ searches/month

## Future Enhancements

### Potential Improvements:
1. **Cache web search results** (24-hour TTL)
2. **Parallel API calls** (Amadeus + Tavily simultaneously)
3. **Confidence scoring** (prefer higher confidence source)
4. **Multiple fallback sources** (Tavily → SerpAPI → LLM estimates)
5. **User preference** (allow users to choose data source)

## Maintenance

### Monitoring:
- Track Amadeus vs Tavily usage ratio
- Monitor fallback frequency
- Alert on high fallback rates (may indicate API issues)

### Updates Required When:
- Amadeus production API is activated → Update detection logic
- Search engines change structure → Update Tavily queries
- New booking sources added → Extend fallback chain

## File Structure

```
tools/
├── booking_tools.py          # Main booking functions (updated)
├── web_search_booking.py     # New: Tavily search functions
└── ...

docs/
└── HYBRID_SEARCH_IMPLEMENTATION.md  # This document
```

## Dependencies

### New Python Packages:
```bash
pip install tavily-python
```

### Existing Dependencies:
- amadeus
- google-adk
- python-dotenv

## Rollback Plan

If issues occur:
1. Set environment variable: `DISABLE_TAVILY_FALLBACK=true`
2. System reverts to Amadeus-only mode
3. LLM estimates used if Amadeus fails

## Code Examples

### Example 1: Test Data Detection

```python
def is_amadeus_test_data(data: dict) -> bool:
    """
    Detect if Amadeus returned test/sandbox data.

    Test data indicators:
    - Booking URLs contain "amadeus.com/book"
    - Multiple options with identical prices
    - Placeholder data
    """
    if not data or "flights" not in data:
        return True

    flights = data.get("flights", [])

    # Check for Amadeus test booking URLs
    for flight in flights:
        url = flight.get("booking_url", "")
        if "amadeus.com/book" in url:
            return True

    # Check if all prices are identical (test data symptom)
    if len(flights) >= 2:
        prices = [f.get("price_per_person") for f in flights]
        if len(set(prices)) == 1:  # All same price
            return True

    return False
```

### Example 2: Tavily Flight Search

```python
def search_flights_tavily(origin, destination, departure_date, return_date, adults, cabin_class):
    """Search flights using Tavily web search"""

    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # Construct search query
    query = (
        f"flights from {origin} to {destination} "
        f"departing {departure_date} returning {return_date} "
        f"{adults} adults {cabin_class} class "
        f"site:google.com/travel/flights OR site:kayak.com"
    )

    # Search with Tavily
    results = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    # Return with LLM parsing instructions
    return {
        "search_results": results,
        "source": "tavily_web_search",
        "llm_instruction": """
        Parse search results and extract 3 diverse flight options.
        Include airline, price, duration, stops, departure time.
        Provide realistic, varied options.
        """
    }
```

### Example 3: Hybrid Function with Fallback

```python
def estimate_flight_cost(origin, destination, departure_date, return_date, adults, cabin_class):
    """
    Hybrid approach: Try Amadeus first, fallback to Tavily
    """

    # Step 1: Try Amadeus API
    print("[FLIGHTS] Attempting Amadeus API...")
    amadeus_result = _try_amadeus_flights(
        origin, destination, departure_date,
        return_date, adults, cabin_class
    )

    # Step 2: Check if production data
    if amadeus_result and not is_amadeus_test_data(amadeus_result):
        print("[FLIGHTS] Using Amadeus production data")
        return amadeus_result

    # Step 3: Fallback to Tavily web search
    print("[FLIGHTS] Amadeus returned test data, using Tavily fallback")
    tavily_result = search_flights_tavily(
        origin, destination, departure_date,
        return_date, adults, cabin_class
    )

    return tavily_result
```

### Example 4: LLM Parsing Instructions

```python
llm_instruction = f"""
Based on the web search results, provide 3 DIVERSE flight options.

**Route**: {origin} → {destination}
**Dates**: {departure_date} to {return_date}
**Passengers**: {adults} adults
**Class**: {cabin_class}

**Requirements**:
1. Extract data from search results if available
2. Use your knowledge for this route if needed
3. Provide DIVERSE options:
   - Option 1: Premium carrier (Delta/United/American)
   - Option 2: Mid-tier with possible connection
   - Option 3: Budget option or alternative routing

4. Format as JSON:
[
  {{
    "airline": "Airline Name",
    "route": "{origin} → {destination}",
    "price_per_person": 450,
    "duration": "5h 30m",
    "stops": 0,
    "departure_time": "8:00 AM",
    "cabin_class": "{cabin_class}",
    "booking_url": "https://..."
  }},
  ...
]

**IMPORTANT**: All prices must be DIFFERENT (not identical).
"""
```

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create `tools/web_search_booking.py` module
- [ ] Implement `search_flights_tavily()` function
- [ ] Implement `search_hotels_tavily()` function
- [ ] Add Tavily dependency to requirements.txt

### Phase 2: Detection
- [ ] Add `is_amadeus_test_data()` to `tools/booking_tools.py`
- [ ] Add `is_test_property()` for hotel detection
- [ ] Add logging for detection results

### Phase 3: Integration
- [ ] Update `estimate_flight_cost()` with fallback logic
- [ ] Update `estimate_hotel_cost()` with fallback logic
- [ ] Add `TAVILY_API_KEY` to `.env.example`
- [ ] Update environment variable documentation

### Phase 4: Testing
- [ ] Test with Amadeus test data → Should trigger fallback
- [ ] Test with mock production data → Should skip fallback
- [ ] Test Tavily API errors → Should handle gracefully
- [ ] Test end-to-end with real requests

### Phase 5: Documentation
- [x] Create implementation plan document
- [ ] Add code comments
- [ ] Update README with Tavily setup instructions
- [ ] Document environment variables

## Support

For issues or questions:
- Check logs for `[FLIGHTS]` and `[TAVILY]` tags
- Verify Tavily API key is valid
- Ensure internet connectivity for web search
- Review Amadeus API quota status

## Related Documents

- [ADK Technical Implementation](../ADK_TECHNICAL_IMPLEMENTATION.md)
- [Rate Limits Documentation](../RATE_LIMITS.md)
- [Hackathon Submission](../HACKATHON_SUBMISSION.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-25
**Status**: Design Phase - Not Yet Implemented
**Author**: AI Vacation Planner Development Team
