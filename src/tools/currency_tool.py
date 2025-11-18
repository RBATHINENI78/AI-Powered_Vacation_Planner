"""
Currency Tool - Real-time currency conversion from ExchangeRate API
"""

import os
import httpx
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

EXCHANGERATE_API_KEY = os.getenv("EXCHANGERATE_API_KEY")


def get_currency_exchange(
    from_currency: str,
    to_currency: str,
    amount: float = 1.0
) -> Dict[str, Any]:
    """
    Get currency exchange rate and convert amount using ExchangeRate API.

    Args:
        from_currency: Source currency code (e.g., USD)
        to_currency: Target currency code (e.g., EUR)
        amount: Amount to convert

    Returns:
        Currency conversion information
    """
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/pair/{from_currency}/{to_currency}/{amount}"

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)

            if response.status_code == 200:
                data = response.json()

                if data.get("result") == "success":
                    rate = data["conversion_rate"]
                    converted = data["conversion_result"]

                    return {
                        "from_currency": from_currency,
                        "to_currency": to_currency,
                        "exchange_rate": rate,
                        "original_amount": amount,
                        "converted_amount": round(converted, 2),
                        "formatted": f"{amount} {from_currency} = {round(converted, 2)} {to_currency}",
                        "last_updated": data.get("time_last_update_utc", "N/A"),
                        "source": "exchangerate_api",
                        "status": "success"
                    }
                else:
                    return {
                        "error": data.get("error-type", "Unknown error"),
                        "source": "error",
                        "status": "error"
                    }
            else:
                return {
                    "error": f"API error: {response.status_code}",
                    "source": "error",
                    "status": "error"
                }

    except Exception as e:
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "error": str(e),
            "source": "error",
            "status": "error"
        }


def get_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """
    Get just the exchange rate without conversion.

    Args:
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        Exchange rate information
    """
    return get_currency_exchange(from_currency, to_currency, 1.0)


def convert_budget(
    budget_items: Dict[str, float],
    from_currency: str,
    to_currency: str
) -> Dict[str, Any]:
    """
    Convert a complete budget from one currency to another.

    Args:
        budget_items: Dictionary of budget items and their costs
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        Converted budget with all items
    """
    # Get the exchange rate first
    rate_info = get_exchange_rate(from_currency, to_currency)

    if rate_info.get("status") == "error":
        return rate_info

    rate = rate_info["exchange_rate"]

    # Convert each budget item
    converted_items = {}
    total_original = 0
    total_converted = 0

    for item, cost in budget_items.items():
        converted_cost = round(cost * rate, 2)
        converted_items[item] = {
            "original": f"{cost} {from_currency}",
            "converted": f"{converted_cost} {to_currency}"
        }
        total_original += cost
        total_converted += converted_cost

    return {
        "budget_items": converted_items,
        "total_original": f"{total_original} {from_currency}",
        "total_converted": f"{round(total_converted, 2)} {to_currency}",
        "exchange_rate": rate,
        "source": "exchangerate_api",
        "status": "success"
    }
