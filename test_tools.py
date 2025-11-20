"""
Test script for all vacation planner tools
Testing: Charlotte, USA → Hyderabad, India
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the agent module
from agents.vacation_planner import agent

print("="*80)
print("Testing Vacation Planner Tools")
print("Query: Charlotte, USA → Hyderabad, India")
print("Dates: Dec 15-25, 2025 | 2 adults | Indian citizenship | Budget: $5000")
print("="*80)

print("\n1. Testing Weather Tool...")
print("-"*80)
weather = agent.get_weather_info(city='Hyderabad', country='India')
print(weather)

print("\n2. Testing Visa Requirements...")
print("-"*80)
visa = agent.check_visa_requirements(citizenship='India', destination='India', duration_days=10)
print(visa)

print("\n3. Testing Currency Exchange...")
print("-"*80)
currency = agent.get_currency_exchange(origin='USA', destination='India', amount=5000)
print(currency)

print("\n4. Testing Flight Search...")
print("-"*80)
flights = agent.search_flights(
    origin='Charlotte, USA',
    destination='Hyderabad, India',
    departure_date='2025-12-15',
    return_date='2025-12-25',
    travelers=2
)
print(flights)

print("\n5. Testing Hotel Search...")
print("-"*80)
hotels = agent.search_hotels(
    destination='Hyderabad',
    check_in='2025-12-15',
    check_out='2025-12-25',
    guests=2,
    rooms=1
)
print(hotels)

print("\n6. Testing Itinerary Generation...")
print("-"*80)
itinerary = agent.generate_detailed_itinerary(
    destination='Hyderabad',
    start_date='2025-12-15',
    end_date='2025-12-25',
    interests='Recreation, party life, architecture, historical',
    travelers=2
)
print(itinerary)

print("\n7. Testing Trip Document Generation...")
print("-"*80)
trip_doc = agent.generate_trip_document(
    destination='Hyderabad',
    start_date='2025-12-15',
    end_date='2025-12-25',
    travelers=2,
    origin='Charlotte, USA',
    interests='Recreation, party life, architecture, historical',
    budget=5000
)
print(trip_doc)

print("\n" + "="*80)
print("All tools tested successfully!")
print("="*80)
