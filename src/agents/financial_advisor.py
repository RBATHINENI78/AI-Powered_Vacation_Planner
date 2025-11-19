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

        # Cost estimates by destination (per day, in USD)
        self.destination_costs = {
            "France": {"budget": 100, "moderate": 200, "luxury": 400},
            "Japan": {"budget": 80, "moderate": 180, "luxury": 350},
            "UK": {"budget": 120, "moderate": 220, "luxury": 450},
            "Italy": {"budget": 90, "moderate": 180, "luxury": 380},
            "Thailand": {"budget": 40, "moderate": 80, "luxury": 200},
            "Australia": {"budget": 100, "moderate": 200, "luxury": 400},
            "Germany": {"budget": 90, "moderate": 170, "luxury": 350},
            "Spain": {"budget": 80, "moderate": 160, "luxury": 320}
        }

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive budget plan with currency conversion.

        Args:
            input_data: Contains budget details and destination

        Returns:
            Complete financial plan
        """
        destination = input_data.get("destination", "")
        from_currency = input_data.get("from_currency", "USD")
        budget_total = input_data.get("budget", 3000)
        travelers = input_data.get("travelers", 2)
        nights = input_data.get("nights", 7)
        travel_style = input_data.get("travel_style", "moderate")

        # Get destination currency
        to_currency = self._get_destination_currency(destination)

        # Get exchange rate
        exchange_info = await self._get_exchange_rate(from_currency, to_currency)

        # Create budget breakdown
        budget_breakdown = self._create_budget_breakdown(
            destination, budget_total, travelers, nights, travel_style
        )

        # Convert budget to destination currency
        converted_budget = self._convert_budget(
            budget_breakdown,
            exchange_info.get("rate", 1.0),
            to_currency
        )

        # Get cost saving tips
        saving_tips = self._get_saving_tips(destination, travel_style)

        # Calculate if budget is sufficient
        budget_assessment = self._assess_budget(
            budget_total, budget_breakdown["total"], travel_style
        )

        # Send budget info to other agents
        self.send_message(
            to_agent="orchestrator",
            message_type="budget_update",
            content={
                "total_budget": budget_total,
                "estimated_cost": budget_breakdown["total"],
                "within_budget": budget_assessment["within_budget"]
            }
        )

        return {
            "status": "success",
            "destination": destination,
            "currency_info": {
                "from": from_currency,
                "to": to_currency,
                "exchange_rate": exchange_info.get("rate", 1.0),
                "last_updated": exchange_info.get("last_updated", "N/A")
            },
            "budget_breakdown": budget_breakdown,
            "converted_budget": converted_budget,
            "budget_assessment": budget_assessment,
            "saving_tips": saving_tips,
            "payment_recommendations": self._get_payment_tips(destination)
        }

    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get current exchange rate from API."""
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    if data.get("result") == "success":
                        return {
                            "rate": data["conversion_rate"],
                            "last_updated": data.get("time_last_update_utc", "N/A"),
                            "source": "exchangerate_api"
                        }

            # Fallback rates
            return self._get_fallback_rate(from_currency, to_currency)

        except Exception as e:
            logger.error(f"Exchange rate fetch error: {e}")
            return self._get_fallback_rate(from_currency, to_currency)

    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get fallback exchange rate."""
        fallback_rates = {
            ("USD", "EUR"): 0.92,
            ("USD", "GBP"): 0.79,
            ("USD", "JPY"): 149.50,
            ("USD", "THB"): 35.50,
            ("USD", "AUD"): 1.53
        }

        rate = fallback_rates.get((from_currency, to_currency), 1.0)
        return {
            "rate": rate,
            "last_updated": "Fallback rate",
            "source": "fallback"
        }

    def _get_destination_currency(self, destination: str) -> str:
        """Get currency code for destination."""
        currency_map = {
            "France": "EUR",
            "Germany": "EUR",
            "Italy": "EUR",
            "Spain": "EUR",
            "UK": "GBP",
            "Japan": "JPY",
            "Thailand": "THB",
            "Australia": "AUD"
        }

        dest_country = destination.split(",")[-1].strip() if "," in destination else destination
        return currency_map.get(dest_country, "USD")

    def _create_budget_breakdown(
        self,
        destination: str,
        total_budget: float,
        travelers: int,
        nights: int,
        travel_style: str
    ) -> Dict[str, Any]:
        """Create detailed budget breakdown."""
        dest_country = destination.split(",")[-1].strip() if "," in destination else destination

        # Get daily costs
        daily_costs = self.destination_costs.get(
            dest_country,
            {"budget": 80, "moderate": 160, "luxury": 320}
        )
        daily_per_person = daily_costs.get(travel_style, daily_costs["moderate"])

        # Calculate components
        accommodation = daily_per_person * 0.35 * nights * travelers
        food = daily_per_person * 0.25 * nights * travelers
        activities = daily_per_person * 0.20 * nights * travelers
        transport = daily_per_person * 0.15 * nights * travelers
        misc = daily_per_person * 0.05 * nights * travelers

        # Estimate flights (rough estimates)
        flight_estimates = {
            "France": 800, "Japan": 1200, "UK": 700,
            "Italy": 850, "Thailand": 1000, "Australia": 1500
        }
        flights = flight_estimates.get(dest_country, 800) * travelers

        subtotal = accommodation + food + activities + transport + misc + flights
        emergency_fund = subtotal * 0.10
        total = subtotal + emergency_fund

        return {
            "flights": round(flights, 2),
            "accommodation": round(accommodation, 2),
            "food_and_dining": round(food, 2),
            "activities": round(activities, 2),
            "local_transport": round(transport, 2),
            "miscellaneous": round(misc, 2),
            "emergency_fund": round(emergency_fund, 2),
            "subtotal": round(subtotal, 2),
            "total": round(total, 2),
            "per_person": round(total / travelers, 2),
            "per_day": round((total - flights) / nights, 2)
        }

    def _convert_budget(
        self,
        budget: Dict[str, Any],
        rate: float,
        to_currency: str
    ) -> Dict[str, Any]:
        """Convert budget to destination currency."""
        converted = {}
        for key, value in budget.items():
            if isinstance(value, (int, float)):
                converted[key] = round(value * rate, 2)

        converted["currency"] = to_currency
        return converted

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
