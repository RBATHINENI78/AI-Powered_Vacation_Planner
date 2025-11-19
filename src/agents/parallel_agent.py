"""
Parallel Agent - Orchestrates booking phase with concurrent execution
Implements ParallelAgent pattern from ADK for 3-4x speed improvement
"""

import asyncio
from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent
from .booking_agents import FlightBookingAgent, HotelBookingAgent, CarRentalAgent
from .experience_curator import ExperienceCuratorAgent


class ParallelBookingAgent(BaseAgent):
    """
    Parallel Agent for booking phase.
    Executes multiple booking agents concurrently for better performance.
    """

    def __init__(self):
        super().__init__(
            name="parallel_booking",
            description="Orchestrates booking phase with parallel execution"
        )

        # Initialize sub-agents
        self.flight_agent = FlightBookingAgent()
        self.hotel_agent = HotelBookingAgent()
        self.car_agent = CarRentalAgent()
        self.experience_agent = ExperienceCuratorAgent()

        # Track parallel tasks
        self.parallel_tasks = [
            ("flights", self.flight_agent),
            ("hotels", self.hotel_agent),
            ("car_rental", self.car_agent),
            ("activities", self.experience_agent)
        ]

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute booking agents in parallel.
        All agents run concurrently as they are independent.

        Args:
            input_data: Contains booking parameters for all agents

        Returns:
            Combined booking results from all agents
        """
        logger.info(f"[PARALLEL] Starting booking phase with {len(self.parallel_tasks)} concurrent tasks")

        # Prepare inputs for each agent
        agent_inputs = self._prepare_all_inputs(input_data)

        # Create async tasks
        tasks = []
        task_names = []

        for task_name, agent in self.parallel_tasks:
            task_input = agent_inputs.get(task_name, {})
            task = asyncio.create_task(
                self._execute_with_tracking(task_name, agent, task_input)
            )
            tasks.append(task)
            task_names.append(task_name)

        # Execute all tasks concurrently
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        results = {}
        execution_log = []
        total_time = 0
        max_time = 0

        for i, (task_name, result) in enumerate(zip(task_names, results_list)):
            if isinstance(result, Exception):
                logger.error(f"[PARALLEL] Task {task_name} failed: {result}")
                results[task_name] = {"status": "error", "error": str(result)}
                execution_log.append({
                    "task": task_name,
                    "status": "error",
                    "error": str(result)
                })
            else:
                results[task_name] = result
                exec_time = result.get("_metadata", {}).get("execution_time_ms", 0)
                total_time += exec_time
                max_time = max(max_time, exec_time)
                execution_log.append({
                    "task": task_name,
                    "status": "success",
                    "execution_time_ms": exec_time
                })

        # Calculate speedup
        if max_time > 0:
            speedup = total_time / max_time
        else:
            speedup = 1.0

        # Compile booking summary
        booking_summary = self._compile_booking_summary(results)

        logger.info(f"[PARALLEL] Completed booking phase. Speedup: {speedup:.2f}x")

        return {
            "status": "success",
            "phase": "booking",
            "results": results,
            "execution_log": execution_log,
            "booking_summary": booking_summary,
            "performance": {
                "total_sequential_time_ms": total_time,
                "actual_parallel_time_ms": max_time,
                "speedup_factor": round(speedup, 2),
                "tasks_completed": len([e for e in execution_log if e["status"] == "success"]),
                "tasks_failed": len([e for e in execution_log if e["status"] == "error"])
            }
        }

    async def _execute_with_tracking(
        self,
        task_name: str,
        agent: BaseAgent,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent with additional tracking."""
        logger.debug(f"[PARALLEL] Starting task: {task_name}")

        result = await agent.execute(input_data)

        logger.debug(f"[PARALLEL] Completed task: {task_name}")
        return result

    def _prepare_all_inputs(self, input_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Prepare inputs for all parallel agents."""

        # Common data
        destination = input_data.get("destination", "")
        origin = input_data.get("origin", "")
        departure_date = input_data.get("departure_date", "")
        return_date = input_data.get("return_date", "")
        travelers = input_data.get("travelers", 2)

        return {
            "flights": {
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "travelers": travelers,
                "cabin_class": input_data.get("cabin_class", "economy"),
                "priority": input_data.get("flight_priority", "price")
            },
            "hotels": {
                "destination": destination,
                "check_in": departure_date,
                "check_out": return_date,
                "guests": travelers,
                "rooms": input_data.get("rooms", 1),
                "budget_per_night": input_data.get("hotel_budget_per_night", 150),
                "star_rating": input_data.get("star_rating", 3),
                "priority": input_data.get("hotel_priority", "rating")
            },
            "car_rental": {
                "pickup_location": destination,
                "pickup_date": departure_date,
                "return_date": return_date,
                "car_type": input_data.get("car_type", "compact"),
                "needs_car": input_data.get("needs_car", False)
            },
            "activities": {
                "destination": destination,
                "interests": input_data.get("interests", []),
                "activity_budget_per_day": input_data.get("activity_budget_per_day", 50),
                "nights": input_data.get("nights", 7),
                "travelers": travelers
            }
        }

    def _compile_booking_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compile summary of all bookings."""

        flights = results.get("flights", {})
        hotels = results.get("hotels", {})
        car = results.get("car_rental", {})
        activities = results.get("activities", {})

        # Get recommended options
        flight_rec = flights.get("recommended", {}).get("flight", {})
        hotel_rec = hotels.get("recommended", {}).get("hotel", {})
        car_rec = car.get("recommended", {})
        activity_cost = activities.get("total_activity_cost", {})

        # Calculate totals
        flight_cost = flight_rec.get("total_price", 0)
        hotel_cost = hotel_rec.get("total_price", 0)
        car_cost = car_rec.get("total_price", 0) if car_rec else 0
        activity_total = activity_cost.get("total_group", 0)

        total_cost = flight_cost + hotel_cost + car_cost + activity_total

        return {
            "recommended_flight": {
                "airline": flight_rec.get("airline", "N/A"),
                "price": flight_rec.get("total_price", 0)
            },
            "recommended_hotel": {
                "name": hotel_rec.get("name", "N/A"),
                "price": hotel_rec.get("total_price", 0),
                "stars": hotel_rec.get("stars", 0)
            },
            "car_rental": {
                "included": car_rec is not None and car_rec != {},
                "price": car_cost
            },
            "activities": {
                "count": len(activities.get("suggested_itinerary", [])),
                "total_cost": activity_total
            },
            "total_estimated_cost": round(total_cost, 2),
            "options_found": {
                "flights": flights.get("results_count", 0),
                "hotels": hotels.get("results_count", 0),
                "rentals": car.get("results_count", 0)
            }
        }
