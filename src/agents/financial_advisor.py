"""
Financial Advisor Agent - Budget Planning and Currency Exchange
Uses external currency APIs (MCP pattern)
"""

import os
import httpx
from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent


class FinancialAdvisorAgent(BaseAgent):
    """
    Financial Advisor Agent for budget planning and currency exchange.
    Integrates with currency exchange APIs (MCP pattern).
    Uses RestCountries API for currency detection and ExchangeRate API for conversion.
    Uses LLM knowledge for budget estimates instead of static data.
    """

    def __init__(self):
        super().__init__(
            name="financial_advisor",
            description="Manages budget planning and currency exchange"
        )

        self.api_key = os.getenv("EXCHANGERATE_API_KEY")
        self.base_url = "https://v6.exchangerate-api.com/v6"

        # Register A2A message handlers
        self.register_message_handler("budget_request", self._handle_budget_request)
        self.register_message_handler("currency_request", self._handle_currency_request)

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive budget plan with currency conversion.

        Args:
            input_data: Contains budget details and destination

        Returns:
            Complete financial plan
        """
        destination = input_data.get("destination", "")
        origin = input_data.get("origin", "USA")
        budget_total = input_data.get("budget", 3000)
        travelers = input_data.get("travelers", 2)
        nights = input_data.get("nights", 7)
        travel_style = input_data.get("travel_style", "moderate")

        # Get currency exchange using RestCountries API
        currency_info = await self._get_currency_exchange(origin, destination, budget_total)

        # Create budget breakdown (LLM-powered - returns instruction for LLM to generate estimates)
        budget_breakdown = self._create_budget_breakdown_llm(
            destination, budget_total, travelers, nights, travel_style
        )

        # Get cost saving tips
        saving_tips = self._get_saving_tips(destination, travel_style)

        # Send budget info to other agents
        self.send_message(
            to_agent="orchestrator",
            message_type="budget_update",
            content={
                "total_budget": budget_total,
                "destination": destination
            }
        )

        return {
            "status": "success",
            "destination": destination,
            "currency_info": currency_info,
            "budget_breakdown": budget_breakdown,
            "saving_tips": saving_tips,
            "payment_recommendations": self._get_payment_tips(destination)
        }

    async def _get_currency_exchange(self, origin: str, destination: str, amount: float = 1.0) -> Dict[str, Any]:
        """
        Get currency exchange rate using RestCountries API for currency detection.

        Args:
            origin: Origin location (country or city)
            destination: Destination location (country or city)
            amount: Amount to convert

        Returns:
            Currency exchange information
        """
        # Get currencies from RestCountries API
        origin_currency, origin_currency_name, origin_country = await self._get_currency_from_restcountries(origin)
        dest_currency, dest_currency_name, dest_country = await self._get_currency_from_restcountries(destination)

        # Handle currency detection failures
        if not origin_currency:
            return {
                "error": "currency_detection_failed",
                "location": origin,
                "message": f"Could not automatically determine the currency for '{origin}'.",
                "instruction": f"Please identify the country for '{origin}' and provide its currency code."
            }

        if not dest_currency:
            return {
                "error": "currency_detection_failed",
                "location": destination,
                "message": f"Could not automatically determine the currency for '{destination}'.",
                "instruction": f"Please identify the country for '{destination}' and provide its currency code."
            }

        # If same currency, no conversion needed
        if origin_currency == dest_currency:
            return {
                "origin": origin,
                "origin_country": origin_country,
                "destination": destination,
                "destination_country": dest_country,
                "from_currency": origin_currency,
                "from_currency_name": origin_currency_name,
                "to_currency": dest_currency,
                "to_currency_name": dest_currency_name,
                "rate": 1.0,
                "amount": amount,
                "converted": amount,
                "message": f"Same currency - no conversion needed. Both {origin} and {destination} use {origin_currency_name} ({origin_currency})."
            }

        # Fetch real-time exchange rate
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{origin_currency}/{dest_currency}/{amount}"
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("result") == "success":
                        return {
                            "origin": origin,
                            "origin_country": origin_country,
                            "destination": destination,
                            "destination_country": dest_country,
                            "from_currency": origin_currency,
                            "from_currency_name": origin_currency_name,
                            "to_currency": dest_currency,
                            "to_currency_name": dest_currency_name,
                            "rate": data["conversion_rate"],
                            "amount": amount,
                            "converted": round(data["conversion_result"], 2),
                            "formatted": f"1 {origin_currency} = {data['conversion_rate']} {dest_currency}",
                            "conversion_example": f"{amount} {origin_currency} = {round(data['conversion_result'], 2)} {dest_currency}",
                            "last_updated": data.get("time_last_update_utc", "N/A")
                        }
            return {"error": f"Exchange rate API returned status {response.status_code}"}
        except Exception as e:
            logger.error(f"Failed to fetch exchange rate: {str(e)}")
            return {"error": f"Failed to fetch exchange rate: {str(e)}"}

    async def _get_currency_from_restcountries(self, location_name: str) -> tuple:
        """
        Fetch currency info from RestCountries API.

        Returns:
            (currency_code, currency_name, country_name) or (None, None, None) if not found
        """
        parts = [p.strip() for p in location_name.split(",")]

        for part in reversed(parts):
            try:
                # Try exact match first
                url = f"https://restcountries.com/v3.1/name/{part}?fullText=true&fields=name,currencies"
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            country_data = data[0]
                            country_name = country_data.get("name", {}).get("common", part)
                            currencies = country_data.get("currencies", {})
                            if currencies:
                                currency_code = list(currencies.keys())[0]
                                currency_name = currencies[currency_code].get("name", currency_code)
                                return currency_code, currency_name, country_name

                    # Try partial match
                    url = f"https://restcountries.com/v3.1/name/{part}?fields=name,currencies"
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 0:
                            # Find best match
                            best_match = None
                            for country in data:
                                common_name = country.get("name", {}).get("common", "")
                                official_name = country.get("name", {}).get("official", "")
                                if common_name.lower() == part.lower() or official_name.lower() == part.lower():
                                    best_match = country
                                    break
                                if best_match is None or len(common_name) < len(best_match.get("name", {}).get("common", "")):
                                    best_match = country

                            if best_match:
                                country_name = best_match.get("name", {}).get("common", part)
                                currencies = best_match.get("currencies", {})
                                if currencies:
                                    currency_code = list(currencies.keys())[0]
                                    currency_name = currencies[currency_code].get("name", currency_code)
                                    return currency_code, currency_name, country_name
            except Exception:
                continue

        return None, None, None

    def _create_budget_breakdown_llm(
        self,
        destination: str,
        total_budget: float,
        travelers: int,
        nights: int,
        travel_style: str
    ) -> Dict[str, Any]:
        """
        Create LLM-powered budget breakdown instruction.

        Returns structured data for LLM to generate realistic budget estimates
        based on its knowledge of typical costs in the destination.
        """
        return {
            "destination": destination,
            "total_budget": total_budget,
            "travelers": travelers,
            "nights": nights,
            "travel_style": travel_style,
            "instruction_for_llm": f"""Using your knowledge of typical travel costs, provide a REALISTIC budget breakdown for {destination}:

**Trip Details:**
- Destination: {destination}
- Duration: {nights} nights
- Travelers: {travelers}
- Travel Style: {travel_style}
- Total Budget: ${total_budget:,.2f}

**REQUIRED: Provide detailed cost estimates for each category:**

1. **Flights** (round-trip for {travelers} travelers)
   - Based on typical flight costs to {destination}
   - Consider travel style: budget carriers vs. premium airlines

2. **Accommodation** ({nights} nights)
   - {travel_style.title()} tier hotels/accommodations
   - Cost per night and total

3. **Food and Dining**
   - Breakfast, lunch, dinner for {nights} days
   - Consider {travel_style} dining (street food vs. restaurants vs. fine dining)

4. **Activities and Attractions**
   - Typical tourist activities in {destination}
   - Entry fees, tours, experiences

5. **Local Transportation**
   - Within-city transport (metro, taxis, car rentals)
   - Based on {destination}'s transport infrastructure

6. **Miscellaneous**
   - Shopping, tips, unexpected expenses
   - Travel insurance, visa fees if applicable

7. **Emergency Fund** (10% of subtotal)

**IMPORTANT:**
- Use REALISTIC prices based on {destination}'s actual cost of living
- Adjust for {travel_style} level (budget/moderate/luxury)
- Provide SPECIFIC dollar amounts, not ranges
- Total should be close to ${total_budget:,.2f} but be honest if it's insufficient
- Include per-person and per-day costs

Format as a structured breakdown with specific amounts for each category."""
        }


    def _assess_budget(
        self,
        user_budget: float,
        estimated_cost: float,
        travel_style: str
    ) -> Dict[str, Any]:
        """Assess if budget is sufficient."""
        difference = user_budget - estimated_cost
        percentage = (difference / user_budget) * 100 if user_budget > 0 else 0

        if difference >= 0:
            if percentage > 20:
                status = "comfortable"
                message = f"Budget is comfortable with {percentage:.0f}% buffer"
            else:
                status = "adequate"
                message = f"Budget is adequate with {percentage:.0f}% buffer"
        else:
            status = "insufficient"
            message = f"Budget is short by ${abs(difference):.2f}"

        recommendations = []
        if status == "insufficient":
            recommendations = [
                f"Consider reducing trip to {int((user_budget / estimated_cost) * 7)} nights",
                "Switch to budget accommodations",
                "Reduce planned activities",
                "Look for flight deals or alternative airports"
            ]
        elif status == "adequate":
            recommendations = [
                "Consider travel insurance",
                "Keep emergency fund accessible"
            ]

        return {
            "within_budget": difference >= 0,
            "status": status,
            "difference": round(difference, 2),
            "buffer_percentage": round(percentage, 1),
            "message": message,
            "recommendations": recommendations
        }

    def _get_saving_tips(self, destination: str, travel_style: str) -> List[str]:
        """Get cost-saving tips for destination."""
        general_tips = [
            "Book flights 6-8 weeks in advance",
            "Use public transportation instead of taxis",
            "Eat at local restaurants, not tourist spots",
            "Get a travel credit card with no foreign fees"
        ]

        destination_tips = {
            "France": [
                "Get a Paris Museum Pass for multiple attractions",
                "Buy wine at supermarkets, not restaurants",
                "Use Navigo pass for unlimited metro travel"
            ],
            "Japan": [
                "Get a JR Pass for train travel",
                "Eat at convenience stores (high quality, low cost)",
                "Visit free temples and shrines"
            ],
            "UK": [
                "Get an Oyster card for London transport",
                "Book train tickets in advance for discounts",
                "Visit free museums (British Museum, Tate Modern)"
            ]
        }

        dest_country = destination.split(",")[-1].strip() if "," in destination else destination
        specific_tips = destination_tips.get(dest_country, [])

        return general_tips + specific_tips

    def _get_payment_tips(self, destination: str) -> List[str]:
        """Get payment recommendations for destination."""
        return [
            "Notify your bank of travel dates",
            "Carry some local cash for small purchases",
            "Use credit cards for large purchases (better rates)",
            "Avoid airport currency exchange (poor rates)",
            "Consider a travel card with no foreign transaction fees"
        ]

    def _handle_budget_request(self, message) -> Dict[str, Any]:
        """Handle A2A budget request."""
        logger.info(f"[A2A] Processing budget request from {message.from_agent}")
        return {"status": "acknowledged"}

    def _handle_currency_request(self, message) -> Dict[str, Any]:
        """Handle A2A currency request."""
        logger.info(f"[A2A] Processing currency request from {message.from_agent}")
        return {"status": "acknowledged"}
