"""
Centralized Configuration for ADK Vacation Planner
All configurable settings in one place
"""

import os
from typing import Dict, Any


class Config:
    """
    Centralized configuration for the vacation planner.

    Override settings via environment variables or modify defaults here.
    """

    # ==================== MODEL CONFIGURATION ====================

    # Default model for all agents
    # Using gemini-2.5-flash-lite for better rate limits
    DEFAULT_MODEL = os.getenv("ADK_DEFAULT_MODEL", "gemini-2.5-flash-lite")

    # Per-agent model overrides (optional)
    # Strategy: Match model to task complexity for optimal performance and rate limits
    AGENT_MODELS: Dict[str, str] = {
        # Simple data retrieval - use lite for speed and rate limits
        "travel_advisory": "gemini-2.5-flash-lite",          # Check advisories
        "destination_intelligence": "gemini-2.5-flash-lite",  # Weather/packing
        "immigration_specialist": "gemini-2.5-flash-lite",    # Visa requirements
        "currency_exchange": "gemini-2.5-flash-lite",         # Currency conversion

        # Booking agents - medium complexity, use lite (parallel execution)
        "flight_booking": "gemini-2.5-flash-lite",
        "hotel_booking": "gemini-2.5-flash-lite",
        "car_rental": "gemini-2.5-flash-lite",

        # Complex planning - use 2.0-flash-exp for better reasoning
        "activities": "gemini-2.0-flash-exp",                  # Creative activity planning
        "itinerary": "gemini-2.0-flash-exp",                   # Complex scheduling
        "suggestions_checkpoint": "gemini-2.0-flash-exp",      # Quality review

        # Critical analysis - use thinking model
        "budget_checkpoint": "gemini-2.0-flash-thinking-exp-1219",  # Budget analysis

        # Document generation - needs quality
        "document_generator": "gemini-2.0-flash-exp",

        # Budget fitting agents (LoopAgent implementation)
        "budget_assessment": "gemini-2.0-flash-thinking-exp-1219",  # Complex STOP/CONTINUE logic
        "tier_recommendation": "gemini-2.5-flash-lite",       # Simple tier selection
        "budget_fitting_loop": "gemini-2.5-flash-lite",       # Loop orchestration
    }

    # ==================== API CONFIGURATION ====================

    # API Keys (loaded from environment variables)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    # ==================== FEATURE FLAGS ====================

    # Use Amadeus MCP for flight/hotel bookings (requires credentials)
    # If False or Amadeus returns test data, fallback to Tavily MCP search
    USE_AMADEUS_API = os.getenv("USE_AMADEUS_API", "true").lower() == "true"

    # Amadeus environment: "test" or "production"
    # When "test", system will detect test data and fallback to Tavily
    AMADEUS_ENV = os.getenv("AMADEUS_ENV", "test")

    # Auto-detect Amadeus test data and fallback to Tavily
    # When True, system detects test data patterns and uses Tavily MCP
    AUTO_DETECT_TEST_DATA = os.getenv("AUTO_DETECT_TEST_DATA", "true").lower() == "true"

    # Force Tavily MCP for all searches (bypass Amadeus completely)
    FORCE_TAVILY_SEARCH = os.getenv("FORCE_TAVILY_SEARCH", "false").lower() == "true"

    # ==================== TIMEOUT SETTINGS ====================

    # API timeouts (in seconds)
    WEATHER_API_TIMEOUT = int(os.getenv("WEATHER_API_TIMEOUT", "30"))
    AMADEUS_API_TIMEOUT = int(os.getenv("AMADEUS_API_TIMEOUT", "15"))
    CURRENCY_API_TIMEOUT = int(os.getenv("CURRENCY_API_TIMEOUT", "10"))

    # ==================== RATE LIMIT SETTINGS ====================

    # Retry configuration for rate limits (free tier: 15 RPM)
    # Enable automatic retry with 30-second wait for rate limit errors
    ENABLE_RATE_LIMIT_RETRY = os.getenv("ENABLE_RATE_LIMIT_RETRY", "true").lower() == "true"
    RATE_LIMIT_RETRY_DELAY = int(os.getenv("RATE_LIMIT_RETRY_DELAY", "30"))  # seconds
    RATE_LIMIT_MAX_RETRIES = int(os.getenv("RATE_LIMIT_MAX_RETRIES", "3"))

    # ==================== LOGGING ====================

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # ==================== HELPER METHODS ====================

    @classmethod
    def get_model_for_agent(cls, agent_name: str) -> str:
        """
        Get the model to use for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., "travel_advisory")

        Returns:
            Model name to use (e.g., "gemini-1.5-flash")
        """
        return cls.AGENT_MODELS.get(agent_name, cls.DEFAULT_MODEL)

    @classmethod
    def get_model_config(cls, agent_name: str) -> Dict[str, Any]:
        """
        Get the complete model configuration for an agent.

        Returns a dict with model name and Vertex AI configuration if available.
        This ensures agents use Vertex AI when credentials are available.

        Args:
            agent_name: Name of the agent

        Returns:
            Dict with 'model' and optionally 'vertexai', 'project', 'location'
        """
        config = {
            "model": cls.get_model_for_agent(agent_name)
        }

        # If Vertex AI credentials are available, add them
        if cls.GOOGLE_APPLICATION_CREDENTIALS and cls.GOOGLE_CLOUD_PROJECT:
            config.update({
                "vertexai": True,
                "project": cls.GOOGLE_CLOUD_PROJECT,
                "location": cls.GOOGLE_CLOUD_LOCATION
            })

        return config

    @classmethod
    def get_amadeus_base_url(cls) -> str:
        """Get Amadeus API base URL based on environment."""
        if cls.AMADEUS_ENV == "production":
            return "https://api.amadeus.com"
        else:
            return "https://test.api.amadeus.com"

    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)."""
        print("="*80)
        print("VACATION PLANNER CONFIGURATION")
        print("="*80)
        print(f"\n[MODEL SETTINGS]")
        print(f"  Default Model: {cls.DEFAULT_MODEL}")
        print(f"  Agent-specific overrides: {len(cls.AGENT_MODELS)}")
        for agent, model in cls.AGENT_MODELS.items():
            print(f"    - {agent}: {model}")

        print(f"\n[API SETTINGS]")
        print(f"  Google API Key: {'✓ Set' if cls.GOOGLE_API_KEY else '✗ Missing'}")
        print(f"  OpenWeather API Key: {'✓ Set' if cls.OPENWEATHER_API_KEY else '✗ Missing'}")
        print(f"  Amadeus Client ID: {'✓ Set' if cls.AMADEUS_CLIENT_ID else '✗ Missing'}")
        print(f"  Amadeus Client Secret: {'✓ Set' if cls.AMADEUS_CLIENT_SECRET else '✗ Missing'}")

        print(f"\n[FEATURE FLAGS]")
        print(f"  Use Amadeus API: {cls.USE_AMADEUS_API}")
        print(f"  Amadeus Environment: {cls.AMADEUS_ENV}")
        print(f"  Amadeus Base URL: {cls.get_amadeus_base_url()}")

        print(f"\n[TIMEOUTS]")
        print(f"  Weather API: {cls.WEATHER_API_TIMEOUT}s")
        print(f"  Amadeus API: {cls.AMADEUS_API_TIMEOUT}s")
        print(f"  Currency API: {cls.CURRENCY_API_TIMEOUT}s")

        print(f"\n[LOGGING]")
        print(f"  Log Level: {cls.LOG_LEVEL}")

        print("\n" + "="*80)


# Create singleton instance
config = Config()


if __name__ == "__main__":
    # Print configuration when run directly
    Config.print_config()
