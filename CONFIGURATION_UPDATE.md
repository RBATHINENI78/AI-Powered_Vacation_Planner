# Configuration System Update

**Date:** 2025-11-22
**Status:** ✅ **COMPLETED**

---

## What Changed

The vacation planner now has **centralized configuration** for all settings. You no longer need to edit individual agent files to change models or settings.

---

## Quick Examples

### Change Model for All Agents

**Before (edit 12 files):**
```python
# Had to edit every agent file:
# adk_agents/destination.py
model="gemini-1.5-flash"  # Edit this line

# adk_agents/currency.py
model="gemini-1.5-flash"  # Edit this line

# ... 10 more files
```

**After (edit 1 file OR use env var):**

**Option 1: Environment Variable** (No code changes!)
```bash
export ADK_DEFAULT_MODEL="gemini-2.0-flash"
adk web agents_web --port 8080
```

**Option 2: Edit config.py** (One line change)
```python
# config.py
DEFAULT_MODEL = "gemini-2.0-flash"  # ← Change this line
```

**Done!** All 12 agents now use `gemini-2.0-flash`.

---

### Use Different Models for Different Agents

Edit `config.py`:
```python
DEFAULT_MODEL = "gemini-1.5-flash"  # Default for most agents

AGENT_MODELS = {
    "travel_advisory": "gemini-1.5-pro",  # Use Pro for complex analysis
    "itinerary": "gemini-1.5-pro",        # Use Pro for detailed planning
    # All other agents use gemini-1.5-flash
}
```

---

### Switch Amadeus to Production

Edit `config.py`:
```python
AMADEUS_ENV = "production"  # Change from "test"
```

This gives you real hotel data for ALL cities (not just test cities).

---

## Files Created

1. **[config.py](config.py)** - Centralized configuration
   - Model settings
   - API keys
   - Feature flags
   - Timeouts

2. **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Complete documentation
   - How to change models
   - Environment variables
   - Per-agent overrides
   - Troubleshooting

3. **[update_agents_config.py](update_agents_config.py)** - Migration script
   - Automated the update of all 12 agent files
   - Can be used for future config changes

---

## Files Modified

All 12 agent files now import and use config:

```python
from config import Config

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            name="my_agent",
            model=Config.get_model_for_agent("my_agent"),  # ← Uses config!
            tools=[...]
        )
```

**Updated agents:**
- ✅ travel_advisory.py
- ✅ destination.py
- ✅ immigration.py
- ✅ currency.py
- ✅ booking.py (3 agents: flight, hotel, car)
- ✅ activities.py
- ✅ itinerary.py
- ✅ documents.py
- ✅ budget_checkpoint.py
- ✅ suggestions_checkpoint.py

**Total:** 12 agents across 10 files

---

## How to Use

### Check Current Configuration
```bash
cd adk-native
python3 config.py
```

### Change Model via Environment Variable
```bash
export ADK_DEFAULT_MODEL="gemini-2.0-flash"
cd adk-native
adk web agents_web --port 8080
```

### Change Model in config.py
```python
# Edit config.py
DEFAULT_MODEL = "gemini-1.5-pro"  # Change this line
```

Then restart:
```bash
pkill -f "adk web"
adk web agents_web --port 8080
```

---

## Benefits

### Before
- ❌ Had to edit 12 agent files to change model
- ❌ No way to test different models easily
- ❌ Hardcoded settings scattered across codebase
- ❌ No environment variable support

### After
- ✅ Change model in ONE place (`config.py`)
- ✅ Or use environment variable (no code changes!)
- ✅ Per-agent model overrides possible
- ✅ All settings centralized
- ✅ Easy testing of different configurations
- ✅ Configuration visible at startup

---

## Current Configuration

Run `python3 config.py` to see:

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

## Testing

### Test 1: Verify All Agents Load
```bash
cd adk-native
python3 -c "
from adk_agents import *
from config import Config
print('✅ All agents imported successfully')
print(f'Default model: {Config.DEFAULT_MODEL}')
"
```

**Expected output:**
```
✅ All agents imported successfully
Default model: gemini-1.5-flash
```

### Test 2: Check Config Values
```bash
cd adk-native
python3 config.py
```

### Test 3: Verify Server Starts
```bash
adk web agents_web --port 8080
```

Server should start without errors and use configured model.

---

## Server Status

- ✅ Server running on port 8080
- ✅ Process ID: 82488
- ✅ All agents using centralized config
- ✅ Current model: `gemini-1.5-flash`

---

## Next Steps

1. **Try different models:**
   ```bash
   # Test gemini-2.0-flash
   export ADK_DEFAULT_MODEL="gemini-2.0-flash"
   ```

2. **Use Pro for specific agents:**
   ```python
   # In config.py
   AGENT_MODELS = {
       "itinerary": "gemini-1.5-pro",  # Detailed planning
   }
   ```

3. **Switch Amadeus to production:**
   ```python
   # In config.py
   AMADEUS_ENV = "production"  # Real hotel data
   ```

---

## Troubleshooting

### Rate Limit Error (429)

**Error:** `google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED`

**Solution:**
```bash
# Switch to model with available quota
export ADK_DEFAULT_MODEL="gemini-1.5-flash"
```

See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for more troubleshooting tips.

---

## Documentation

- **[config.py](config.py)** - Configuration file (edit this)
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Complete usage guide
- **[SESSION_UPDATES_SUMMARY.md](SESSION_UPDATES_SUMMARY.md)** - Previous updates

---

**Document Version:** 1.0
**Last Updated:** 2025-11-22
**Status:** ✅ Configuration system active and tested
