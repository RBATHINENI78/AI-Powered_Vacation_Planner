"""
Orchestrator Agent - Main coordinator for all phases
Integrates Security, Research, Booking, and Optimization phases
"""

import uuid
import time
import re
from datetime import datetime
from typing import Dict, Any
from loguru import logger

from .base_agent import BaseAgent
from .security_guardian import SecurityGuardianAgent
from .sequential_agent import SequentialResearchAgent
from .parallel_agent import ParallelBookingAgent
from .loop_agent import LoopBudgetOptimizer


class OrchestratorAgent(BaseAgent):
    """
    Main Orchestrator Agent that coordinates all vacation planning phases:
    1. Security Phase - PII detection
    2. Research Phase - Sequential agent (Destination -> Immigration -> Financial)
    3. Booking Phase - Parallel agent (Flights, Hotels, Car, Activities)
    4. Optimization Phase - Loop agent (Budget optimization with HITL)
    """

    def __init__(self):
        super().__init__(
            name="orchestrator",
            description="Main coordinator for vacation planning workflow"
        )

        # Initialize phase agents
        self.security_agent = SecurityGuardianAgent()
        self.research_agent = SequentialResearchAgent()
        self.booking_agent = ParallelBookingAgent()
        self.optimizer_agent = LoopBudgetOptimizer()

        # Register A2A message handlers
        self.register_message_handler("security_alert", self._handle_security_alert)
        self.register_message_handler("budget_update", self._handle_budget_update)

        # Track overall execution
        self.execution_phases = []

    async def plan_vacation(self, user_request: str) -> Dict[str, Any]:
        """
        Main entry point for vacation planning.

        Args:
            user_request: Natural language vacation request

        Returns:
            Complete vacation plan
        """
        session_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        logger.info(f"[ORCHESTRATOR] Starting vacation planning session: {session_id}")

        # Parse user request
        parsed_request = self._parse_request(user_request)

        # Execute planning workflow
        result = await self.execute(parsed_request)

        # Add session info
        result["session_id"] = session_id
        result["total_time_seconds"] = round(time.time() - start_time, 2)

        return result

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete vacation planning workflow.

        Args:
            input_data: Parsed vacation request

        Returns:
            Complete vacation plan
        """
        results = {}
        phase_log = []

        # ==================== Phase 1: Security ====================
        logger.info("[ORCHESTRATOR] Phase 1: Security Check")

        security_input = {"text": input_data.get("original_request", "")}
        security_result = await self.security_agent.execute(security_input)
        results["security"] = security_result

        phase_log.append({
            "phase": "security",
            "status": "success" if security_result.get("safe_to_proceed", True) else "warning",
            "execution_time_ms": security_result.get("_metadata", {}).get("execution_time_ms", 0)
        })

        # Check if we should proceed
        if not security_result.get("safe_to_proceed", True):
            risk_level = security_result.get("risk_level", "unknown")
            if risk_level == "critical":
                return {
                    "status": "blocked",
                    "reason": "Critical PII detected - please remove sensitive data",
                    "security_report": security_result,
                    "phase_log": phase_log
                }

        # ==================== Phase 2: Research ====================
        logger.info("[ORCHESTRATOR] Phase 2: Research Phase (Sequential)")

        research_input = {
            "city": input_data.get("city", ""),
            "country": input_data.get("country", ""),
            "citizenship": input_data.get("citizenship", "US"),
            "budget": input_data.get("budget", 3000),
            "travelers": input_data.get("travelers", 2),
            "nights": input_data.get("nights", 7),
            "travel_style": input_data.get("travel_style", "moderate"),
            "from_currency": "USD",
            "dates": {
                "departure": input_data.get("departure_date", ""),
                "return": input_data.get("return_date", "")
            }
        }

        research_result = await self.research_agent.execute(research_input)
        results["research"] = research_result

        phase_log.append({
            "phase": "research",
            "status": research_result.get("status", "error"),
            "execution_time_ms": research_result.get("_metadata", {}).get("execution_time_ms", 0),
            "steps_completed": research_result.get("successful_steps", 0)
        })

        # ==================== Phase 3: Booking ====================
        logger.info("[ORCHESTRATOR] Phase 3: Booking Phase (Parallel)")

        booking_input = {
            "origin": input_data.get("origin", ""),
            "destination": f"{input_data.get('city', '')}, {input_data.get('country', '')}",
            "departure_date": input_data.get("departure_date", ""),
            "return_date": input_data.get("return_date", ""),
            "travelers": input_data.get("travelers", 2),
            "nights": input_data.get("nights", 7),
            "rooms": input_data.get("rooms", 1),
            "cabin_class": input_data.get("cabin_class", "economy"),
            "hotel_budget_per_night": input_data.get("hotel_budget", 150),
            "star_rating": input_data.get("star_rating", 3),
            "needs_car": input_data.get("needs_car", False),
            "interests": input_data.get("interests", []),
            "activity_budget_per_day": input_data.get("activity_budget", 50)
        }

        booking_result = await self.booking_agent.execute(booking_input)
        results["booking"] = booking_result

        phase_log.append({
            "phase": "booking",
            "status": booking_result.get("status", "error"),
            "execution_time_ms": booking_result.get("_metadata", {}).get("execution_time_ms", 0),
            "speedup": booking_result.get("performance", {}).get("speedup_factor", 1.0)
        })

        # ==================== Phase 4: Budget Optimization ====================
        logger.info("[ORCHESTRATOR] Phase 4: Budget Optimization (Loop)")

        # Calculate current total cost
        booking_summary = booking_result.get("booking_summary", {})
        current_cost = booking_summary.get("total_estimated_cost", 0)

        optimizer_input = {
            "target_budget": input_data.get("budget", 3000),
            "current_cost": current_cost,
            "booking_results": {
                "flights": booking_result.get("results", {}).get("flights", {}),
                "hotels": booking_result.get("results", {}).get("hotels", {}),
                "car_rental": booking_result.get("results", {}).get("car_rental", {}),
                "activities": booking_result.get("results", {}).get("activities", {}),
                "nights": input_data.get("nights", 7)
            },
            "auto_approve": True  # For demo purposes
        }

        optimizer_result = await self.optimizer_agent.execute(optimizer_input)
        results["optimization"] = optimizer_result

        phase_log.append({
            "phase": "optimization",
            "status": optimizer_result.get("status", "error"),
            "execution_time_ms": optimizer_result.get("_metadata", {}).get("execution_time_ms", 0),
            "iterations": optimizer_result.get("iterations_used", 0),
            "savings": optimizer_result.get("total_savings", 0)
        })

        # ==================== Compile Final Plan ====================
        final_plan = self._compile_final_plan(input_data, results)

        return {
            "status": "success",
            "destination": f"{input_data.get('city', '')}, {input_data.get('country', '')}",
            "plan": final_plan,
            "phase_results": results,
            "phase_log": phase_log,
            "summary": self._create_summary(results, optimizer_result)
        }

    def _parse_request(self, request: str) -> Dict[str, Any]:
        """Parse natural language request into structured data."""
        parsed = {
            "original_request": request,
            "city": "",
            "country": "",
            "origin": "",
            "departure_date": "",
            "return_date": "",
            "travelers": 2,
            "budget": 3000,
            "nights": 7,
            "interests": [],
            "travel_style": "moderate",
            "citizenship": "US"
        }

        # Extract destination
        dest_patterns = [
            r"to\s+([A-Za-z\s]+),\s*([A-Za-z\s]+)",
            r"trip to\s+([A-Za-z\s]+)",
            r"vacation (?:to|in)\s+([A-Za-z\s]+)"
        ]

        for pattern in dest_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    parsed["city"] = match.group(1).strip()
                    parsed["country"] = match.group(2).strip()
                else:
                    parsed["city"] = match.group(1).strip()
                    # Infer country
                    city_to_country = {
                        "Paris": "France", "Tokyo": "Japan", "London": "UK",
                        "Rome": "Italy", "Berlin": "Germany", "Barcelona": "Spain",
                        "Sydney": "Australia", "Bangkok": "Thailand"
                    }
                    parsed["country"] = city_to_country.get(parsed["city"], "")
                break

        # Extract origin
        origin_match = re.search(r"from\s+([A-Za-z\s,]+?)(?:\s+to|\s+Travel|$)", request, re.IGNORECASE)
        if origin_match:
            parsed["origin"] = origin_match.group(1).strip()

        # Extract dates
        date_pattern = r"(\w+\s+\d{1,2}(?:-\d{1,2})?(?:,?\s*\d{4})?)"
        dates = re.findall(date_pattern, request)
        if dates:
            # Parse dates (simplified)
            parsed["departure_date"] = "2025-06-15"  # Default
            parsed["return_date"] = "2025-06-25"
            parsed["nights"] = 10

        # Extract travelers
        travelers_match = re.search(r"(\d+)\s*(?:adults?|people|travelers?)", request, re.IGNORECASE)
        if travelers_match:
            parsed["travelers"] = int(travelers_match.group(1))

        # Extract budget
        budget_match = re.search(r"\$?([\d,]+)(?:\s*-\s*\$?([\d,]+))?", request)
        if budget_match:
            if budget_match.group(2):
                # Range - take average
                low = int(budget_match.group(1).replace(",", ""))
                high = int(budget_match.group(2).replace(",", ""))
                parsed["budget"] = (low + high) // 2
            else:
                parsed["budget"] = int(budget_match.group(1).replace(",", ""))

        # Extract interests
        interest_keywords = [
            "museums", "art", "history", "food", "cuisine", "wine",
            "architecture", "culture", "shopping", "nightlife", "nature",
            "beaches", "adventure", "relaxation"
        ]
        found_interests = []
        for keyword in interest_keywords:
            if keyword.lower() in request.lower():
                found_interests.append(keyword)
        parsed["interests"] = found_interests if found_interests else ["culture", "food"]

        # Determine travel style from budget
        if parsed["budget"] < 2000:
            parsed["travel_style"] = "budget"
        elif parsed["budget"] > 5000:
            parsed["travel_style"] = "luxury"
        else:
            parsed["travel_style"] = "moderate"

        return parsed

    def _compile_final_plan(
        self,
        input_data: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile the final vacation plan."""
        research = results.get("research", {})
        booking = results.get("booking", {})
        optimization = results.get("optimization", {})

        # Get research report
        research_report = research.get("research_report", {})

        # Get booking summary
        booking_summary = booking.get("booking_summary", {})

        # Generate itinerary text
        itinerary = self._generate_itinerary_text(input_data, research, booking, optimization)

        return {
            "destination": f"{input_data.get('city', '')}, {input_data.get('country', '')}",
            "dates": f"{input_data.get('departure_date', '')} to {input_data.get('return_date', '')}",
            "travelers": input_data.get("travelers", 2),
            "research_summary": research_report,
            "booking_summary": booking_summary,
            "final_cost": optimization.get("final_cost", booking_summary.get("total_estimated_cost", 0)),
            "within_budget": optimization.get("within_budget", True),
            "itinerary": itinerary,
            "model": "gemini-2.5-flash",
            "generated_at": datetime.utcnow().isoformat()
        }

    def _generate_itinerary_text(
        self,
        input_data: Dict[str, Any],
        research: Dict[str, Any],
        booking: Dict[str, Any],
        optimization: Dict[str, Any]
    ) -> str:
        """Generate human-readable itinerary."""
        city = input_data.get("city", "")
        country = input_data.get("country", "")
        travelers = input_data.get("travelers", 2)

        research_report = research.get("research_report", {})
        booking_summary = booking.get("booking_summary", {})

        # Build itinerary text
        lines = [
            f"# Vacation Plan: {city}, {country}",
            "",
            "## Trip Overview",
            f"- **Destination**: {city}, {country}",
            f"- **Dates**: {input_data.get('departure_date', 'TBD')} to {input_data.get('return_date', 'TBD')}",
            f"- **Travelers**: {travelers}",
            f"- **Total Budget**: ${optimization.get('final_cost', 0):,.2f}",
            "",
            "## Weather & Packing",
            f"- **Conditions**: {research_report.get('destination_summary', {}).get('weather', 'N/A')}",
            f"- **Temperature**: {research_report.get('destination_summary', {}).get('temperature', 'N/A')}",
            "",
            "### Packing Essentials",
        ]

        for item in research_report.get("packing_essentials", []):
            lines.append(f"- {item}")

        lines.extend([
            "",
            "## Travel Requirements",
            f"- **Visa Required**: {research_report.get('travel_requirements', {}).get('visa_required', 'Check')}",
            f"- **Max Stay**: {research_report.get('travel_requirements', {}).get('max_stay', 'N/A')}",
            "",
            "### Required Documents",
        ])

        for doc in research_report.get("travel_requirements", {}).get("documents", []):
            lines.append(f"- {doc}")

        lines.extend([
            "",
            "## Bookings",
            "",
            "### Flight",
            f"- **Airline**: {booking_summary.get('recommended_flight', {}).get('airline', 'TBD')}",
            f"- **Total Cost**: ${booking_summary.get('recommended_flight', {}).get('price', 0):,.2f}",
            "",
            "### Hotel",
            f"- **Property**: {booking_summary.get('recommended_hotel', {}).get('name', 'TBD')}",
            f"- **Stars**: {'⭐' * booking_summary.get('recommended_hotel', {}).get('stars', 3)}",
            f"- **Total Cost**: ${booking_summary.get('recommended_hotel', {}).get('price', 0):,.2f}",
            "",
            "## Budget Summary",
            f"- **Original Estimate**: ${optimization.get('original_cost', 0):,.2f}",
            f"- **After Optimization**: ${optimization.get('final_cost', 0):,.2f}",
            f"- **Total Savings**: ${optimization.get('total_savings', 0):,.2f}",
            "",
            "---",
            "",
            "*Plan generated by AI-Powered Vacation Planner using Google ADK*"
        ])

        return "\n".join(lines)

    def _create_summary(
        self,
        results: Dict[str, Any],
        optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create execution summary."""
        return {
            "phases_completed": 4,
            "security_status": results.get("security", {}).get("risk_level", "none"),
            "research_steps": results.get("research", {}).get("successful_steps", 0),
            "booking_speedup": results.get("booking", {}).get("performance", {}).get("speedup_factor", 1.0),
            "optimization_savings": optimization.get("total_savings", 0),
            "final_cost": optimization.get("final_cost", 0),
            "within_budget": optimization.get("within_budget", True)
        }

    def _handle_security_alert(self, message) -> Dict[str, Any]:
        """Handle security alert from Security Guardian."""
        logger.warning(f"[ORCHESTRATOR] Security alert: {message.content}")
        return {"status": "acknowledged", "action": "reviewing"}

    def _handle_budget_update(self, message) -> Dict[str, Any]:
        """Handle budget update from Financial Advisor."""
        logger.info(f"[ORCHESTRATOR] Budget update: {message.content}")
        return {"status": "acknowledged"}
