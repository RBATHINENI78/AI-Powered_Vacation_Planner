"""
Visa Tool - Check visa requirements for travel
"""

from typing import Dict, Any


def check_visa_requirements(citizenship: str, destination: str) -> Dict[str, Any]:
    """
    Check visa requirements for travel based on citizenship and destination.

    Args:
        citizenship: Country of citizenship (e.g., United States)
        destination: Destination country or city

    Returns:
        Visa requirement information
    """
    # Comprehensive visa database for US citizens
    # In production, this would connect to a visa API
    visa_database = {
        "France": {
            "visa_required": False,
            "max_stay": "90 days within 180-day period",
            "requirements": [
                "Valid passport (3 months beyond stay)",
                "Return or onward ticket",
                "Proof of accommodation",
                "Proof of sufficient funds"
            ],
            "notes": "Part of Schengen Area - visa-free for tourism",
            "entry_type": "Visa-free"
        },
        "United Kingdom": {
            "visa_required": False,
            "max_stay": "6 months",
            "requirements": [
                "Valid passport",
                "Return ticket",
                "Proof of funds",
                "Accommodation details"
            ],
            "notes": "Electronic Travel Authorization (ETA) required from 2024",
            "entry_type": "Visa-free with ETA"
        },
        "Japan": {
            "visa_required": False,
            "max_stay": "90 days",
            "requirements": [
                "Valid passport",
                "Return ticket",
                "Proof of funds",
                "Visit Japan Web registration"
            ],
            "notes": "Register on Visit Japan Web before arrival",
            "entry_type": "Visa-free"
        },
        "Australia": {
            "visa_required": True,
            "visa_type": "ETA (Electronic Travel Authority)",
            "max_stay": "90 days",
            "requirements": [
                "Valid passport",
                "ETA application online",
                "Return ticket"
            ],
            "processing_time": "Usually instant to 24 hours",
            "cost": "AUD 20",
            "notes": "Apply online through Australian ETA app",
            "entry_type": "ETA required"
        },
        "China": {
            "visa_required": True,
            "visa_type": "Tourist Visa (L)",
            "max_stay": "30-90 days",
            "requirements": [
                "Valid passport (6 months validity, 2 blank pages)",
                "Completed visa application form",
                "Passport photo",
                "Flight itinerary",
                "Hotel reservations",
                "Proof of funds"
            ],
            "processing_time": "4-5 business days",
            "cost": "$140-160",
            "notes": "Apply at Chinese embassy or visa center",
            "entry_type": "Visa required"
        },
        "Brazil": {
            "visa_required": False,
            "max_stay": "90 days",
            "requirements": [
                "Valid passport (6 months validity)",
                "Return ticket",
                "Proof of funds"
            ],
            "notes": "Visa-free for US citizens since 2019",
            "entry_type": "Visa-free"
        },
        "India": {
            "visa_required": True,
            "visa_type": "e-Tourist Visa",
            "max_stay": "90 days",
            "requirements": [
                "Valid passport (6 months validity, 2 blank pages)",
                "Digital photo",
                "Return ticket",
                "Accommodation details"
            ],
            "processing_time": "3-5 business days",
            "cost": "$25-100 depending on duration",
            "notes": "Apply online at indianvisaonline.gov.in",
            "entry_type": "e-Visa"
        },
        "Thailand": {
            "visa_required": False,
            "max_stay": "30 days",
            "requirements": [
                "Valid passport (6 months validity)",
                "Return ticket within 30 days",
                "Proof of funds (20,000 THB)"
            ],
            "notes": "Can extend for additional 30 days at immigration office",
            "entry_type": "Visa-free"
        },
        "UAE": {
            "visa_required": False,
            "max_stay": "30 days",
            "requirements": [
                "Valid passport (6 months validity)",
                "Return ticket",
                "Accommodation booking"
            ],
            "notes": "Visa on arrival, free for US citizens",
            "entry_type": "Visa on arrival"
        }
    }

    # Extract country from destination (handle "Paris, France" format)
    if "," in destination:
        parts = destination.split(",")
        dest_country = parts[-1].strip()
    else:
        dest_country = destination.strip()

    # Handle common country name variations
    country_mapping = {
        "UK": "United Kingdom",
        "Britain": "United Kingdom",
        "England": "United Kingdom",
        "US": "United States",
        "USA": "United States",
        "Emirates": "UAE",
        "Dubai": "UAE"
    }

    dest_country = country_mapping.get(dest_country, dest_country)

    # Look up visa info
    if dest_country in visa_database:
        visa_info = visa_database[dest_country]
        return {
            "destination": destination,
            "destination_country": dest_country,
            "citizenship": citizenship,
            "visa_info": visa_info,
            "source": "visa_database",
            "status": "success"
        }

    # Default response for unknown destinations
    return {
        "destination": destination,
        "destination_country": dest_country,
        "citizenship": citizenship,
        "visa_info": {
            "visa_required": "Check with embassy",
            "max_stay": "Varies",
            "requirements": [
                "Valid passport",
                "Check with destination embassy or consulate"
            ],
            "notes": f"Please verify requirements at the {dest_country} embassy"
        },
        "source": "default",
        "status": "partial"
    }


def get_visa_application_steps(destination: str) -> Dict[str, Any]:
    """
    Get step-by-step visa application instructions.

    Args:
        destination: Destination country

    Returns:
        Application steps and timeline
    """
    # Get basic visa info
    visa_info = check_visa_requirements("United States", destination)

    if visa_info["visa_info"].get("visa_required") == False:
        return {
            "destination": destination,
            "steps": [
                "1. Ensure passport is valid for required period",
                "2. Book flights and accommodation",
                "3. Prepare proof of funds",
                "4. Print return ticket and hotel reservations",
                "5. Travel and present documents at immigration"
            ],
            "timeline": "No advance visa application needed",
            "status": "success"
        }

    return {
        "destination": destination,
        "steps": [
            "1. Check passport validity (usually 6 months required)",
            "2. Gather required documents",
            "3. Complete visa application form",
            "4. Pay visa fee",
            "5. Submit application (online or at embassy)",
            "6. Wait for processing",
            "7. Collect visa or receive e-visa"
        ],
        "timeline": "Start process 4-6 weeks before travel",
        "tips": [
            "Apply early to avoid delays",
            "Double-check all documents before submission",
            "Keep copies of all submitted documents"
        ],
        "status": "success"
    }
