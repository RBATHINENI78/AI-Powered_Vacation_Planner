"""
Pure ADK Currency Exchange Agent
Budget planning and currency conversion using ADK patterns
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

from tools.currency_tools import (
    get_currency_for_country,
    get_exchange_rate,
    get_budget_breakdown
)


class CurrencyExchangeAgent(Agent):
    """
    Pure ADK Currency Exchange Agent.

    Handles currency conversion, budget planning, and financial advice for travel.
    Integrates with RestCountries API and ExchangeRate API for real-time data.
    """

    def __init__(self):
        super().__init__(
            name="currency_exchange",
            description="""You are a financial advisor specializing in travel budgets and currency exchange.

RESPONSIBILITIES:
1. Call get_currency_for_country to identify currencies for origin and destination
2. Call get_exchange_rate to get real-time conversion rates
3. Call get_budget_breakdown to create detailed budget plan

BUDGET PLANNING:
- Analyze total budget vs destination costs
- Break down: flights, hotels, food, transport, activities, misc
- Identify if budget is sufficient
- Suggest cost-saving tips

CURRENCY EXCHANGE:
- Identify origin and destination currencies
- Provide real-time exchange rate
- Convert budget to local currency

OUTPUT FORMAT:
Provide:
- Currency exchange rate and converted budget
- Detailed budget breakdown with dollar amounts
- Budget sufficiency analysis
- Cost-saving tips

DO NOT INCLUDE:
- Payment method recommendations
- Credit card advice
- ATM information
- Tipping customs

IMPORTANT:
- Use actual exchange rates from get_exchange_rate
- Base budget estimates on real destination costs
- Consider travel style (budget/moderate/luxury)
- Account for seasonal price variations""",
            model=Config.get_model_for_agent("currency_exchange"),
            tools=[
                FunctionTool(get_currency_for_country),
                FunctionTool(get_exchange_rate),
                FunctionTool(get_budget_breakdown)
            ]
        )
