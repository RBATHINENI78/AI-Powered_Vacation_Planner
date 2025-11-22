# Climate Data API Integration - Implementation Plan

**Feature**: Replace Hardcoded "Best Time to Visit" Data with API Integration
**Branch**: `feature/climate-data-api-integration`
**Status**: Planning
**Priority**: Medium
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-21

---

## Problem Statement

### Current Implementation
The `_get_best_time()` method in [src/agents/destination_intelligence.py:259-270](../../src/agents/destination_intelligence.py#L259-L270) uses hardcoded data:

```python
def _get_best_time(self, city: str, country: str) -> str:
    """Get best time to visit destination."""
    # Simplified recommendations (would use historical data in production)
    best_times = {
        "France": "April to June or September to November",
        "Japan": "March to May or September to November",
        "Italy": "April to June or September to October",
        "UK": "May to September",
        "Thailand": "November to February",
        "Australia": "September to November or March to May"
    }
    return best_times.get(country, "Year-round with seasonal variations")
```

### Issues
1. **Limited Coverage**: Only 6 countries hardcoded (out of 195+ countries)
2. **No City-Level Granularity**: Paris vs Nice have different optimal times
3. **Stale Data**: No updates for climate changes or emerging travel trends
4. **Not Scalable**: Manual data entry doesn't scale
5. **Missing Context**: No consideration for user preferences (budget season, festivals, crowd levels)

---

## Proposed Solution

### Approach: Multi-Layer Architecture with Graceful Fallbacks

**Layer 1**: SQLite Cache (6-month validity)
**Layer 2**: OpenWeather Climate API (existing API key)
**Layer 3**: Gemini LLM Analysis (existing integration)
**Layer 4**: Hardcoded Data (current fallback)

### Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│  _get_best_time(city, country)                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  1. Check SQLite DB │
         │  (6-month cache)    │
         └──────────┬──────────┘
                    │
            ┌───────┴────────┐
            │   Cache Hit?   │
            └───────┬────────┘
                    │
         ┌──────────┴──────────┐
         │ YES                 │ NO
         ▼                     ▼
    ┌─────────┐      ┌──────────────────────┐
    │ Return  │      │ 2. OpenWeather       │
    │ Cached  │      │    Climate API       │
    │ Data    │      │    (30-year history) │
    └─────────┘      └──────────┬───────────┘
                                 │
                         ┌───────┴────────┐
                         │   API Success? │
                         └───────┬────────┘
                                 │
                      ┌──────────┴──────────┐
                      │ YES                 │ NO
                      ▼                     ▼
            ┌──────────────────┐    ┌───────────────┐
            │ 3. Store in DB   │    │ 3. Gemini LLM │
            │ 4. Return Data   │    │    Analysis   │
            └──────────────────┘    └───────┬───────┘
                                            │
                                    ┌───────┴────────┐
                                    │   LLM Success? │
                                    └───────┬────────┘
                                            │
                                 ┌──────────┴──────────┐
                                 │ YES                 │ NO
                                 ▼                     ▼
                       ┌─────────────────┐   ┌───────────────┐
                       │ Return LLM Data │   │ 4. Hardcoded  │
                       └─────────────────┘   │    Fallback   │
                                             └───────────────┘
```

---

## Implementation Plan

### Phase 1: Database Layer (30 min)

#### 1.1 Create SQLite Schema
**File**: `src/database/climate_cache.py` (NEW)

```python
"""
Climate Data Cache - SQLite database for caching climate recommendations
"""
import sqlite3
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger


class ClimateCache:
    """SQLite cache for climate data with 6-month expiry."""

    DB_PATH = Path(__file__).parent.parent.parent / "data" / "climate_cache.db"
    CACHE_VALIDITY_MONTHS = 6

    def __init__(self):
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database with schema."""
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS climate_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    best_months TEXT NOT NULL,
                    peak_season TEXT,
                    off_season TEXT,
                    avg_temp_by_month TEXT,  -- JSON string
                    rainfall_by_month TEXT,  -- JSON string
                    source TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, country)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_location
                ON climate_data(city, country)
            """)

    async def get(self, city: str, country: str) -> Optional[Dict[str, Any]]:
        """Get cached climate data if valid."""
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM climate_data
                WHERE city = ? AND country = ?
            """, (city, country))

            row = cursor.fetchone()
            if not row:
                return None

            # Check if cache is still valid (6 months)
            last_updated = datetime.fromisoformat(row["last_updated"])
            expiry = timedelta(days=30 * self.CACHE_VALIDITY_MONTHS)

            if datetime.now() - last_updated > expiry:
                logger.info(f"[CACHE] Expired data for {city}, {country}")
                return None

            logger.info(f"[CACHE] Hit for {city}, {country}")
            return dict(row)

    async def set(self, city: str, country: str, data: Dict[str, Any]):
        """Store climate data in cache."""
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO climate_data
                (city, country, best_months, peak_season, off_season,
                 avg_temp_by_month, rainfall_by_month, source, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                city, country,
                data.get("best_months", ""),
                data.get("peak_season", ""),
                data.get("off_season", ""),
                data.get("avg_temp_by_month", "{}"),
                data.get("rainfall_by_month", "{}"),
                data.get("source", "api")
            ))
        logger.info(f"[CACHE] Stored data for {city}, {country}")
```

---

### Phase 2: OpenWeather Climate API Integration (45 min)

#### 2.1 Update DestinationIntelligenceAgent
**File**: `src/agents/destination_intelligence.py`

**Changes**:
```python
from src.database.climate_cache import ClimateCache

class DestinationIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(...)
        self.climate_cache = ClimateCache()  # NEW

    async def _get_best_time(self, city: str, country: str) -> str:
        """Get best time to visit with API + caching."""
        # Layer 1: Check cache
        cached = await self.climate_cache.get(city, country)
        if cached:
            return cached["best_months"]

        # Layer 2: OpenWeather Climate API
        try:
            api_data = await self._fetch_climate_from_api(city, country)
            if api_data:
                await self.climate_cache.set(city, country, api_data)
                return api_data["best_months"]
        except Exception as e:
            logger.warning(f"Climate API failed: {e}")

        # Layer 3: Gemini LLM Analysis
        try:
            llm_data = await self._analyze_climate_with_llm(city, country)
            if llm_data:
                return llm_data["best_months"]
        except Exception as e:
            logger.warning(f"LLM analysis failed: {e}")

        # Layer 4: Hardcoded fallback
        return self._get_fallback_best_time(country)

    async def _fetch_climate_from_api(
        self,
        city: str,
        country: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch climate data from OpenWeather Climate API."""
        try:
            # OpenWeather Historical API endpoint
            url = f"{self.base_url}/climatology/v1/monthly"
            params = {
                "q": f"{city},{country}",
                "appid": self.api_key
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return self._analyze_climate_data(data)
                else:
                    logger.error(f"Climate API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Climate API fetch error: {e}")
            return None

    def _analyze_climate_data(self, data: Dict) -> Dict[str, Any]:
        """Analyze 12 months of climate data to find best time."""
        # Analyze temperature, rainfall, and conditions
        # Return best months based on:
        # - Comfortable temperatures (15-28°C)
        # - Low rainfall (<50mm/month)
        # - Good weather conditions

        monthly_scores = []
        for month_data in data.get("monthly", []):
            score = self._calculate_month_score(month_data)
            monthly_scores.append((month_data["month"], score))

        # Find top 3-4 consecutive months
        best_months = self._find_best_consecutive_months(monthly_scores)

        return {
            "best_months": best_months,
            "source": "openweather_api",
            "avg_temp_by_month": {...},
            "rainfall_by_month": {...}
        }

    async def _analyze_climate_with_llm(
        self,
        city: str,
        country: str
    ) -> Optional[Dict[str, Any]]:
        """Use Gemini to analyze best time to visit."""
        prompt = f"""Analyze the best time to visit {city}, {country}.

        Provide:
        1. Best months to visit (e.g., "April to June or September to November")
        2. Peak tourist season
        3. Off-season months

        Consider: weather, festivals, crowds, prices

        Return JSON format:
        {{
          "best_months": "April to June or September to November",
          "peak_season": "July to August",
          "off_season": "November to March"
        }}
        """

        # Use existing Gemini integration to analyze
        # (Implementation depends on how Gemini is currently used)
        # Return parsed JSON response
        pass

    def _get_fallback_best_time(self, country: str) -> str:
        """Hardcoded fallback data (current implementation)."""
        best_times = {
            "France": "April to June or September to November",
            "Japan": "March to May or September to November",
            "Italy": "April to June or September to October",
            "UK": "May to September",
            "Thailand": "November to February",
            "Australia": "September to November or March to May"
        }
        return best_times.get(country, "Year-round with seasonal variations")
```

---

### Phase 3: Testing & Validation (45 min)

#### 3.1 Unit Tests
**File**: `tests/test_climate_cache.py` (NEW)

```python
import pytest
from src.database.climate_cache import ClimateCache


@pytest.mark.asyncio
async def test_cache_set_and_get():
    cache = ClimateCache()

    data = {
        "best_months": "April to June",
        "source": "test"
    }

    await cache.set("Paris", "France", data)
    result = await cache.get("Paris", "France")

    assert result is not None
    assert result["best_months"] == "April to June"


@pytest.mark.asyncio
async def test_cache_expiry():
    # Test 6-month expiry logic
    pass


@pytest.mark.asyncio
async def test_cache_miss():
    cache = ClimateCache()
    result = await cache.get("NonExistentCity", "NonExistentCountry")
    assert result is None
```

#### 3.2 Integration Tests
**File**: `tests/test_destination_intelligence_climate.py` (NEW)

```python
@pytest.mark.asyncio
async def test_climate_api_integration():
    agent = DestinationIntelligenceAgent()

    # Test Layer 1: Cache
    result1 = await agent._get_best_time("Paris", "France")

    # Test Layer 2: API
    result2 = await agent._get_best_time("NewYork", "USA")

    # Test Layer 4: Fallback
    result3 = await agent._get_best_time("UnknownCity", "UnknownCountry")

    assert all([result1, result2, result3])
```

---

## Dependencies

### Python Packages (Already Installed)
- `httpx>=0.25.0` - Already in requirements.txt ✓
- `sqlite3` - Python standard library ✓

### API Keys (Already Available)
- `OPENWEATHER_API_KEY` - Already configured ✓

### New Dependencies
None required!

---

## Rollout Plan

### Phase 1: Development (This Branch)
1. Create database layer
2. Integrate OpenWeather Climate API
3. Add LLM fallback
4. Write tests

### Phase 2: Testing
1. Test with 10+ destinations
2. Verify cache invalidation
3. Test API failure scenarios
4. Validate LLM fallback quality

### Phase 3: Merge & Deploy
1. Code review
2. Merge to `main`
3. Monitor API usage
4. Track cache hit rates

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Coverage** | 195+ countries | Cache size after 1 month |
| **Cache Hit Rate** | >80% | Logs analysis |
| **API Latency** | <500ms | Response time tracking |
| **Fallback Rate** | <10% | Error rate monitoring |
| **Data Freshness** | 6-month rolling | Cache expiry checks |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenWeather API limits | Medium | Use 6-month cache + LLM fallback |
| API changes endpoint | Low | Maintain hardcoded fallback |
| SQLite concurrency | Low | Use connection pooling |
| Increased latency | Medium | Async operations + caching |

---

## Future Enhancements

1. **User Preferences**: Filter by budget season, festivals, crowd levels
2. **Amadeus Integration**: Use existing Amadeus API for travel recommendations
3. **Real-time Updates**: Subscribe to climate alerts
4. **ML Model**: Train on user feedback to improve recommendations
5. **Regional Granularity**: City-district level recommendations (e.g., Paris vs Marseille)

---

## References

- [OpenWeather Climate API Documentation](https://openweathermap.org/api/climatology)
- [Current Implementation](../../src/agents/destination_intelligence.py#L259-L270)
- [SQLite Python Documentation](https://docs.python.org/3/library/sqlite3.html)

---

## Checklist

- [ ] Create `src/database/` directory
- [ ] Implement `ClimateCache` class
- [ ] Update `DestinationIntelligenceAgent`
- [ ] Add `_fetch_climate_from_api` method
- [ ] Add `_analyze_climate_data` method
- [ ] Add `_analyze_climate_with_llm` method
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test with 10+ destinations
- [ ] Document API usage patterns
- [ ] Update ADK_FEATURES_IMPLEMENTED.md
- [ ] Create pull request
- [ ] Code review
- [ ] Merge to main

---

**Status**: Ready for implementation
**Next Step**: Create database layer (`src/database/climate_cache.py`)
