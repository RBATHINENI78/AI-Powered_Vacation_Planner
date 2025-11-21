"""
Travel Advisory Agent - Checks travel warnings and restrictions BEFORE planning
Runs first in the workflow to block travel to restricted destinations
Includes Tavily search for global events and safety alerts
"""

import os
import httpx
from typing import Dict, Any, List, Optional
from loguru import logger
from .base_agent import BaseAgent

# Try to import Tavily
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("Tavily not installed. Global events search will be disabled.")


# USA Travel Ban Countries (Effective June 9, 2025)
# Source: https://travel.state.gov
USA_FULL_BAN_COUNTRIES = [
    "Afghanistan", "Burma", "Myanmar", "Chad", "Republic of the Congo",
    "Congo", "Equatorial Guinea", "Eritrea", "Haiti", "Iran",
    "Libya", "Somalia", "Sudan", "Yemen"
]

USA_PARTIAL_BAN_COUNTRIES = [
    "Burundi", "Cuba", "Laos", "Sierra Leone", "Togo",
    "Turkmenistan", "Venezuela"
]

# Country name variations mapping
COUNTRY_ALIASES = {
    "myanmar": "Burma",
    "republic of congo": "Republic of the Congo",
    "democratic republic of congo": "Republic of the Congo",
    "drc": "Republic of the Congo",
    "usa": "United States",
    "us": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
}


class TravelAdvisoryAgent(BaseAgent):
    """
    Travel Advisory Agent - First checkpoint in vacation planning.

    Checks:
    1. US State Dept travel advisories (for US citizens traveling abroad)
    2. USA travel ban (for foreign nationals coming to USA)
    3. Global events/warnings at destination during travel dates

    Blocks travel planning if:
    - Destination has Level 4 "Do Not Travel" advisory
    - Traveler's origin country is on USA ban list (when traveling to USA)
    - Critical security alerts exist for destination
    """

    STATE_DEPT_API = "https://cadataapi.state.gov/api/TravelAdvisories"

    def __init__(self):
        super().__init__(
            name="travel_advisory",
            description="Checks travel warnings and restrictions before planning"
        )
        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Initialize Tavily client for global events search
        self.tavily_client = None
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if TAVILY_AVAILABLE and tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
            logger.info("[TRAVEL_ADVISORY] Tavily client initialized for global events search")
        else:
            logger.warning("[TRAVEL_ADVISORY] Tavily API key not found. Set TAVILY_API_KEY env var for global events search.")

        # Register A2A handlers
        self.register_message_handler("check_advisory", self._handle_advisory_request)

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check travel advisories and restrictions.

        Args:
            input_data: Contains:
                - origin_country: Traveler's country of citizenship/origin
                - destination_country: Where they want to travel
                - travel_dates: Optional dict with start/end dates

        Returns:
            Advisory result with can_proceed flag
        """
        origin = input_data.get("origin_country", "United States")
        destination = input_data.get("destination_country", "")
        destination_city = input_data.get("destination_city", "")
        travel_dates = input_data.get("travel_dates", {})

        # Normalize country names
        origin = self._normalize_country(origin)
        destination = self._normalize_country(destination)

        logger.info(f"[TRAVEL_ADVISORY] Checking: {origin} -> {destination}")

        advisories = []
        warnings = []
        blockers = []

        # Check 1: US citizens traveling abroad
        if self._is_usa(origin) and not self._is_usa(destination):
            state_dept_result = await self._check_state_dept_advisory(destination)
            if state_dept_result:
                advisories.append(state_dept_result)

                # Block if Level 4
                if state_dept_result.get("level") == 4:
                    blockers.append({
                        "type": "do_not_travel",
                        "message": f"US State Department Level 4 Advisory: Do Not Travel to {destination}",
                        "details": state_dept_result.get("advisory_text", "")
                    })
                elif state_dept_result.get("level") == 3:
                    warnings.append({
                        "type": "reconsider_travel",
                        "message": f"US State Department Level 3 Advisory: Reconsider Travel to {destination}",
                        "details": state_dept_result.get("advisory_text", "")
                    })

        # Check 2: Foreign nationals traveling TO USA
        if self._is_usa(destination) and not self._is_usa(origin):
            ban_result = self._check_usa_travel_ban(origin)
            if ban_result:
                if ban_result.get("ban_type") == "full":
                    blockers.append({
                        "type": "usa_travel_ban",
                        "message": f"USA Travel Ban: {origin} nationals are restricted from entering the United States",
                        "details": "Full visa ban applies to both immigrant and nonimmigrant visas",
                        "exemptions": ban_result.get("exemptions", [])
                    })
                elif ban_result.get("ban_type") == "partial":
                    warnings.append({
                        "type": "usa_partial_restriction",
                        "message": f"USA Travel Restriction: {origin} has partial visa restrictions",
                        "details": "Restrictions apply to immigrants and certain nonimmigrant visas (B-1/B-2, F, M, J)",
                        "exemptions": ban_result.get("exemptions", [])
                    })

        # Check 3: Domestic travel (same country) - no advisories needed
        if self._is_same_country(origin, destination):
            return {
                "status": "success",
                "can_proceed": True,
                "travel_type": "domestic",
                "message": "Domestic travel - no international travel advisories apply",
                "advisories": [],
                "warnings": [],
                "blockers": [],
                "global_events": []
            }

        # Check 4: Global events and safety alerts using Tavily
        global_events = []
        if self.tavily_client and destination:
            events_result = await self._search_global_events(
                destination=destination,
                destination_city=destination_city,
                travel_dates=travel_dates
            )
            if events_result:
                global_events = events_result.get("events", [])
                # Add critical events as warnings
                for event in events_result.get("critical_events", []):
                    warnings.append({
                        "type": "global_event",
                        "message": event.get("title", "Global event alert"),
                        "details": event.get("description", ""),
                        "source": event.get("source", "Tavily Search")
                    })

        # Determine if travel can proceed
        can_proceed = len(blockers) == 0

        # Send notification to orchestrator
        if blockers:
            self.send_message(
                to_agent="orchestrator",
                message_type="travel_blocked",
                content={
                    "origin": origin,
                    "destination": destination,
                    "blockers": blockers
                },
                priority="critical"
            )
        elif warnings:
            self.send_message(
                to_agent="orchestrator",
                message_type="travel_warning",
                content={
                    "origin": origin,
                    "destination": destination,
                    "warnings": warnings
                },
                priority="high"
            )

        return {
            "status": "success",
            "can_proceed": can_proceed,
            "travel_type": "international",
            "origin": origin,
            "destination": destination,
            "advisories": advisories,
            "warnings": warnings,
            "blockers": blockers,
            "global_events": global_events,
            "recommendation": self._get_recommendation(blockers, warnings),
            "checked_at": self._get_timestamp()
        }

    async def _search_global_events(
        self,
        destination: str,
        destination_city: str = "",
        travel_dates: Dict[str, str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for global events, protests, natural disasters, and safety alerts
        at the destination using Tavily Search API.
        """
        if not self.tavily_client:
            return None

        try:
            # Build search query
            location = destination_city if destination_city else destination
            date_info = ""
            if travel_dates:
                start = travel_dates.get("start", "")
                end = travel_dates.get("end", "")
                if start and end:
                    date_info = f" {start} to {end}"
                elif start:
                    date_info = f" {start}"

            # Search for safety and events
            queries = [
                f"{location} travel safety warnings alerts{date_info}",
                f"{location} protests demonstrations civil unrest{date_info}",
                f"{location} natural disasters weather emergencies{date_info}",
            ]

            all_events = []
            critical_events = []

            for query in queries:
                logger.info(f"[TAVILY] Searching: {query}")
                try:
                    response = self.tavily_client.search(
                        query=query,
                        search_depth="basic",
                        max_results=3,
                        include_answer=True
                    )

                    # Process results
                    if response.get("results"):
                        for result in response["results"]:
                            event = {
                                "title": result.get("title", ""),
                                "description": result.get("content", "")[:500],
                                "url": result.get("url", ""),
                                "source": result.get("source", "Tavily Search"),
                                "relevance_score": result.get("score", 0)
                            }
                            all_events.append(event)

                            # Check for critical keywords
                            content_lower = (result.get("content", "") + result.get("title", "")).lower()
                            critical_keywords = [
                                "emergency", "evacuation", "danger", "warning",
                                "protest", "violence", "unrest", "attack",
                                "earthquake", "hurricane", "tsunami", "flood",
                                "outbreak", "epidemic", "quarantine"
                            ]
                            if any(keyword in content_lower for keyword in critical_keywords):
                                critical_events.append(event)

                except Exception as e:
                    logger.warning(f"[TAVILY] Search error for query '{query}': {e}")
                    continue

            logger.info(f"[TAVILY] Found {len(all_events)} events, {len(critical_events)} critical")

            return {
                "events": all_events[:10],  # Limit to 10 events
                "critical_events": critical_events[:5],  # Limit critical to 5
                "search_performed": True
            }

        except Exception as e:
            logger.error(f"[TAVILY] Global events search failed: {e}")
            return None

    async def _check_state_dept_advisory(self, country: str) -> Optional[Dict[str, Any]]:
        """Fetch US State Department travel advisory for a country."""
        try:
            response = await self.http_client.get(self.STATE_DEPT_API)

            if response.status_code == 200:
                data = response.json()

                # Search for the country in advisories
                for advisory in data:
                    advisory_country = advisory.get("country_name", "").lower()
                    if country.lower() in advisory_country or advisory_country in country.lower():
                        level = advisory.get("level", 1)
                        return {
                            "country": advisory.get("country_name"),
                            "level": level,
                            "level_description": self._get_level_description(level),
                            "advisory_text": advisory.get("advisory_text", ""),
                            "date_updated": advisory.get("date_updated", ""),
                            "source": "US State Department"
                        }

                # Country not found - assume Level 1
                return {
                    "country": country,
                    "level": 1,
                    "level_description": "Exercise Normal Precautions",
                    "advisory_text": "No specific advisory found",
                    "source": "US State Department"
                }

        except Exception as e:
            logger.error(f"[TRAVEL_ADVISORY] State Dept API error: {e}")
            # Return a safe default on error
            return {
                "country": country,
                "level": 0,
                "level_description": "Unable to fetch advisory",
                "advisory_text": f"Error fetching advisory: {str(e)}",
                "source": "US State Department",
                "error": True
            }

        return None

    def _check_usa_travel_ban(self, origin_country: str) -> Optional[Dict[str, Any]]:
        """Check if origin country is on USA travel ban list."""
        origin_lower = origin_country.lower()

        # Check full ban
        for banned in USA_FULL_BAN_COUNTRIES:
            if banned.lower() in origin_lower or origin_lower in banned.lower():
                return {
                    "ban_type": "full",
                    "country": origin_country,
                    "restriction": "Full visa ban - immigrant and nonimmigrant visas",
                    "effective_date": "June 9, 2025",
                    "exemptions": [
                        "Lawful Permanent Residents (Green Card holders)",
                        "Dual nationals traveling on non-designated country passport",
                        "Asylum/refugee status holders",
                        "Diplomatic visa holders",
                        "Athletes for 2026 World Cup / 2028 Olympics"
                    ]
                }

        # Check partial ban
        for restricted in USA_PARTIAL_BAN_COUNTRIES:
            if restricted.lower() in origin_lower or origin_lower in restricted.lower():
                return {
                    "ban_type": "partial",
                    "country": origin_country,
                    "restriction": "Partial restrictions on immigrant and certain nonimmigrant visas",
                    "affected_visas": ["B-1/B-2 (Tourist)", "F (Student)", "M (Vocational)", "J (Exchange)"],
                    "effective_date": "June 9, 2025",
                    "exemptions": [
                        "Lawful Permanent Residents",
                        "Certain work visas may still be available",
                        "Diplomatic visas"
                    ]
                }

        return None

    def _get_level_description(self, level: int) -> str:
        """Get description for State Dept advisory level."""
        levels = {
            1: "Exercise Normal Precautions",
            2: "Exercise Increased Caution",
            3: "Reconsider Travel",
            4: "Do Not Travel"
        }
        return levels.get(level, "Unknown")

    def _get_recommendation(self, blockers: List, warnings: List) -> str:
        """Generate travel recommendation based on findings."""
        if blockers:
            return "BLOCKED: Travel to this destination is not recommended. Please choose an alternative destination."
        elif warnings:
            return "CAUTION: Travel is possible but carries elevated risks. Review warnings carefully before proceeding."
        else:
            return "CLEAR: No significant travel advisories. Safe to proceed with planning."

    def _normalize_country(self, country: str) -> str:
        """Normalize country name to standard form."""
        if not country:
            return "United States"  # Default assumption

        country_lower = country.lower().strip()

        # Check aliases
        for alias, standard in COUNTRY_ALIASES.items():
            if alias in country_lower:
                return standard

        # Capitalize properly
        return country.title()

    def _is_usa(self, country: str) -> bool:
        """Check if country is USA."""
        usa_variants = ["united states", "usa", "us", "america"]
        return country.lower().strip() in usa_variants or "united states" in country.lower()

    def _is_same_country(self, origin: str, destination: str) -> bool:
        """Check if origin and destination are the same country."""
        return origin.lower().strip() == destination.lower().strip()

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    async def _handle_advisory_request(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A advisory check request."""
        logger.info(f"[A2A] Received advisory request from {message.get('from_agent')}")
        return await self.execute(message.get("content", {}))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
