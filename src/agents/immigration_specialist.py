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
            description="Handles visa requirements and travel documentation"
        )

        # Register A2A message handlers
        self.register_message_handler("weather_advisory", self._handle_weather_advisory)

        # Visa requirements database
        self.visa_database = {
            "France": {
                "US": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "UK": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "IN": {"required": True, "max_stay": "90 days", "type": "Schengen Visa"},
                "CN": {"required": True, "max_stay": "90 days", "type": "Schengen Visa"}
            },
            "Japan": {
                "US": {"required": False, "max_stay": "90 days", "type": "Visa-free"},
                "UK": {"required": False, "max_stay": "90 days", "type": "Visa-free"},
                "IN": {"required": True, "max_stay": "15-90 days", "type": "Tourist Visa"},
                "CN": {"required": True, "max_stay": "15-30 days", "type": "Tourist Visa"}
            },
            "UK": {
                "US": {"required": False, "max_stay": "6 months", "type": "ETA"},
                "EU": {"required": False, "max_stay": "6 months", "type": "Visa-free"},
                "IN": {"required": True, "max_stay": "6 months", "type": "Standard Visitor Visa"},
                "CN": {"required": True, "max_stay": "6 months", "type": "Standard Visitor Visa"}
            },
            "Italy": {
                "US": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "UK": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "IN": {"required": True, "max_stay": "90 days", "type": "Schengen Visa"}
            },
            "Thailand": {
                "US": {"required": False, "max_stay": "30 days", "type": "Visa Exemption"},
                "UK": {"required": False, "max_stay": "30 days", "type": "Visa Exemption"},
                "IN": {"required": True, "max_stay": "15-60 days", "type": "Tourist Visa/VOA"}
            },
            "Australia": {
                "US": {"required": True, "max_stay": "90 days", "type": "ETA (subclass 601)"},
                "UK": {"required": True, "max_stay": "90 days", "type": "ETA (subclass 601)"},
                "IN": {"required": True, "max_stay": "90 days", "type": "Visitor Visa"}
            },
            "Germany": {
                "US": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "UK": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "IN": {"required": True, "max_stay": "90 days", "type": "Schengen Visa"}
            },
            "Spain": {
                "US": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "UK": {"required": False, "max_stay": "90 days", "type": "Schengen"},
                "IN": {"required": True, "max_stay": "90 days", "type": "Schengen Visa"}
            }
        }

        # Weather advisories received
        self.weather_advisories = []

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check visa requirements and travel documentation.

        Args:
            input_data: Contains 'citizenship', 'destination', 'duration'

        Returns:
            Visa requirements and documentation checklist
        """
        citizenship = input_data.get("citizenship", "US")
        destination = input_data.get("destination", "")
        duration = input_data.get("duration_days", 7)

        if not destination:
            return {
                "status": "error",
                "error": "Destination is required"
            }

        # Get visa requirements
        visa_info = self._get_visa_requirements(citizenship, destination)

        # Check if duration exceeds allowed stay
        duration_warning = self._check_duration(visa_info, duration)

        # Get required documents
        documents = self._get_required_documents(visa_info, citizenship)

        # Get application steps if visa required
        application_steps = []
        if visa_info.get("required"):
            application_steps = self._get_application_steps(destination, visa_info.get("type"))

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
            "visa_requirements": visa_info,
            "duration_warning": duration_warning,
            "required_documents": documents,
            "application_steps": application_steps,
            "travel_warnings": travel_warnings,
            "entry_requirements": self._get_entry_requirements(destination)
        }

    def _get_visa_requirements(self, citizenship: str, destination: str) -> Dict[str, Any]:
        """Get visa requirements for citizenship and destination."""
        # Normalize country names
        country_codes = {
            "United States": "US", "USA": "US", "US": "US",
            "United Kingdom": "UK", "Britain": "UK", "UK": "UK",
            "India": "IN", "IN": "IN",
            "China": "CN", "CN": "CN"
        }

        citizenship_code = country_codes.get(citizenship, citizenship)

        # Extract destination country
        dest_country = destination.split(",")[-1].strip() if "," in destination else destination

        # Look up in database
        country_data = self.visa_database.get(dest_country, {})
        visa_info = country_data.get(citizenship_code, None)

        if visa_info:
            return {
                "destination": dest_country,
                "required": visa_info["required"],
                "max_stay": visa_info["max_stay"],
                "visa_type": visa_info["type"],
                "source": "database"
            }
        else:
            return {
                "destination": dest_country,
                "required": "Check embassy",
                "max_stay": "Varies",
                "visa_type": "Unknown",
                "note": "Please verify with official embassy sources",
                "source": "default"
            }

    def _check_duration(self, visa_info: Dict[str, Any], duration: int) -> Dict[str, Any]:
        """Check if trip duration exceeds visa limits."""
        max_stay = visa_info.get("max_stay", "90 days")

        # Extract number from max_stay
        try:
            max_days = int(''.join(filter(str.isdigit, max_stay.split()[0])))
        except (ValueError, IndexError):
            max_days = 90

        if duration > max_days:
            return {
                "warning": True,
                "message": f"Trip duration ({duration} days) exceeds maximum stay ({max_days} days)",
                "recommendation": "Consider applying for extended visa or splitting trip"
            }

        return {
            "warning": False,
            "message": f"Duration ({duration} days) is within allowed stay ({max_days} days)"
        }

    def _get_required_documents(self, visa_info: Dict[str, Any], citizenship: str) -> List[str]:
        """Get list of required documents."""
        base_documents = [
            "Valid passport (6+ months validity)",
            "Return/onward ticket",
            "Proof of accommodation",
            "Proof of sufficient funds",
            "Travel insurance (recommended)"
        ]

        if visa_info.get("required"):
            base_documents.extend([
                "Completed visa application form",
                "Passport-sized photos",
                "Bank statements (3-6 months)",
                "Employment letter or business documents",
                "Invitation letter (if applicable)"
            ])

        return base_documents

    def _get_application_steps(self, destination: str, visa_type: str) -> List[Dict[str, Any]]:
        """Get visa application steps."""
        return [
            {
                "step": 1,
                "action": "Gather required documents",
                "timeline": "2-4 weeks before application"
            },
            {
                "step": 2,
                "action": "Complete online application form",
                "timeline": "1-2 hours"
            },
            {
                "step": 3,
                "action": "Schedule appointment at embassy/VFS",
                "timeline": "Book 2-3 weeks in advance"
            },
            {
                "step": 4,
                "action": "Attend biometrics appointment",
                "timeline": "30 minutes"
            },
            {
                "step": 5,
                "action": "Wait for processing",
                "timeline": f"5-15 business days for {visa_type}"
            },
            {
                "step": 6,
                "action": "Collect passport with visa",
                "timeline": "Pickup or courier delivery"
            }
        ]

    def _get_entry_requirements(self, destination: str) -> List[str]:
        """Get general entry requirements."""
        requirements = [
            "Valid travel documents",
            "Completed customs declaration",
            "Proof of onward travel"
        ]

        # Add destination-specific requirements
        special_requirements = {
            "Japan": ["Visit Japan Web registration", "Quarantine info (if applicable)"],
            "Australia": ["Incoming Passenger Card", "Declare food items"],
            "Thailand": ["TM6 arrival card", "Hotel booking confirmation"],
            "UK": ["Electronic Travel Authorization (ETA)", "Proof of return ticket"]
        }

        dest_country = destination.split(",")[-1].strip() if "," in destination else destination
        if dest_country in special_requirements:
            requirements.extend(special_requirements[dest_country])

        return requirements

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
