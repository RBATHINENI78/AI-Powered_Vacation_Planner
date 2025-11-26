"""
Tavily MCP Server for Web Search
Provides web search capabilities via Tavily API with caching and rate limiting
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("[TAVILY_MCP] tavily-python not installed. Install with: pip install tavily-python")


class TavilyMCPServer:
    """
    MCP Server for Tavily web search with built-in caching and rate limiting.

    Features:
    - Automatic rate limit tracking (1000 calls/month free tier)
    - Result caching (24-hour TTL)
    - Centralized error handling
    - Query deduplication
    """

    def __init__(self):
        """Initialize Tavily MCP server"""
        self.client: Optional[Any] = None
        self.call_count = 0
        self.monthly_limit = 1000  # Free tier limit
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.cache_ttl_hours = 24

        if not TAVILY_AVAILABLE:
            logger.error("[TAVILY_MCP] Tavily library not available")
            return

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            logger.error("[TAVILY_MCP] TAVILY_API_KEY not found in environment")
            return

        try:
            self.client = TavilyClient(api_key=api_key)
            logger.info("[TAVILY_MCP] TavilyClient initialized successfully")
        except Exception as e:
            logger.error(f"[TAVILY_MCP] Failed to initialize TavilyClient: {e}")

    def _check_cache(self, cache_key: str) -> Optional[Any]:
        """Check if query result is cached and still valid"""
        if cache_key not in self.cache:
            return None

        result, timestamp = self.cache[cache_key]

        # Check if cache is still valid
        if datetime.now() - timestamp < timedelta(hours=self.cache_ttl_hours):
            logger.info(f"[TAVILY_MCP] Cache hit for query: {cache_key[:50]}...")
            return result

        # Cache expired, remove it
        del self.cache[cache_key]
        return None

    def _save_cache(self, cache_key: str, result: Any):
        """Save search result to cache"""
        self.cache[cache_key] = (result, datetime.now())
        logger.info(f"[TAVILY_MCP] Cached result for query: {cache_key[:50]}...")

    def _check_rate_limit(self):
        """Check if rate limit has been exceeded"""
        if self.call_count >= self.monthly_limit:
            raise Exception(
                f"[TAVILY_MCP] Monthly rate limit exceeded ({self.monthly_limit} calls/month). "
                "Upgrade to Tavily Pro for higher limits."
            )

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_domains: Optional[list] = None,
        exclude_domains: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Search the web using Tavily API.

        Args:
            query: Search query string
            search_depth: "basic" or "advanced" (default: "advanced")
            max_results: Maximum number of results (default: 5)
            include_domains: List of domains to include (e.g., ["google.com/travel/flights"])
            exclude_domains: List of domains to exclude

        Returns:
            Dict with search results and metadata
        """
        if not self.client:
            return {
                "error": "Tavily client not initialized",
                "message": "Check TAVILY_API_KEY environment variable"
            }

        # Create cache key
        cache_key = f"{query}_{search_depth}_{max_results}_{include_domains}_{exclude_domains}"

        # Check cache first
        cached_result = self._check_cache(cache_key)
        if cached_result:
            return cached_result

        # Check rate limit
        try:
            self._check_rate_limit()
        except Exception as e:
            logger.error(str(e))
            return {
                "error": "Rate limit exceeded",
                "message": str(e)
            }

        # Perform search
        logger.info(f"[TAVILY_MCP] Searching: {query[:100]}...")

        try:
            results = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )

            # Increment call counter
            self.call_count += 1

            # Cache results
            self._save_cache(cache_key, results)

            logger.info(f"[TAVILY_MCP] Found {len(results.get('results', []))} results")
            logger.info(f"[TAVILY_MCP] API calls used: {self.call_count}/{self.monthly_limit}")

            return results

        except Exception as e:
            logger.error(f"[TAVILY_MCP] Search error: {e}")
            return {
                "error": "Search failed",
                "message": str(e)
            }

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 2,
        cabin_class: str = "economy"
    ) -> Dict[str, Any]:
        """
        Search for flights using Tavily web search.
        Targets Google Flights, Kayak, Skyscanner.

        Args:
            origin: Origin city or airport code
            destination: Destination city or airport code
            departure_date: Departure date (YYYY-MM-DD)
            return_date: Return date for round-trip (YYYY-MM-DD)
            adults: Number of adult passengers
            cabin_class: Cabin class (economy, business, first)

        Returns:
            Search results with LLM parsing instructions
        """
        # Construct optimized query
        if return_date:
            query = (
                f"flights from {origin} to {destination} "
                f"departing {departure_date} returning {return_date} "
                f"{adults} adults {cabin_class} class"
            )
        else:
            query = (
                f"one-way flights from {origin} to {destination} "
                f"{departure_date} {adults} adults {cabin_class}"
            )

        logger.info(f"[TAVILY_MCP] Flight search: {origin} → {destination}")

        # Search with flight-specific domains
        results = self.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_domains=[
                "google.com/travel/flights",
                "kayak.com",
                "skyscanner.com"
            ]
        )

        if "error" in results:
            return results

        # Add LLM parsing instructions
        results["llm_instruction"] = f"""
Based on the web search results, provide 3 DIVERSE flight options from {origin} to {destination}.

**CRITICAL FORMATTING - MUST FOLLOW EXACTLY:**

For EACH flight option, use this EXACT format:

```
Flight Option [N]: [Airline Name]

Route: [Origin Airport] ([CODE]) → [Destination Airport] ([CODE])
Flight Type: [Direct/1 stop/2 stops]
Duration: Approximately [X] hours [XX] minutes
Price: $[XXX.XX] per person ($[XXX.XX] total) ({cabin_class.title()})
Departure Time: [HH:MM AM/PM]
Booking Link: https://google.com/travel/flights or https://kayak.com/...
```

**Example:**
```
Flight Option 1: Delta Air Lines

Route: Charlotte (CLT) → Salt Lake City (SLC)
Flight Type: Direct
Duration: Approximately 5 hours 30 minutes
Price: $450.25 per person ($900.50 total) (Economy)
Departure Time: 8:00 AM
Booking Link: https://google.com/travel/flights/search?q=CLT+to+SLC
```

**REQUIREMENTS:**
1. Extract data from search results if available
2. Use your knowledge of this route if search data insufficient
3. Provide DIVERSE options:
   - Option 1: Premium carrier (Delta/United/American), possibly direct
   - Option 2: Mid-tier option, may have 1 connection
   - Option 3: Budget or alternative routing

4. **CRITICAL**: All 3 options must have DIFFERENT prices (not identical!)
5. Include realistic airport codes in parentheses
6. Duration format: "Approximately X hours XX minutes"
7. Price format: "$XXX.XX per person ($XXX.XX total) (Class)"
8. Use actual booking URLs from search results if available

**Route Details:**
- Origin: {origin}
- Destination: {destination}
- Departure: {departure_date}
- Return: {return_date if return_date else 'One-way'}
- Adults: {adults}
- Cabin: {cabin_class}

Provide exactly 3 flight options with the format above.
"""

        return results

    def search_hotels(
        self,
        destination: str,
        checkin: str,
        checkout: str,
        guests: int = 2,
        hotel_class: str = "3-star"
    ) -> Dict[str, Any]:
        """
        Search for hotels using Tavily web search.
        Targets Booking.com, Hotels.com, Expedia.

        Args:
            destination: City or location
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            guests: Number of guests
            hotel_class: Hotel class (2-star, 3-star, 4-star, 5-star)

        Returns:
            Search results with LLM parsing instructions
        """
        query = (
            f"{hotel_class} hotels in {destination} "
            f"{checkin} to {checkout} "
            f"{guests} guests"
        )

        logger.info(f"[TAVILY_MCP] Hotel search: {destination} ({hotel_class})")

        # Search with hotel-specific domains
        results = self.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_domains=[
                "booking.com",
                "hotels.com",
                "expedia.com"
            ]
        )

        if "error" in results:
            return results

        # Calculate nights
        try:
            from datetime import datetime
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
            nights = (checkout_date - checkin_date).days
        except:
            nights = 5  # Default

        # Add LLM parsing instructions
        results["llm_instruction"] = f"""
Based on the web search results, provide 3 DIVERSE {hotel_class} hotel options in {destination}.

Extract hotel names and prices from search results if available. Use your knowledge if needed.

Provide DIVERSE options within {hotel_class} category:
- Different neighborhoods/areas
- Range of prices
- Different amenities

Format each hotel exactly as:
- Hotel Name
- $XX/night ($XXX total for {nights} nights)
- Star rating, room type
- Location/area
- 2-3 key amenities

**Destination:** {destination}
**Dates:** {checkin} to {checkout} ({nights} nights)
**Guests:** {guests}
**Class:** {hotel_class}
"""

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "calls_used": self.call_count,
            "monthly_limit": self.monthly_limit,
            "remaining_calls": self.monthly_limit - self.call_count,
            "cache_size": len(self.cache),
            "cache_ttl_hours": self.cache_ttl_hours
        }


# Global MCP server instance
_tavily_mcp_server: Optional[TavilyMCPServer] = None


def get_tavily_mcp() -> TavilyMCPServer:
    """Get or create global Tavily MCP server instance"""
    global _tavily_mcp_server
    if _tavily_mcp_server is None:
        _tavily_mcp_server = TavilyMCPServer()
    return _tavily_mcp_server
