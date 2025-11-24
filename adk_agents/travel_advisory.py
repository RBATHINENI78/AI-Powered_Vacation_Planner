"""
Pure ADK Travel Advisory Agent with CODE-ENFORCED blocking
Uses Google ADK Agent with custom _run_async_impl for blocking logic
"""

from google.adk.agents import Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import FunctionTool
from google.adk.events import Event
import sys
import os
from typing import AsyncGenerator, Dict, Any, Optional, ClassVar
from loguru import logger

# Add parent directory to path to import tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.travel_tools import check_state_dept_advisory, check_usa_travel_ban
from config import Config

# Optional Tavily integration
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("[TRAVEL_ADVISORY] TavilyClient not available - skipping global events check")


class TravelAdvisoryAgent(Agent):
    """
    ADK Travel Advisory Agent with CODE-ENFORCED blocking.

    Implements 4-check pattern from original code:
    1. US citizens traveling abroad → Check State Dept advisory
    2. Foreign nationals to USA → Check USA travel ban
    3. Domestic travel → Skip advisories
    4. Global events → Check Tavily for safety alerts

    Unlike LLM-prompt-based blocking, this uses Python code to enforce blocking.
    """

    # Emergency fallback: Known Level 4 countries (ONLY used if State Dept API fails)
    # Primary source is ALWAYS the live State Department API
    LEVEL_4_COUNTRIES: ClassVar[list[str]] = [
        "afghanistan", "yemen", "syria", "libya", "somalia",
        "north korea", "south sudan", "mali", "burkina faso",
        "central african republic", "iraq", "iran"
    ]

    tavily_client: Optional[Any] = None  # Pydantic field for Tavily client

    def __init__(self):
        super().__init__(
            name="travel_advisory",
            description="""You are a travel advisory specialist analyzing travel safety.

            Your role: Provide travel safety analysis based on the structured data returned.
            You will receive a structured response with can_proceed, blockers, and warnings.

            Present this information clearly to the user.""",
            model=Config.get_model_for_agent("travel_advisory"),
            tools=[
                FunctionTool(check_state_dept_advisory),
                FunctionTool(check_usa_travel_ban)
            ]
        )

        # Initialize Tavily client if available
        if TAVILY_AVAILABLE and os.getenv("TAVILY_API_KEY"):
            self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            logger.info("[TRAVEL_ADVISORY] TavilyClient initialized")

    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        CODE-ENFORCED blocking logic (matches old code pattern).

        Extracts origin/destination from context, performs 4 checks,
        and returns structured response with can_proceed boolean.
        """
        # Extract travel info from context
        input_text = str(context.user_content)
        logger.info(f"[TRAVEL_ADVISORY] Processing: {input_text}")

        # Parse origin and destination from input
        origin, destination = self._extract_locations(input_text)
        logger.info(f"[TRAVEL_ADVISORY] Origin: {origin}, Destination: {destination}")

        # Initialize results
        blockers = []
        warnings = []
        travel_type = "international"  # Default
        domestic_country = None

        # ==================== CHECK 1: US citizens traveling abroad ====================
        if self._is_usa(origin) and not self._is_usa(destination):
            logger.info(f"[TRAVEL_ADVISORY] Check 1: US → {destination}")
            state_dept_result = await check_state_dept_advisory(destination)

            advisory_level = state_dept_result.get("level", 1)
            is_api_error = state_dept_result.get("error", False)
            not_found_in_api = state_dept_result.get("not_found", False)

            # Fallback: Use hardcoded list if API failed OR country not found in API database
            if (is_api_error or not_found_in_api) and self._is_level_4_country(destination):
                logger.warning(f"[TRAVEL_ADVISORY] API returned no data for {destination} - Using hardcoded Level 4 fallback")
                advisory_level = 4
                state_dept_result["level"] = 4
                state_dept_result["level_description"] = "Do Not Travel"
                state_dept_result["advisory_text"] = "State Department Level 4 advisory: Do not travel due to terrorism, civil unrest, kidnapping, and armed conflict."
                state_dept_result["date_updated"] = "Current"

            # CODE-ENFORCED BLOCKING - Trust API data
            if advisory_level == 4:
                blockers.append({
                    "type": "level_4_advisory",
                    "message": f"⛔ TRAVEL BLOCKED: Level 4 'Do Not Travel' advisory for {destination}",
                    "details": state_dept_result,
                    "alternative_destinations": self._suggest_alternatives(destination)
                })
            elif advisory_level == 3:
                warnings.append({
                    "type": "level_3_advisory",
                    "message": f"⚠️ WARNING: Level 3 'Reconsider Travel' advisory for {destination}",
                    "details": state_dept_result
                })
            elif advisory_level == 2:
                warnings.append({
                    "type": "level_2_advisory",
                    "message": f"ℹ️ NOTICE: Level 2 'Exercise Increased Caution' for {destination}",
                    "details": state_dept_result
                })

        # ==================== CHECK 2: Foreign nationals to USA ====================
        elif not self._is_usa(origin) and self._is_usa(destination):
            logger.info(f"[TRAVEL_ADVISORY] Check 2: {origin} → USA")
            ban_result = check_usa_travel_ban(origin)

            if ban_result:
                if ban_result.get("ban_type") == "full":
                    blockers.append({
                        "type": "usa_travel_ban",
                        "message": f"⛔ TRAVEL BLOCKED: Full USA travel ban for citizens of {origin}",
                        "details": ban_result
                    })
                elif ban_result.get("ban_type") == "partial":
                    warnings.append({
                        "type": "usa_partial_ban",
                        "message": f"⚠️ WARNING: Partial USA travel restrictions for {origin}",
                        "details": ban_result
                    })

        # ==================== CHECK 3: Domestic travel ====================
        elif self._is_same_country(origin, destination):
            logger.info(f"[TRAVEL_ADVISORY] Check 3: Domestic travel within {origin}")
            # No international advisories needed for domestic travel
            # Set travel type for downstream agents
            travel_type = "domestic"
            domestic_country = origin

        # ==================== CHECK 4: Global events using Tavily ====================
        if self.tavily_client and destination:
            logger.info(f"[TRAVEL_ADVISORY] Check 4: Tavily global events for {destination}")
            try:
                events_result = await self._search_global_events(destination)
                for event in events_result.get("critical_events", []):
                    warnings.append({
                        "type": "global_event",
                        "message": f"⚠️ ALERT: {event.get('title', 'Safety concern')}",
                        "details": event
                    })
            except Exception as e:
                logger.error(f"[TRAVEL_ADVISORY] Tavily search failed: {e}")

        # ==================== CODE-ENFORCED DECISION ====================
        can_proceed = len(blockers) == 0

        result = {
            "can_proceed": can_proceed,
            "travel_status": "BLOCKED" if not can_proceed else ("CAUTION" if warnings else "CLEAR"),
            "origin": origin,
            "destination": destination,
            "blockers": blockers,
            "warnings": warnings,
            "travel_type": travel_type,
            "domestic_country": domestic_country
        }

        logger.info(f"[TRAVEL_ADVISORY] Result: can_proceed={can_proceed}, blockers={len(blockers)}, warnings={len(warnings)}")

        # Format output message
        if not can_proceed:
            message = self._format_blocked_message(destination, blockers, input_text)
        else:
            message = f"✅ **TRAVEL ADVISORY CLEAR**\n\n"

            # Add domestic travel notice if applicable
            if result.get("travel_type") == "domestic":
                message += f"**Domestic Travel:** {origin} → {destination}\n"
                message += "No international travel advisories or visa requirements apply.\n"
                message += "Currency exchange not needed (same country).\n\n"

            if warnings:
                message += "**Important Notices:**\n"
                for warning in warnings:
                    message += f"- {warning['message']}\n"
            else:
                if result.get("travel_type") != "domestic":
                    message += f"No travel advisories for {destination}. Proceed with normal precautions.\n"

        # Yield result as Event (ADK pattern)
        from google.genai.types import Content, Part

        yield Event(
            author="travel_advisory",  # Required field
            content=Content(parts=[Part(text=message)]),
            custom_metadata=result  # Store structured data for next agents
        )

        # CRITICAL: If blocked, raise exception to stop workflow
        if not can_proceed:
            logger.error(f"[TRAVEL_ADVISORY] Travel blocked - raising exception to stop workflow")
            # Raise standard Python exception to stop the workflow
            raise RuntimeError(
                f"TRAVEL_BLOCKED: {message}"
            )

    # ==================== Helper Methods ====================

    def _extract_locations(self, input_text: str) -> tuple[str, str]:
        """Extract origin and destination from user input."""
        import re

        # Convert to lowercase for matching
        text_lower = input_text.lower()

        # Pattern 1: "to CITY, COUNTRY from ORIGIN"
        match = re.search(r'to\s+([^\.]+?)\s+from\s+([^\.]+?)(?:\.|$)', text_lower, re.IGNORECASE)
        if match:
            destination = match.group(1).strip()
            origin = match.group(2).strip()
            # Clean up extra text (like dates, budget)
            destination = re.split(r'\s+travel dates|origin:|citizenship:|budget:', destination)[0].strip()
            origin = re.split(r'\s+citizenship:|budget:', origin)[0].strip()
            return origin, destination

        # Pattern 2: "vacation to DESTINATION" (assume USA origin)
        match = re.search(r'(?:vacation|trip)\s+to\s+([^\.]+?)(?:\s+for|\.|$)', text_lower, re.IGNORECASE)
        if match:
            destination = match.group(1).strip()
            # Clean up
            destination = re.split(r'\s+travel dates|origin:|citizenship:|budget:|for\s+\d+', destination)[0].strip()
            return "USA", destination

        # Fallback
        return "USA", "Unknown"

    def _is_usa(self, location: str) -> bool:
        """Check if location is in USA."""
        location_lower = location.lower()
        return any(term in location_lower for term in ["usa", "united states", "us", "america"])

    def _is_same_country(self, origin: str, destination: str) -> bool:
        """Check if origin and destination are in same country."""
        if self._is_usa(origin) and self._is_usa(destination):
            return True
        # Simple heuristic: extract country from "City, Country" format
        origin_country = origin.split(",")[-1].strip().lower()
        dest_country = destination.split(",")[-1].strip().lower()
        return origin_country == dest_country

    def _is_level_4_country(self, country: str) -> bool:
        """Check if country is in hardcoded Level 4 list."""
        country_lower = country.lower()
        return any(l4_country in country_lower for l4_country in self.LEVEL_4_COUNTRIES)

    def _suggest_alternatives(self, blocked_destination: str) -> list[str]:
        """Suggest safer alternative destinations based on region."""
        # Regional alternatives
        alternatives_map = {
            "afghanistan": ["Dubai, UAE", "Oman", "Jordan", "Turkey"],
            "yemen": ["Dubai, UAE", "Oman", "Jordan", "Qatar"],
            "syria": ["Jordan", "Lebanon", "Turkey", "Cyprus"],
            "libya": ["Tunisia", "Morocco", "Egypt", "Malta"],
            "somalia": ["Kenya", "Tanzania", "Seychelles", "Mauritius"],
            "north korea": ["South Korea", "Japan", "Taiwan", "Vietnam"],
            "south sudan": ["Kenya", "Tanzania", "Uganda", "Rwanda"]
        }

        dest_lower = blocked_destination.lower()
        for key, alts in alternatives_map.items():
            if key in dest_lower:
                return alts

        # Generic fallback
        return ["Dubai, UAE", "Singapore", "Barcelona, Spain", "Tokyo, Japan"]

    def _format_blocked_message(self, destination: str, blockers: list, input_text: str) -> str:
        """Format a professional, detailed blocking message."""
        import re
        from datetime import datetime

        # Extract travel dates from input if available
        date_match = re.search(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d+)-(\d+),\s+(\d+)', input_text, re.IGNORECASE)
        travel_dates = ""
        if date_match:
            travel_dates = date_match.group(0)  # Full match like "December 15-22, 2025"

        message = ""

        for blocker in blockers:
            blocker_type = blocker.get("type")
            details = blocker.get("details", {})

            if blocker_type == "level_4_advisory":
                # Level 4: Do Not Travel
                level_desc = details.get("level_description", "Do Not Travel")
                advisory_text = details.get("advisory_text", "")
                date_updated = details.get("date_updated", "")

                message += f"I regret to inform you that I cannot plan a vacation to {destination}"
                if travel_dates:
                    message += f" for your requested dates"
                message += ".\n\n"

                # State Department advisory
                message += f"**U.S. State Department Travel Advisory:**\n"
                message += f"- **Level 4: {level_desc}**\n"
                if date_updated:
                    message += f"- **Last Updated:** {date_updated}\n"
                message += f"- **Effective:** Immediate (current advisory in effect)\n\n"

                # Specific risks
                message += f"**Significant Travel Warnings:**\n"
                message += f"- ⚠️ **Critical Safety Risk:** Increased life-risks for U.S. citizens\n"
                message += f"- ⚠️ **Detention Risk:** High risk of wrongful detention (D indicator)\n"
                message += f"- ⚠️ **Limited Consular Services:** U.S. Embassy operations limited or suspended\n"
                message += f"- ⚠️ **Terrorism Threat:** Ongoing threat of terrorist attacks\n"
                message += f"- ⚠️ **Civil Unrest:** Volatile security situation\n\n"

                if advisory_text:
                    message += f"**Official Advisory:**\n{advisory_text[:300]}...\n\n"

                message += f"**Due to these severe travel restrictions and safety concerns, I strongly advise against travel to {destination}.**\n\n"

            elif blocker_type == "usa_travel_ban":
                # USA Travel Ban
                ban_type = details.get("ban_type", "Full")
                restriction = details.get("restriction", "")
                effective_date = details.get("effective_date", "")
                exemptions = details.get("exemptions", [])

                message += f"I regret to inform you that travel from {destination} to the United States is currently restricted.\n\n"

                message += f"**U.S. Travel Ban:**\n"
                message += f"- **Ban Type:** {ban_type.title()} Travel Ban\n"
                message += f"- **Effective Date:** {effective_date}\n"
                message += f"- **Restriction:** {restriction}\n\n"

                if exemptions:
                    message += f"**Exemptions (may apply):**\n"
                    for exemption in exemptions:
                        message += f"- {exemption}\n"
                    message += "\n"

                message += f"**Please consult with immigration authorities for specific guidance on your situation.**\n\n"

            # Alternative destinations
            if "alternative_destinations" in blocker:
                message += f"**Recommended Alternative Destinations:**\n"
                for alt in blocker["alternative_destinations"]:
                    message += f"- {alt}\n"
                message += "\n"

        message += "---\n\n"
        message += "**⛔ Vacation planning cannot proceed due to travel restrictions. ⛔**\n"

        return message

    async def _search_global_events(self, destination: str) -> Dict[str, Any]:
        """Search for global safety events using Tavily."""
        if not self.tavily_client:
            return {"critical_events": []}

        try:
            query = f"travel safety alert {destination} {2025}"
            # Tavily search is synchronous, not async
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )

            # Filter for critical events
            critical_events = []
            critical_keywords = ["alert", "warning", "attack", "unrest", "conflict", "terror", "danger"]

            for result in response.get("results", []):
                content = (result.get("content", "") + " " + result.get("title", "")).lower()
                if any(keyword in content for keyword in critical_keywords):
                    critical_events.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", "")
                    })

            return {"critical_events": critical_events}
        except Exception as e:
            logger.error(f"[TRAVEL_ADVISORY] Tavily search error: {e}")
            return {"critical_events": []}
