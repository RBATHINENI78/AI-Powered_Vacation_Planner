"""
Amadeus API Client for flight and hotel searches
"""

import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class AmadeusClient:
    """Client for Amadeus Travel API"""

    def __init__(self):
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        self.base_url = "https://test.api.amadeus.com"  # Use production URL for live data
        self.token = None
        self.token_expires = None

    async def _get_token(self) -> str:
        """Get OAuth2 access token"""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token

        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code == 200:
                result = response.json()
                self.token = result["access_token"]
                # Token expires in seconds, subtract 60 for safety margin
                expires_in = result.get("expires_in", 1799) - 60
                from datetime import timedelta
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)
                return self.token
            else:
                logger.error(f"Failed to get Amadeus token: {response.text}")
                raise Exception(f"Authentication failed: {response.status_code}")

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for flight offers

        Args:
            origin: IATA airport code (e.g., JFK)
            destination: IATA airport code (e.g., CDG)
            departure_date: Date in YYYY-MM-DD format
            return_date: Optional return date
            adults: Number of adult passengers
            max_results: Maximum number of results
        """
        token = await self._get_token()

        url = f"{self.base_url}/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "max": max_results,
            "currencyCode": "USD"
        }

        if return_date:
            params["returnDate"] = return_date

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Flight search failed: {response.text}")
                return {"error": response.text, "status": response.status_code}

    async def search_hotels(
        self,
        city_code: str,
        check_in: str,
        check_out: str,
        adults: int = 1,
        rooms: int = 1,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search for hotel offers

        Args:
            city_code: IATA city code (e.g., PAR for Paris)
            check_in: Check-in date YYYY-MM-DD
            check_out: Check-out date YYYY-MM-DD
            adults: Number of adults
            rooms: Number of rooms
            max_results: Maximum results
        """
        token = await self._get_token()

        # First get hotel list by city
        url = f"{self.base_url}/v1/reference-data/locations/hotels/by-city"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "cityCode": city_code,
            "radius": 20,
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code != 200:
                return {"error": response.text, "status": response.status_code}

            hotels_data = response.json()
            hotel_ids = [h["hotelId"] for h in hotels_data.get("data", [])[:max_results]]

            if not hotel_ids:
                return {"error": "No hotels found", "data": []}

            # Get offers for these hotels
            offers_url = f"{self.base_url}/v3/shopping/hotel-offers"
            offers_params = {
                "hotelIds": ",".join(hotel_ids),
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "adults": adults,
                "roomQuantity": rooms,
                "currency": "USD"
            }

            response = await client.get(offers_url, headers=headers, params=offers_params)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.text, "status": response.status_code}

    async def get_airport_code(self, city_name: str) -> str:
        """Get IATA airport code for a city"""
        token = await self._get_token()

        url = f"{self.base_url}/v1/reference-data/locations"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "keyword": city_name,
            "subType": "AIRPORT,CITY"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("data"):
                    return data["data"][0]["iataCode"]

            # Fallback to common mappings
            city_codes = {
                "New York": "JFK", "NYC": "JFK",
                "Paris": "CDG",
                "London": "LHR",
                "Tokyo": "NRT",
                "Los Angeles": "LAX",
                "Chicago": "ORD",
                "Kochi": "COK",
                "Mumbai": "BOM",
                "Delhi": "DEL"
            }
            return city_codes.get(city_name, city_name[:3].upper())
