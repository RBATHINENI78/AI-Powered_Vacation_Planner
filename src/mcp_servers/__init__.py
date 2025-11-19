"""
MCP Servers for Vacation Planner
Real-time flight and hotel data via Amadeus API
"""

from .amadeus_client import AmadeusClient
from .amadeus_flights import search_flights_amadeus
from .amadeus_hotels import search_hotels_amadeus

__all__ = ['AmadeusClient', 'search_flights_amadeus', 'search_hotels_amadeus']
