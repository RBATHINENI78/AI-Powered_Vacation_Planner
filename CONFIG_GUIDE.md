# Configuration Guide

**Date:** 2025-11-22
**Status:** ✅ **ACTIVE**

---

## Overview

The vacation planner now uses **centralized configuration** for all settings, making it easy to switch models, adjust timeouts, and configure features without editing code.

---

## Configuration File

**Location:** [`config.py`](config.py)

All settings are defined in the `Config` class. You can modify settings in three ways:

1. **Edit `config.py` directly** (persistent changes)
2. **Set environment variables** (temporary overrides)
3. **Modify per-agent settings** (granular control)

---

## Model Configuration

### Quick Start: Change Default Model

**Option 1: Environment Variable** (Recommended for testing)
```bash
export ADK_DEFAULT_MODEL="gemini-2.0-flash"
adk web agents_web --port 8080
```

**Option 2: Edit `config.py`** (Recommended for production)
```python
# In config.py
DEFAULT_MODEL = "gemini-1.5-pro"  # Change this line
```

**Option 3: Per-Agent Override** (Advanced)
```python
# In config.py
AGENT_MODELS: Dict[str, str] = {
    "travel_advisory": "gemini-1.5-pro",      # Use Pro for complex analysis
    "itinerary": "gemini-1.5-pro",            # Use Pro for detailed itinerary
    "destination_intelligence": "gemini-2.0-flash",  # Use 2.0 for fast weather
    # All other agents use DEFAULT_MODEL
}
```

---

## Available Models

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| `gemini-1.5-flash` | ⚡⚡⚡ Fast | Good | FREE (higher quota) | Most agents, testing |
| `gemini-2.0-flash` | ⚡⚡ Fast | Better | FREE (lower quota) | Balanced performance |
| `gemini-1.5-pro` | ⚡ Slower | Best | Paid | Complex analysis, detailed output |

**Rate Limits (Free Tier):**
- `gemini-1.5-flash`: 1500 requests/day
- `gemini-2.0-flash`: 200 requests/day
- `gemini-1.5-pro`: 50 requests/day

---

## Configuration Options

### Model Settings

```python
# Default model for all agents
DEFAULT_MODEL = "gemini-1.5-flash"

# Per-agent overrides
AGENT_MODELS = {
    "travel_advisory": "gemini-1.5-flash",
    "destination_intelligence": "gemini-1.5-flash",
    "immigration_specialist": "gemini-1.5-flash",
    "currency_exchange": "gemini-1.5-flash",
    "flight_booking": "gemini-1.5-flash",
    "hotel_booking": "gemini-1.5-flash",
    "car_rental": "gemini-1.5-flash",
    "activities": "gemini-1.5-flash",
    "itinerary": "gemini-1.5-flash",
    "document_generator": "gemini-1.5-flash",
    "budget_checkpoint": "gemini-1.5-flash",
    "suggestions_checkpoint": "gemini-1.5-flash",
}
```

### API Configuration

```python
# API Keys (from environment variables)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
```

### Feature Flags

```python
# Use Amadeus MCP for hotel bookings
USE_AMADEUS_API = True  # or "false" via env: USE_AMADEUS_API=false

# Amadeus environment: "test" or "production"
AMADEUS_ENV = "test"  # or "production" via env: AMADEUS_ENV=production
```

### Timeout Settings

```python
# API timeouts (in seconds)
WEATHER_API_TIMEOUT = 30   # OpenWeather API
AMADEUS_API_TIMEOUT = 15   # Amadeus hotel/flight search
CURRENCY_API_TIMEOUT = 10  # Exchange rate API
```

---

## How Agents Use Config

All agents now import and use the config:

```python
from config import Config

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            model=Config.get_model_for_agent("my_agent"),  # ← Uses config
            tools=[...]
        )
```

**How it works:**
1. `Config.get_model_for_agent("my_agent")` checks `AGENT_MODELS` dict
2. If `"my_agent"` has an override, uses that model
3. Otherwise, uses `DEFAULT_MODEL`

---

## Examples

### Example 1: Switch All Agents to Gemini 2.0 Flash

```bash
export ADK_DEFAULT_MODEL="gemini-2.0-flash"
cd adk-native
adk web agents_web --port 8080
```

### Example 2: Use Pro for Complex Agents, Flash for Others

Edit `config.py`:
```python
DEFAULT_MODEL = "gemini-1.5-flash"  # Default for most agents

AGENT_MODELS = {
    "travel_advisory": "gemini-1.5-pro",  # Complex safety analysis
    "itinerary": "gemini-1.5-pro",        # Detailed day-by-day planning
    # All other agents use gemini-1.5-flash
}
```

### Example 3: Switch Amadeus to Production

Edit `config.py`:
```python
AMADEUS_ENV = "production"  # Change from "test"
```

Or via environment variable:
```bash
export AMADEUS_ENV="production"
adk web agents_web --port 8080
```

### Example 4: Increase Timeouts for Slow Connections

Edit `config.py`:
```python
WEATHER_API_TIMEOUT = 60   # Increase from 30s
AMADEUS_API_TIMEOUT = 30   # Increase from 15s
```

---

## Checking Current Configuration

Run this command to see your current settings:

```bash
cd adk-native
python3 config.py
```

**Output:**
```
================================================================================
VACATION PLANNER CONFIGURATION
================================================================================

[MODEL SETTINGS]
  Default Model: gemini-1.5-flash
  Agent-specific overrides: 0

[API SETTINGS]
  Google API Key: ✓ Set
  OpenWeather API Key: ✓ Set
  Amadeus Client ID: ✓ Set
  Amadeus Client Secret: ✓ Set

[FEATURE FLAGS]
  Use Amadeus API: True
  Amadeus Environment: test
  Amadeus Base URL: https://test.api.amadeus.com

[TIMEOUTS]
  Weather API: 30s
  Amadeus API: 15s
  Currency API: 10s

[LOGGING]
  Log Level: INFO

================================================================================
```

---

## Troubleshooting

### Issue: Rate Limit Errors (429)

**Symptom:** `google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED`

**Solution:** Switch to a model with available quota:

```bash
# If gemini-2.0-flash is exhausted, try 1.5-flash
export ADK_DEFAULT_MODEL="gemini-1.5-flash"
```

Or edit `config.py`:
```python
DEFAULT_MODEL = "gemini-1.5-flash"
```

### Issue: Slow API Responses

**Symptom:** Agents timing out or hanging

**Solution:** Increase timeouts in `config.py`:

```python
WEATHER_API_TIMEOUT = 60   # Increase from 30s
AMADEUS_API_TIMEOUT = 30   # Increase from 15s
```

### Issue: Amadeus Not Returning Hotels

**Symptom:** Hotels showing LLM estimates instead of real data

**Solution:** Switch to production Amadeus API:

Edit `config.py`:
```python
AMADEUS_ENV = "production"
```

See [AMADEUS_MCP_STATUS.md](AMADEUS_MCP_STATUS.md) for details.

---

## Migration Notes

### Before (Hardcoded)
```python
# Old code in every agent file
model="gemini-1.5-flash"  # Had to edit 12 files to change model!
```

### After (Centralized)
```python
# New code in every agent file
model=Config.get_model_for_agent("agent_name")

# Change model in ONE place (config.py):
DEFAULT_MODEL = "gemini-2.0-flash"  # ← All agents now use this!
```

**Benefits:**
- ✅ Change model in one place
- ✅ Per-agent overrides possible
- ✅ Environment variable support
- ✅ Easy testing of different models
- ✅ No code changes needed

---

## Advanced: Dynamic Model Selection

You can even implement dynamic model selection based on conditions:

```python
# In config.py
import os
from datetime import datetime

class Config:
    @classmethod
    def get_model_for_agent(cls, agent_name: str) -> str:
        """Dynamic model selection based on time of day, load, etc."""

        # Example 1: Use Pro during business hours, Flash otherwise
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            return "gemini-1.5-pro"
        else:
            return "gemini-1.5-flash"

        # Example 2: Check remaining quota and switch models
        # (Implement quota checking logic here)

        # Example 3: A/B testing
        import random
        return random.choice(["gemini-1.5-flash", "gemini-2.0-flash"])
```

---

## Summary

### Quick Reference

| Task | Command |
|------|---------|
| Change default model | Edit `config.py`: `DEFAULT_MODEL = "..."` |
| Override via env var | `export ADK_DEFAULT_MODEL="gemini-2.0-flash"` |
| Per-agent override | Edit `AGENT_MODELS` dict in `config.py` |
| Check current config | `python3 config.py` |
| Switch Amadeus env | Edit `config.py`: `AMADEUS_ENV = "production"` |
| Increase timeouts | Edit timeout values in `config.py` |

### Files Modified

- ✅ `config.py` - Centralized configuration
- ✅ All 12 agent files - Now use `Config.get_model_for_agent()`
- ✅ `update_agents_config.py` - Migration script (for future updates)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-22
**Status:** ✅ All agents using centralized config
