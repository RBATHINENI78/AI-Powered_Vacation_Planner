"""
Currency Exchange Tools - Budget planning and currency conversion
Integrates with ExchangeRate API and RestCountries API
"""

import os
import httpx
from typing import Dict, Any, Optional, Tuple
from loguru import logger


async def get_currency_for_country(country: str) -> Optional[Dict[str, Any]]:
    """
    Get currency information for a country using RestCountries API.

    Args:
        country: Country name or code

    Returns:
        Currency code, name, and symbol
    """
    try:
        # Clean country name
        country_clean = country.strip().split(",")[-1].strip()

        url = f"https://restcountries.com/v3.1/name/{country_clean}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    country_data = data[0]
                    currencies = country_data.get("currencies", {})

                    if currencies:
                        # Get first currency
                        currency_code = list(currencies.keys())[0]
                        currency_info = currencies[currency_code]

                        return {
                            "country": country_data.get("name", {}).get("common", country),
                            "currency_code": currency_code,
                            "currency_name": currency_info.get("name", ""),
                            "currency_symbol": currency_info.get("symbol", ""),
                        }

        logger.warning(f"[CURRENCY] Could not find currency for {country}")
        return None

    except Exception as e:
        logger.error(f"[CURRENCY] RestCountries API error: {e}")
        return None


async def get_exchange_rate(from_currency: str, to_currency: str, amount: float = 1.0) -> Dict[str, Any]:
    """
    Get real-time exchange rate between two currencies.

    Args:
        from_currency: Source currency code (e.g., "USD")
        to_currency: Target currency code (e.g., "EUR")
        amount: Amount to convert

    Returns:
        Exchange rate and converted amount
    """
    api_key = os.getenv("EXCHANGERATE_API_KEY")

    if not api_key:
        # Fallback: Use approximate rates
        logger.warning("[CURRENCY] EXCHANGERATE_API_KEY not set, using estimates")
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": 1.0,
            "amount": amount,
            "converted": amount,
            "source": "estimate",
            "note": "Set EXCHANGERATE_API_KEY for real-time rates"
        }

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)

            if response.status_code == 200:
                data = response.json()

                if data.get("result") == "success":
                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "rate": data["conversion_rate"],
                        "amount": amount,
                        "converted": round(data["conversion_result"], 2),
                        "source": "exchangerate-api",
                        "last_updated": data.get("time_last_update_utc", "")
                    }

        logger.error(f"[CURRENCY] Exchange rate API returned non-success")
        return _fallback_exchange_rate(from_currency, to_currency, amount)

    except Exception as e:
        logger.error(f"[CURRENCY] Exchange rate error: {e}")
        return _fallback_exchange_rate(from_currency, to_currency, amount)


def _fallback_exchange_rate(from_currency: str, to_currency: str, amount: float) -> Dict[str, Any]:
    """Provide fallback exchange rates for common currencies."""
    # Simplified fallback rates (USD base)
    rates_to_usd = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 149.5,
        "CAD": 1.36,
        "AUD": 1.53,
        "CHF": 0.88,
        "CNY": 7.24,
        "INR": 83.12,
        "MXN": 17.08
    }

    from_rate = rates_to_usd.get(from_currency, 1.0)
    to_rate = rates_to_usd.get(to_currency, 1.0)

    # Convert via USD
    rate = to_rate / from_rate if from_rate != 0 else 1.0
    converted = amount * rate

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": round(rate, 4),
        "amount": amount,
        "converted": round(converted, 2),
        "source": "fallback_estimate",
        "note": "Approximate rate - set EXCHANGERATE_API_KEY for accurate data"
    }


def get_budget_breakdown(destination_country: str, budget: float, travelers: int = 2, nights: int = 7, travel_style: str = "moderate") -> Dict[str, Any]:
    """
    Get budget breakdown recommendations using LLM knowledge.

    Args:
        destination_country: Destination country
        budget: Total budget in origin currency
        travelers: Number of travelers
        nights: Number of nights
        travel_style: Travel style (budget/moderate/luxury)

    Returns:
        Structured instruction for LLM to generate budget breakdown
    """
    return {
        "destination_country": destination_country,
        "budget": budget,
        "travelers": travelers,
        "nights": nights,
        "travel_style": travel_style,
        "llm_instruction": f"""Create a detailed budget breakdown for {travelers} travelers visiting {destination_country} for {nights} nights with a total budget of ${budget:.2f} ({travel_style} style).

**Budget Categories:**

1. **Flights** (Round-trip for {travelers} people)
   - Estimated cost
   - Percentage of budget

2. **Accommodation** ({nights} nights)
   - Type based on style ({travel_style})
   - Per night cost
   - Total cost

3. **Food & Dining** ({nights + 1} days)
   - Breakfast, lunch, dinner estimates
   - Daily per person
   - Total for {travelers} people

4. **Transportation** (Local)
   - Airport transfers
   - Daily transport (metro/taxi/rental)
   - Total estimate

5. **Activities & Attractions**
   - Popular attractions/tours
   - Estimated costs
   - Total

6. **Miscellaneous**
   - Travel insurance
   - SIM card/data
   - Shopping allowance
   - Emergency fund (10% of budget)

**Analysis:**
- Is ${budget:.2f} sufficient for {destination_country}?
- Recommended allocation percentages
- Cost-saving tips for {travel_style} travelers
- Expensive vs budget-friendly alternatives

Provide specific dollar amounts based on current {destination_country} prices."""
    }


def get_payment_recommendations(destination_country: str) -> Dict[str, Any]:
    """
    Get payment method recommendations for a destination.

    Args:
        destination_country: Destination country

    Returns:
        Payment recommendations via LLM instruction
    """
    return {
        "destination_country": destination_country,
        "llm_instruction": f"""Provide payment recommendations for travelers to {destination_country}:

**Payment Methods:**
1. **Credit Cards**
   - Acceptance rate (widespread/limited)
   - Best cards to use (Visa, Mastercard, Amex)
   - Foreign transaction fees to watch for

2. **Cash**
   - How much cash to carry
   - Where to exchange (airport/banks/ATMs)
   - Cash vs card ratio

3. **ATMs**
   - Availability
   - Fees (local + foreign)
   - Daily withdrawal limits
   - Safe ATM locations

4. **Digital Payments**
   - Local payment apps (Alipay, PayPay, etc.)
   - Apple Pay/Google Pay acceptance
   - QR code payments

5. **Tips & Warnings**
   - Tipping customs (expected percentage)
   - Scams to avoid
   - Emergency cash backup recommendations

Provide specific advice for {destination_country}."""
    }


def assess_budget_fit(
    user_budget: float,
    estimated_flights_cost: float,
    estimated_hotels_cost: float,
    estimated_activities_cost: float = 500.0,
    estimated_food_cost: float = 300.0
) -> Dict[str, Any]:
    """
    🚨 MANDATORY BUDGET CHECKPOINT - Human-in-the-Loop (HITL) 🚨

    Call this AFTER getting flight and hotel estimates but BEFORE generating itinerary.
    This tool enforces budget assessment and forces you to STOP when user input is needed.

    Args:
        user_budget: User's stated budget in dollars
        estimated_flights_cost: Total flight cost from estimate_flight_cost
        estimated_hotels_cost: Total hotel cost from estimate_hotel_cost
        estimated_activities_cost: Estimated activities (default: $500)
        estimated_food_cost: Estimated food/dining (default: $300)

    Returns:
        {
            "status": "proceed" | "needs_user_input",  # IF "needs_user_input" -> STOP!
            "scenario": "budget_reasonable" | "budget_too_low" | "budget_excess",
            "message": str,
            "breakdown": {...},
            "recommendation": str  # Present this to user if needs_user_input
        }

    CRITICAL BEHAVIOR:
    - If status == "needs_user_input": You MUST display the message and recommendation,
      then STOP and WAIT for user response. DO NOT continue with itinerary.
    - If status == "proceed": Continue automatically with full trip planning.
    """
    total_estimated = (estimated_flights_cost + estimated_hotels_cost +
                      estimated_activities_cost + estimated_food_cost)

    breakdown = {
        "flights": f"${estimated_flights_cost:,.2f}",
        "hotels": f"${estimated_hotels_cost:,.2f}",
        "activities": f"${estimated_activities_cost:,.2f}",
        "food_dining": f"${estimated_food_cost:,.2f}",
        "total_estimated": f"${total_estimated:,.2f}",
        "user_budget": f"${user_budget:,.2f}",
        "difference": f"${user_budget - total_estimated:,.2f}",
        "difference_pct": f"{((user_budget - total_estimated) / total_estimated * 100) if total_estimated > 0 else 0:.1f}%"
    }

    # SCENARIO A: Budget too low (costs exceed budget by >50%)
    if total_estimated > user_budget * 1.5:
        shortage = total_estimated - user_budget
        return {
            "status": "needs_user_input",
            "scenario": "budget_too_low",
            "breakdown": breakdown,
            "message": f"⚠️ BUDGET ALERT: Estimated costs (${total_estimated:,.2f}) exceed your budget (${user_budget:,.2f}) by ${shortage:,.2f}.",
            "recommendation": (
                "🛑 STOP HERE and present these numbered options to the user:\n\n"
                f"1. Proceed anyway (will need additional funding of ~${shortage:,.2f})\n"
                f"2. Adjust budget to ${total_estimated:,.2f} (recommended minimum)\n"
                "3. Reduce scope: shorter trip, budget hotels, fewer activities\n"
                "4. Suggest alternative destinations within your budget\n\n"
                "⛔ DO NOT CONTINUE until user chooses an option."
            )
        }

    # SCENARIO B: Budget much higher than needed (budget exceeds costs by >100%)
    elif user_budget > total_estimated * 2.0:
        excess = user_budget - total_estimated
        return {
            "status": "needs_user_input",
            "scenario": "budget_excess",
            "breakdown": breakdown,
            "message": f"💰 GOOD NEWS: Your ${user_budget:,.2f} budget exceeds estimated costs (${total_estimated:,.2f}) by ${excess:,.2f}!",
            "recommendation": (
                "🛑 STOP HERE and present these numbered upgrade options to the user:\n\n"
                f"1. Upgrade accommodations: Luxury 5-star hotels/resorts (+${excess * 0.4:,.2f})\n"
                "2. Extend trip: Add more days, explore nearby destinations\n"
                f"3. Premium experiences: Private tours, fine dining, spa treatments (+${excess * 0.3:,.2f})\n"
                "4. Multi-destination: Add another city/country to your itinerary\n"
                "5. Keep current plan and save the difference\n\n"
                "⛔ DO NOT CONTINUE until user chooses an option."
            )
        }

    # SCENARIO C: Budget reasonable (within ±50%)
    else:
        return {
            "status": "proceed",
            "scenario": "budget_reasonable",
            "breakdown": breakdown,
            "message": f"✅ Budget Assessment: Your ${user_budget:,.2f} budget is reasonable for estimated costs of ${total_estimated:,.2f}.",
            "recommendation": "✓ Proceed automatically with full trip planning."
        }
