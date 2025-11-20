"""
Immigration Specialist Agent - Visa Requirements and Travel Documentation
"""

from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent


class ImmigrationSpecialistAgent(BaseAgent):
    """
    Immigration Specialist Agent for visa and travel documentation.
    Receives A2A advisories from Destination Intelligence Agent.
    """

    def __init__(self):
        super().__init__(
            name="immigration_specialist",
            description="Handles visa requirements and travel documentation using LLM knowledge"
        )

        # Register A2A message handlers
        self.register_message_handler("weather_advisory", self._handle_weather_advisory)

        # Weather advisories received
        self.weather_advisories = []

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check visa requirements and travel documentation using LLM knowledge.

        Args:
            input_data: Contains 'citizenship', 'destination', 'duration'

        Returns:
            Structured data for LLM to generate comprehensive visa information
        """
        citizenship = input_data.get("citizenship", "")
        destination = input_data.get("destination", "")
        duration = input_data.get("duration_days", 7)

        if not destination:
            return {
                "status": "error",
                "error": "Destination is required"
            }

        # Check if citizenship is provided
        if not citizenship or citizenship.strip() == "":
            return {
                "status": "error",
                "error": "citizenship_required",
                "message": "To provide accurate visa and immigration requirements, I need to know your citizenship/nationality.",
                "prompt_user": True
            }

        # Extract destination country from city, state, country format
        dest_parts = destination.split(",")
        if len(dest_parts) > 1:
            dest_country = dest_parts[-1].strip()
        else:
            dest_country = destination.strip()

        # Get LLM-powered visa requirements
        visa_info = self._get_visa_requirements_llm(citizenship, destination, dest_country, duration)

        # Check for any weather-related restrictions
        travel_warnings = self._check_travel_warnings(destination)

        # Send acknowledgment to destination agent if we received weather advisory
        if self.weather_advisories:
            self.send_message(
                to_agent="destination_intelligence",
                message_type="advisory_acknowledgment",
                content={
                    "received": len(self.weather_advisories),
                    "restrictions_checked": True
                }
            )

        return {
            "status": "success",
            "citizenship": citizenship,
            "destination": destination,
            "destination_country": dest_country,
            "visa_requirements": visa_info,
            "travel_warnings": travel_warnings
        }

    def _get_visa_requirements_llm(self, citizenship: str, destination: str, dest_country: str, duration_days: int) -> Dict[str, Any]:
        """
        Get LLM-powered visa requirements.

        Returns structured data for LLM to generate comprehensive immigration details.
        """
        return {
            "citizenship": citizenship,
            "destination": destination,
            "destination_country": dest_country,
            "duration_days": duration_days,
            "instruction_for_llm": f"""Based on your knowledge, provide COMPREHENSIVE visa and immigration requirements for a {citizenship} citizen traveling to {destination} for {duration_days} days. Include:

**1. Visa Requirement**
- Is visa required? (Yes/No)
- What type of visa? (Tourist, eVisa, Visa-on-Arrival, Visa Exemption, etc.)
- Maximum allowed stay
- Processing time
- Application fee

**2. Application Process** (if visa required)
- How to apply (online, embassy, VFS, etc.)
- Where to apply
- Processing time
- Documents needed

**3. Required Documents**
Complete list including:
- Passport requirements (validity, blank pages)
- Photos specifications
- Financial documents
- Travel bookings
- Other supporting documents

**4. Entry Requirements**
- Passport validity requirement
- Blank pages needed
- Return/onward ticket requirement
- Proof of accommodation
- Proof of funds

**5. Travel Advisories & Restrictions**
- Any current travel bans or restrictions affecting {citizenship} citizens
- COVID-19 requirements (if any)
- Health emergencies
- Political situations
- Safety concerns

**6. Health Requirements**
- Required vaccinations
- Recommended vaccinations
- Yellow fever certificate (if applicable)
- COVID-19 testing/vaccination requirements

**7. Customs Regulations**
- Prohibited items
- Restricted items
- Duty-free allowances
- Currency restrictions
- Declaration requirements

**8. Duration of Stay**
- Maximum allowed stay for {citizenship} citizens
- Extension options (if available)
- Overstay penalties

**9. Special Notes for {citizenship} Citizens**
- Any bilateral agreements
- Special requirements
- Reciprocal arrangements
- Visa waivers

**10. Application Steps** (if visa required)
Step-by-step process with timelines

**IMPORTANT:**
- Provide CURRENT, ACCURATE information based on your training knowledge
- If there are travel bans or restrictions affecting {citizenship} citizens traveling to {dest_country}, CLEARLY state them
- Be specific about requirements for {citizenship} nationals
- Include official sources where possible (embassy websites, gov.travel sites)

Format as a comprehensive, structured guide."""
        }

    def _check_travel_warnings(self, destination: str) -> List[str]:
        """Check for travel warnings including weather advisories."""
        warnings = []

        # Check weather advisories received via A2A
        for advisory in self.weather_advisories:
            if destination in advisory.get("destination", ""):
                warnings.append(f"Weather Alert: {advisory.get('advisory_type')}")
                if advisory.get("recommendation"):
                    warnings.append(advisory["recommendation"])

        return warnings

    def _handle_weather_advisory(self, message) -> Dict[str, Any]:
        """Handle weather advisory from Destination Intelligence Agent."""
        logger.info(f"[A2A] Received weather advisory from {message.from_agent}")

        self.weather_advisories.append(message.content)

        # Check for emergency restrictions
        if message.content.get("advisory_type") == "severe_weather":
            logger.warning(f"[A2A] Severe weather advisory for {message.content.get('destination')}")

        return {
            "status": "received",
            "advisory_id": message.id,
            "action": "will_check_restrictions"
        }
