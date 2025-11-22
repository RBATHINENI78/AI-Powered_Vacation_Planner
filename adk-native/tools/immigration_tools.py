"""
Immigration Tools - Visa requirements and travel documentation
Uses LLM knowledge + structured prompting instead of external APIs
"""

from typing import Dict, Any


def get_visa_requirements(citizenship: str, destination_country: str, duration_days: int = 7) -> Dict[str, Any]:
    """
    Get visa requirements for a citizenship traveling to a destination.

    Returns structured instruction for LLM to provide comprehensive visa information.

    Args:
        citizenship: Traveler's citizenship/nationality
        destination_country: Destination country
        duration_days: Length of stay in days

    Returns:
        Structured data with LLM instruction for visa requirements
    """
    return {
        "citizenship": citizenship,
        "destination_country": destination_country,
        "duration_days": duration_days,
        "llm_instruction": f"""Based on your knowledge, provide COMPREHENSIVE visa and immigration requirements for a {citizenship} citizen traveling to {destination_country} for {duration_days} days.

Include:

**1. Visa Requirement**
- Is visa required? (Yes/No/Visa-free for X days)
- Visa type (Tourist, eVisa, Visa-on-Arrival, etc.)
- Maximum allowed stay
- Processing time
- Application fee (USD)

**2. Application Process** (if visa required)
- How to apply (online portal, embassy, VFS Global, etc.)
- Where to apply (website URL or embassy location)
- Processing time (standard and expedited)
- Required documents

**3. Passport Requirements**
- Minimum validity (e.g., 6 months beyond stay)
- Blank pages needed
- Biometric requirements

**4. Entry Requirements**
- Return/onward ticket requirement
- Proof of accommodation
- Proof of sufficient funds
- Travel insurance requirements

**5. Health Requirements**
- Required vaccinations (Yellow Fever, COVID-19, etc.)
- Recommended vaccinations
- Health insurance requirements

**6. Important Notes**
- Any current travel restrictions
- Border crossing requirements
- Extension possibilities
- Consequences of overstay

Format as clear, actionable information."""
    }


def get_passport_validity_rules(destination_country: str) -> Dict[str, Any]:
    """
    Get passport validity requirements for a destination country.

    Args:
        destination_country: Destination country name

    Returns:
        Passport validity rules
    """
    return {
        "destination_country": destination_country,
        "llm_instruction": f"""Provide passport validity requirements for entering {destination_country}:

**Passport Validity Rules:**
- Minimum validity period from arrival date
- Blank pages required
- Damaged passport policies
- Emergency/temporary passport acceptance

**Common Requirements:**
- Entry stamp procedures
- Exit requirements
- Lost passport procedures while in country

Provide specific requirements for {destination_country}."""
    }


def check_entry_restrictions(citizenship: str, destination_country: str) -> Dict[str, Any]:
    """
    Check for entry restrictions and special requirements.

    Args:
        citizenship: Traveler's citizenship
        destination_country: Destination country

    Returns:
        Entry restrictions information
    """
    return {
        "citizenship": citizenship,
        "destination_country": destination_country,
        "llm_instruction": f"""Check for entry restrictions for {citizenship} citizens entering {destination_country}:

**Entry Restrictions to Check:**
1. Visa ban or restricted entry
2. Required permits or special documentation
3. Restricted areas or regions
4. Religious/cultural entry requirements
5. Dual citizenship considerations
6. Previous visa refusal implications
7. Criminal record restrictions
8. Age restrictions for unaccompanied minors

**Current Situation:**
- COVID-19 related restrictions
- Political tensions affecting entry
- Seasonal restrictions
- Special event restrictions

Provide current accurate information."""
    }
