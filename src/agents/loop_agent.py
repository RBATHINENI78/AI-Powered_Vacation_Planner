"""
Loop Agent - Budget Optimization with iterative refinement
Implements LoopAgent pattern with Human-in-the-Loop (HITL) decision points
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from .base_agent import BaseAgent


class LoopBudgetOptimizer(BaseAgent):
    """
    Loop Agent for budget optimization.
    Iteratively refines booking options until budget constraints are met.
    Includes human-in-the-loop decision points for approval.
    """

    def __init__(self, max_iterations: int = 5):
        super().__init__(
            name="loop_budget_optimizer",
            description="Optimizes bookings through iterative refinement"
        )

        self.max_iterations = max_iterations

        # Optimization strategies
        self.optimization_strategies = [
            ("downgrade_hotel", self._downgrade_hotel, 0.15),
            ("cheaper_flights", self._find_cheaper_flights, 0.20),
            ("reduce_activities", self._reduce_activities, 0.10),
            ("shorter_stay", self._reduce_duration, 0.25),
            ("remove_car", self._remove_car_rental, 0.05)
        ]

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize budget through iterative refinement.

        Args:
            input_data: Contains budget target and current booking results

        Returns:
            Optimized booking options
        """
        target_budget = input_data.get("target_budget", 3000)
        current_cost = input_data.get("current_cost", 0)
        booking_results = input_data.get("booking_results", {})
        auto_approve = input_data.get("auto_approve", False)

        # Check if optimization is needed
        if current_cost <= target_budget:
            return {
                "status": "success",
                "optimization_needed": False,
                "message": f"Current cost (${current_cost}) is within budget (${target_budget})",
                "final_cost": current_cost,
                "final_bookings": booking_results
            }

        logger.info(f"[LOOP] Starting budget optimization. Target: ${target_budget}, Current: ${current_cost}")

        # Track optimization history
        optimization_history = []
        current_bookings = booking_results.copy()
        iteration = 0

        while current_cost > target_budget and iteration < self.max_iterations:
            iteration += 1
            logger.info(f"[LOOP] Iteration {iteration}: Current cost ${current_cost}")

            # Find best optimization strategy
            best_strategy = self._select_strategy(
                current_cost, target_budget, current_bookings
            )

            if not best_strategy:
                logger.warning(f"[LOOP] No more optimization strategies available")
                break

            strategy_name, strategy_func, _ = best_strategy

            # Apply optimization
            optimized, savings, description = strategy_func(current_bookings)

            if savings > 0:
                # Human-in-the-loop decision point
                if not auto_approve:
                    decision = await self._request_human_approval(
                        strategy_name, description, savings, current_cost - savings
                    )
                    if not decision.get("approved", True):
                        logger.info(f"[LOOP] User rejected optimization: {strategy_name}")
                        continue

                # Apply the optimization
                current_bookings = optimized
                previous_cost = current_cost
                current_cost = current_cost - savings

                optimization_history.append({
                    "iteration": iteration,
                    "strategy": strategy_name,
                    "description": description,
                    "savings": round(savings, 2),
                    "new_cost": round(current_cost, 2),
                    "approved": True
                })

                logger.info(f"[LOOP] Applied {strategy_name}: Saved ${savings:.2f}")

            else:
                logger.debug(f"[LOOP] Strategy {strategy_name} yielded no savings")

        # Determine final status
        if current_cost <= target_budget:
            status = "success"
            message = f"Budget optimized to ${current_cost:.2f}"
        else:
            status = "partial"
            message = f"Could only reduce to ${current_cost:.2f} (target: ${target_budget})"

        # Calculate total savings
        original_cost = input_data.get("current_cost", 0)
        total_savings = original_cost - current_cost

        return {
            "status": status,
            "optimization_needed": True,
            "message": message,
            "original_cost": round(original_cost, 2),
            "final_cost": round(current_cost, 2),
            "target_budget": target_budget,
            "total_savings": round(total_savings, 2),
            "savings_percentage": round((total_savings / original_cost) * 100, 1) if original_cost > 0 else 0,
            "iterations_used": iteration,
            "optimization_history": optimization_history,
            "final_bookings": current_bookings,
            "within_budget": current_cost <= target_budget
        }

    def _select_strategy(
        self,
        current_cost: float,
        target: float,
        bookings: Dict[str, Any]
    ) -> Optional[tuple]:
        """Select the best optimization strategy."""
        gap = current_cost - target

        # Sort strategies by potential savings
        viable_strategies = []

        for name, func, savings_pct in self.optimization_strategies:
            potential_savings = current_cost * savings_pct

            # Check if strategy is applicable
            if name == "remove_car" and not bookings.get("car_rental", {}).get("included"):
                continue
            if name == "shorter_stay" and bookings.get("nights", 7) <= 3:
                continue

            viable_strategies.append((name, func, potential_savings))

        # Sort by savings potential
        viable_strategies.sort(key=lambda x: x[2], reverse=True)

        return viable_strategies[0] if viable_strategies else None

    def _downgrade_hotel(self, bookings: Dict[str, Any]) -> tuple:
        """Downgrade hotel to save money."""
        hotel = bookings.get("hotels", {}).get("recommended", {}).get("hotel", {})
        current_price = hotel.get("total_price", 0)

        if current_price > 0:
            # Assume 30% savings from downgrade
            savings = current_price * 0.30
            new_price = current_price - savings

            # Update bookings
            new_bookings = bookings.copy()
            if "hotels" in new_bookings:
                new_bookings["hotels"]["recommended"]["hotel"]["total_price"] = new_price
                new_bookings["hotels"]["recommended"]["hotel"]["stars"] = max(
                    hotel.get("stars", 3) - 1, 2
                )

            return new_bookings, savings, "Downgrade to lower star hotel"

        return bookings, 0, "No hotel to downgrade"

    def _find_cheaper_flights(self, bookings: Dict[str, Any]) -> tuple:
        """Find cheaper flight options."""
        flight = bookings.get("flights", {}).get("recommended", {}).get("flight", {})
        current_price = flight.get("total_price", 0)

        if current_price > 0:
            # Assume 25% savings from different airline/time
            savings = current_price * 0.25
            new_price = current_price - savings

            new_bookings = bookings.copy()
            if "flights" in new_bookings:
                new_bookings["flights"]["recommended"]["flight"]["total_price"] = new_price
                new_bookings["flights"]["recommended"]["flight"]["airline"] = "Budget Carrier"

            return new_bookings, savings, "Switch to budget airline or different times"

        return bookings, 0, "No flights to optimize"

    def _reduce_activities(self, bookings: Dict[str, Any]) -> tuple:
        """Reduce planned activities."""
        activities = bookings.get("activities", {})
        current_cost = activities.get("total_activity_cost", {}).get("total_group", 0)

        if current_cost > 0:
            # Remove 40% of activities
            savings = current_cost * 0.40
            new_cost = current_cost - savings

            new_bookings = bookings.copy()
            if "activities" in new_bookings:
                new_bookings["activities"]["total_activity_cost"]["total_group"] = new_cost

            return new_bookings, savings, "Reduce planned activities by 40%"

        return bookings, 0, "No activities to reduce"

    def _reduce_duration(self, bookings: Dict[str, Any]) -> tuple:
        """Reduce trip duration."""
        hotel = bookings.get("hotels", {}).get("recommended", {}).get("hotel", {})
        nights = hotel.get("nights", 7)

        if nights > 3:
            # Remove 2 nights
            nights_to_remove = 2
            nightly_rate = hotel.get("total_price", 0) / nights if nights > 0 else 0
            hotel_savings = nightly_rate * nights_to_remove

            # Also reduce activity costs proportionally
            activities = bookings.get("activities", {})
            activity_cost = activities.get("total_activity_cost", {}).get("total_group", 0)
            activity_savings = (activity_cost / nights) * nights_to_remove if nights > 0 else 0

            total_savings = hotel_savings + activity_savings

            new_bookings = bookings.copy()
            if "hotels" in new_bookings:
                new_bookings["hotels"]["recommended"]["hotel"]["nights"] = nights - nights_to_remove
                new_bookings["hotels"]["recommended"]["hotel"]["total_price"] = (
                    hotel.get("total_price", 0) - hotel_savings
                )

            return new_bookings, total_savings, f"Reduce trip by {nights_to_remove} nights"

        return bookings, 0, "Trip already at minimum duration"

    def _remove_car_rental(self, bookings: Dict[str, Any]) -> tuple:
        """Remove car rental."""
        car = bookings.get("car_rental", {}).get("recommended", {})
        car_cost = car.get("total_price", 0) if car else 0

        if car_cost > 0:
            new_bookings = bookings.copy()
            new_bookings["car_rental"] = {
                "included": False,
                "message": "Removed to save budget - use public transport"
            }

            return new_bookings, car_cost, "Remove car rental - use public transport"

        return bookings, 0, "No car rental to remove"

    async def _request_human_approval(
        self,
        strategy: str,
        description: str,
        savings: float,
        new_cost: float
    ) -> Dict[str, Any]:
        """
        Request human approval for optimization (HITL).
        In production, this would wait for actual user input.
        """
        logger.info(f"[HITL] Requesting approval for: {strategy}")
        logger.info(f"[HITL] Description: {description}")
        logger.info(f"[HITL] Potential savings: ${savings:.2f}")
        logger.info(f"[HITL] New total cost: ${new_cost:.2f}")

        # In this implementation, auto-approve for demo
        # In production, this would be an actual user prompt
        return {
            "approved": True,
            "strategy": strategy,
            "timestamp": "auto-approved"
        }
