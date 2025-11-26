# Rate Limit Handling

## Issue

The Gemini API free tier has strict rate limits:
- **15 requests per minute** for `gemini-2.5-flash-lite`
- Each agent in the workflow makes LLM calls
- Running the full vacation planner workflow (9+ agents) can exceed this limit

## Error Message

```
429 RESOURCE_EXHAUSTED
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
limit: 15, model: gemini-2.5-flash-lite
Please retry in 26s
```

## Temporary Solution (Free Tier)

**Wait 30 seconds between queries** to allow the quota to reset.

The rate limit window is 60 seconds, so waiting 30 seconds before retrying is sufficient.

## Configuration

Rate limit settings are now in [config.py](config.py):

```python
# ==================== RATE LIMIT SETTINGS ====================

# Retry configuration for rate limits (free tier: 15 RPM)
ENABLE_RATE_LIMIT_RETRY = os.getenv("ENABLE_RATE_LIMIT_RETRY", "true").lower() == "true"
RATE_LIMIT_RETRY_DELAY = int(os.getenv("RATE_LIMIT_RETRY_DELAY", "30"))  # seconds
RATE_LIMIT_MAX_RETRIES = int(os.getenv("RATE_LIMIT_MAX_RETRIES", "3"))
```

**Note:** These settings are documented but not yet implemented in the retry logic. The ADK library has built-in retry support, but it uses shorter delays (not suitable for rate limits).

## Future Solutions

### 1. Upgrade to Paid Tier (Recommended)

Upgrade your Google AI API to a paid tier:
- **1500 requests per minute** (100x more)
- **4 million requests per day**
- Cost: Pay-as-you-go pricing

**How to upgrade:**
1. Visit https://ai.google.dev/pricing
2. Enable billing on your Google Cloud project
3. No code changes required

### 2. Use Vertex AI (Enterprise)

Switch to Vertex AI for higher quotas:
- Set environment variables:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  export GOOGLE_CLOUD_PROJECT=your-project-id
  export GOOGLE_CLOUD_LOCATION=us-central1
  ```
- Modify [config.py](config.py) to enable Vertex AI
- Higher quotas and better SLAs

### 3. Implement Custom Retry Logic

Add application-level retry with exponential backoff:
```python
import time
from google.adk.models.google_llm import _ResourceExhaustedError

def retry_with_backoff(func, max_retries=3, delay=30):
    for attempt in range(max_retries):
        try:
            return func()
        except _ResourceExhaustedError as e:
            if attempt < max_retries - 1:
                print(f"Rate limit hit. Waiting {delay}s before retry {attempt + 1}/{max_retries}...")
                time.sleep(delay)
            else:
                raise
```

### 4. Reduce Agent Count (Development Only)

For testing, simplify the workflow:
- Remove optional agents (e.g., currency exchange)
- Combine agents (e.g., merge booking agents)
- Use cached responses

## Current Status

- ✅ Rate limit settings added to config.py
- ✅ Documentation created
- ⏳ Custom retry logic NOT YET implemented (waiting for user decision on paid tier)
- 📝 Temporary workaround: Wait 30 seconds between queries

## Monitoring Usage

Check your current API usage:
- Visit: https://ai.dev/usage?tab=rate-limit
- Monitor requests per minute
- See when quota resets

---

**Generated:** 2025-11-25
**Status:** Documented (awaiting paid tier decision)
