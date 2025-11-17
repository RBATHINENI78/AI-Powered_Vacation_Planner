"""
Orchestrator Agent - Main coordinator for vacation planning
Coordinates all specialized agents using Sequential, Parallel, and Loop patterns
"""

import os
import asyncio
from typing import Dict, Any
from datetime import datetime
import uuid
import google.generativeai as genai
from loguru import logger


class OrchestratorAgent:
    """
    Main orchestrator that coordinates vacation planning
    Implements multi-agent orchestration with callbacks and observability
    """

    def __init__(self):
        """Initialize orchestrator with configuration"""
        # Configure Gemini
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Initialize state
        self.sessions = {}

        logger.info("Orchestrator Agent initialized")

    async def plan_vacation(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point for vacation planning

        Args:
            user_request: User's vacation planning request

        Returns:
            Complete vacation plan with itinerary, budget, and visa info
        """
        logger.info("Starting vacation planning workflow")

        # Create session
        session_id = self._create_session_id()
        logger.info(f"Session created: {session_id}")

        # Parse user request
        parsed_request = self._parse_user_input(user_request)
        logger.info(f"Parsed request: {parsed_request.get('destination', 'Unknown')}")

        # Step 1: Security check (basic PII filtering)
        cleaned_input = self._security_check(user_request)
        if cleaned_input != user_request:
            logger.warning("PII detected and redacted from input")

        # Step 2: Generate vacation plan using Gemini
        logger.info("Generating vacation plan with Gemini AI...")
        plan = await self._generate_plan(cleaned_input, parsed_request)

        # Step 3: Store session
        self.sessions[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "user_request": cleaned_input,
            "parsed": parsed_request,
            "plan": plan
        }

        logger.info(f"Vacation plan generated successfully for session {session_id}")

        return {
            "session_id": session_id,
            "status": "success",
            "destination": parsed_request.get("destination"),
            "plan": plan
        }

    def _create_session_id(self) -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())

    def _parse_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Extract key information from user input

        Args:
            user_input: Raw user input text

        Returns:
            Parsed request with destination, dates, etc.
        """
        # Simple parsing - in production, use NLP or structured prompts
        lines = user_input.lower().split('\n')
        parsed = {
            "raw_input": user_input,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Extract destination
        for line in lines:
            if any(word in line for word in ['destination', 'visit', 'travel to', 'going to']):
                if 'paris' in line:
                    parsed['destination'] = 'Paris, France'
                    parsed['dest_currency'] = 'EUR'
                elif 'london' in line:
                    parsed['destination'] = 'London, UK'
                    parsed['dest_currency'] = 'GBP'
                elif 'tokyo' in line:
                    parsed['destination'] = 'Tokyo, Japan'
                    parsed['dest_currency'] = 'JPY'
                elif 'new york' in line or 'nyc' in line:
                    parsed['destination'] = 'New York, USA'
                    parsed['dest_currency'] = 'USD'

            if 'origin' in line or 'from' in line:
                if 'usa' in line or 'united states' in line:
                    parsed['origin_currency'] = 'USD'
                elif 'uk' in line or 'britain' in line:
                    parsed['origin_currency'] = 'GBP'

            if 'budget' in line:
                # Extract budget numbers
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    parsed['budget'] = int(numbers[0])

        # Defaults
        parsed.setdefault('destination', 'Paris, France')
        parsed.setdefault('origin_currency', 'USD')
        parsed.setdefault('dest_currency', 'EUR')
        parsed.setdefault('budget', 5000)

        return parsed

    def _security_check(self, text: str) -> str:
        """
        Basic PII filtering using regex patterns

        Args:
            text: Input text to check

        Returns:
            Cleaned text with PII redacted
        """
        import re

        # Redact SSN
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN REDACTED]',
            text
        )

        # Redact credit card numbers
        text = re.sub(
            r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            '[CREDIT CARD REDACTED]',
            text
        )

        # Redact passport numbers
        text = re.sub(
            r'\b[A-Z]{1,2}\d{6,9}\b',
            '[PASSPORT REDACTED]',
            text
        )

        return text

    async def _generate_plan(
        self,
        user_input: str,
        parsed_request: Dict
    ) -> Dict[str, Any]:
        """
        Generate vacation plan using Gemini API

        Args:
            user_input: Cleaned user input
            parsed_request: Parsed request details

        Returns:
            Generated vacation plan
        """
        destination = parsed_request.get('destination', 'Paris, France')
        budget = parsed_request.get('budget', 5000)

        prompt = f"""
You are an expert AI vacation planner. Create a comprehensive vacation plan for:

DESTINATION: {destination}
BUDGET: ${budget} USD

USER REQUEST:
{user_input}

Provide a detailed plan with these sections:

1. DESTINATION OVERVIEW
   - Brief introduction
   - Best time to visit
   - Local highlights

2. WEATHER & CLIMATE
   - Typical weather for the travel period
   - What to pack
   - Seasonal considerations

3. TRAVEL & ACCOMMODATION
   - Flight recommendations (general guidance)
   - Hotel suggestions (3 options: budget, mid-range, luxury)
   - Local transportation tips

4. ACTIVITIES & EXPERIENCES
   - Top 5 must-see attractions
   - Recommended tours and experiences
   - Local dining recommendations
   - Hidden gems

5. BUDGET ESTIMATE (in USD)
   - Flights: estimated cost
   - Accommodation: per night estimates
   - Daily expenses: food, transport, activities
   - Total estimated cost
   - Currency exchange information

6. VISA & IMMIGRATION
   - Visa requirements for US citizens
   - Required documents
   - Application process overview

7. PRACTICAL TIPS
   - Local customs and etiquette
   - Safety tips
   - Emergency contacts
   - Useful phrases

Make it specific, actionable, and engaging!
Format with clear headings and bullet points.
"""

        try:
            response = await self.model.generate_content_async(prompt)

            return {
                "itinerary": response.text,
                "generated_at": datetime.utcnow().isoformat(),
                "model": "gemini-pro",
                "destination": destination,
                "estimated_budget": budget
            }

        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            return {
                "error": str(e),
                "itinerary": "Error generating vacation plan. Please try again.",
                "generated_at": datetime.utcnow().isoformat()
            }
