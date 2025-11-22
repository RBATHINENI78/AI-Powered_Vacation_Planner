"""
Itinerary Tools - Daily schedule generation and trip planning
"""

from typing import Dict, Any, List


def generate_daily_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    interests: List[str] = None,
    pace: str = "moderate",
    travelers: int = 2
) -> Dict[str, Any]:
    """
    Generate a day-by-day itinerary using LLM knowledge.

    Args:
        destination: Destination city/country
        start_date: Trip start date (YYYY-MM-DD)
        end_date: Trip end date (YYYY-MM-DD)
        interests: List of interests (culture, food, adventure, etc.)
        pace: Travel pace (relaxed/moderate/packed)
        travelers: Number of travelers

    Returns:
        Daily itinerary via LLM instruction
    """
    interests_str = ", ".join(interests) if interests else "general sightseeing"

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "interests": interests_str,
        "pace": pace,
        "travelers": travelers,
        "llm_instruction": f"""Create a detailed day-by-day itinerary for {destination} from {start_date} to {end_date} for {travelers} travelers.

**Trip Parameters:**
- Interests: {interests_str}
- Pace: {pace} (adjust daily activities accordingly)
- Travelers: {travelers} people

**Itinerary Format for Each Day:**

**Day X: [Date] - [Theme]**

**Morning (8:00 AM - 12:00 PM):**
- Activity 1
  * Location and address
  * Duration
  * Cost estimate
  * Why visit / highlights
  * Booking requirements

**Lunch (12:00 PM - 1:30 PM):**
- Restaurant recommendation
  * Cuisine type
  * Price range
  * Must-try dishes

**Afternoon (1:30 PM - 6:00 PM):**
- Activity 2
  * Details as above
- Optional: Activity 3 (if {pace} pace allows)

**Dinner (7:00 PM - 9:00 PM):**
- Restaurant recommendation
  * Different from lunch area
  * Atmospheric/special

**Evening (9:00 PM onwards):**
- Optional activity
  * Cultural show, night walk, relaxation

**Logistics:**
- Transportation for the day
- Walking distance vs taxi/metro
- Rest breaks (if pace = relaxed)

**Tips for Day X:**
- Insider tips
- Things to avoid
- Best photo spots

---

**Itinerary Guidelines:**
1. **Logical Flow:** Group nearby attractions together
2. **Timing:** Account for opening hours and travel time
3. **Variety:** Mix of activities based on interests
4. **Rest:** Include downtime for {pace} pace
5. **Weather:** Consider typical weather for time of year
6. **Crowds:** Recommend best times to visit popular spots
7. **Flexibility:** Mark optional activities
8. **Local Experience:** Include authentic local experiences

**Summary Section:**
- Total estimated costs (activities + meals)
- Recommended dress code
- Weather preparedness
- Emergency contacts

Create a {pace}-paced itinerary that balances {interests_str} interests."""
    }


def optimize_route(destination: str, attractions: List[str]) -> Dict[str, Any]:
    """
    Optimize route between multiple attractions.

    Args:
        destination: Destination city
        attractions: List of attraction names

    Returns:
        Optimized route via LLM instruction
    """
    return {
        "destination": destination,
        "attractions": attractions,
        "llm_instruction": f"""Optimize the visiting order for these attractions in {destination}: {', '.join(attractions)}.

**Route Optimization:**

**Attractions to Visit:**
{chr(10).join([f"{i+1}. {attr}" for i, attr in enumerate(attractions)])}

**Analysis:**
1. **Geographical Clustering:**
   - Group nearby attractions
   - Identify distinct areas/neighborhoods

2. **Optimal Order:**
   - Recommended sequence (1 → 2 → 3...)
   - Rationale for each transition
   - Walking time between stops
   - Alternative transport if needed

3. **Time Allocation:**
   - Suggested time at each attraction
   - Total time for entire route
   - Best starting time

4. **Transportation:**
   - Walk vs public transport vs taxi
   - Metro/bus routes if applicable
   - Approximate costs

5. **Efficiency Tips:**
   - Skip-the-line tickets needed?
   - Best entrance to use
   - Lunch/break suggestions along route

Provide the most efficient order to visit all attractions in one day."""
    }


def create_packing_list(
    destination: str,
    start_date: str,
    end_date: str,
    activities: List[str] = None,
    weather_conditions: str = ""
) -> Dict[str, Any]:
    """
    Create comprehensive packing list.

    Args:
        destination: Destination city/country
        start_date: Trip start date
        end_date: Trip end date
        activities: Planned activities
        weather_conditions: Expected weather description

    Returns:
        Packing list via LLM instruction
    """
    activities_str = ", ".join(activities) if activities else "general tourism"

    return {
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "activities": activities_str,
        "weather_conditions": weather_conditions,
        "llm_instruction": f"""Create a comprehensive packing list for a trip to {destination} from {start_date} to {end_date}.

**Trip Details:**
- Destination: {destination}
- Weather: {weather_conditions}
- Activities: {activities_str}
- Duration: Calculate nights from dates

**Packing List:**

**1. Travel Documents:**
- Passport (validity check)
- Visa (if required)
- Travel insurance documents
- Flight/hotel confirmations
- Emergency contacts
- Photocopies of important documents

**2. Clothing:**
Based on {weather_conditions} and {activities_str}:
- Tops (quantity based on nights)
- Bottoms
- Underwear and socks
- Shoes (walking, formal if needed, activity-specific)
- Outerwear (jacket, raincoat)
- Accessories (hat, sunglasses, scarf)
- Sleepwear
- Swimwear (if applicable)

**3. Toiletries:**
- Basics (toothbrush, toothpaste, shampoo, soap)
- Medications and prescriptions
- First aid kit basics
- Sunscreen (SPF 30+)
- Insect repellent (if needed for {destination})
- Personal hygiene items
- Contact lenses/glasses

**4. Electronics:**
- Phone and charger
- Power adapter for {destination} (specify plug type)
- Portable power bank
- Camera and memory cards
- Headphones
- Laptop/tablet (if needed)

**5. Money & Cards:**
- Credit/debit cards (notify bank of travel)
- Cash (local currency recommendations)
- Money belt/hidden wallet
- Copy of credit cards (stored separately)

**6. Activity-Specific Items:**
Based on {activities_str}:
- Hiking boots (if hiking)
- Snorkeling gear (if beach)
- Formal wear (if fancy dining)
- Specific equipment

**7. Comfort Items:**
- Neck pillow (for flight)
- Eye mask and ear plugs
- Reusable water bottle
- Snacks for travel
- Entertainment (book, kindle)

**8. Destination-Specific for {destination}:**
- Cultural dress requirements
- Seasons-specific items
- Local customs considerations

**Packing Tips:**
- Weight limits for flights
- Roll vs fold clothes
- Packing cubes recommendations
- Leave space for souvenirs

**What NOT to Pack:**
- Prohibited items for {destination}
- Items you can buy there"""
    }
