"""
Travel Advisory Tools - FunctionTool wrappers for ADK agents
"""

import httpx
from typing import Dict, Any, Optional
from loguru import logger


# USA Travel Ban Countries (Effective June 9, 2025)
USA_FULL_BAN_COUNTRIES = [
    "Afghanistan", "Burma", "Myanmar", "Chad", "Republic of the Congo",
    "Congo", "Equatorial Guinea", "Eritrea", "Haiti", "Iran",
    "Libya", "Somalia", "Sudan", "Yemen"
]

USA_PARTIAL_BAN_COUNTRIES = [
    "Burundi", "Cuba", "Laos", "Sierra Leone", "Togo",
    "Turkmenistan", "Venezuela"
]


async def check_state_dept_advisory(country: str) -> Dict[str, Any]:
    """
    Check US State Department travel advisory for a country.

    Args:
        country: Country name to check

    Returns:
        Advisory level and details
    """
    STATE_DEPT_API = "https://cadataapi.state.gov/api/TravelAdvisories"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(STATE_DEPT_API)

            if response.status_code == 200:
                data = response.json()

                # Search for the country in advisories
                # API structure: {"Title": "Afghanistan - Level 4: Do Not Travel", ...}
                import re

                for advisory in data:
                    title = advisory.get("Title", "")

                    # Extract country name from "CountryName - Level X: ..." format
                    title_match = re.match(r'^([^-]+)', title)
                    if not title_match:
                        continue

                    advisory_country = title_match.group(1).strip().lower()

                    # Normalize search country (extract country from "City, Country" format)
                    country_search = country.lower().strip()
                    # If format is "City, Country", extract just the country part
                    if ',' in country_search:
                        country_search = country_search.split(',')[-1].strip()

                    # Match country names (both ways for partial matches)
                    if country_search in advisory_country or advisory_country in country_search:
                        # Extract level from title (e.g., "Level 4")
                        level_match = re.search(r'Level (\d)', title)
                        level = int(level_match.group(1)) if level_match else 1

                        # Extract summary text
                        summary = advisory.get("Summary", "")
                        # Remove HTML tags for cleaner text
                        advisory_text = re.sub(r'<[^>]+>', ' ', summary)
                        advisory_text = re.sub(r'\s+', ' ', advisory_text).strip()

                        logger.info(f"[STATE_DEPT] Found {advisory_country.title()}: Level {level}")

                        return {
                            "country": advisory_country.title(),
                            "level": level,
                            "level_description": _get_level_description(level),
                            "advisory_text": advisory_text[:500] + "..." if len(advisory_text) > 500 else advisory_text,
                            "date_updated": advisory.get("Updated", advisory.get("Published", "")),
                            "source": "US State Department",
                            "full_title": title
                        }

                # Country not found in API - mark as "not_found" so agent can use fallback
                logger.warning(f"[STATE_DEPT] Country '{country}' not found in API database")
                return {
                    "country": country,
                    "level": 1,
                    "level_description": "Exercise Normal Precautions",
                    "advisory_text": "No specific advisory found in API",
                    "source": "US State Department",
                    "not_found": True  # Signal that country wasn't in API database
                }

    except Exception as e:
        logger.error(f"[STATE_DEPT] API error: {e}")
        return {
            "country": country,
            "level": 0,
            "level_description": "Unable to fetch advisory",
            "advisory_text": f"Error fetching advisory: {str(e)}",
            "source": "US State Department",
            "error": True
        }


def check_usa_travel_ban(origin_country: str) -> Optional[Dict[str, Any]]:
    """
    Check if origin country is on USA travel ban list.

    Args:
        origin_country: Country of origin/citizenship

    Returns:
        Ban details if restricted, None otherwise
    """
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


def _get_level_description(level: int) -> str:
    """Get description for State Dept advisory level."""
    levels = {
        1: "Exercise Normal Precautions",
        2: "Exercise Increased Caution",
        3: "Reconsider Travel",
        4: "Do Not Travel"
    }
    return levels.get(level, "Unknown")
