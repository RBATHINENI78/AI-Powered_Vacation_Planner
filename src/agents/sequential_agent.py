"""
Sequential Agent - Orchestrates research phase with order-dependent workflows
Implements SequentialAgent pattern from ADK
"""

import asyncio
from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent
from .destination_intelligence import DestinationIntelligenceAgent
from .immigration_specialist import ImmigrationSpecialistAgent
from .financial_advisor import FinancialAdvisorAgent


class SequentialResearchAgent(BaseAgent):
    """
    Sequential Agent for research phase.
    Executes agents in order: Destination -> Immigration -> Financial
    Each step depends on the previous step's output.
    """

    def __init__(self):
        super().__init__(
            name="sequential_research",
            description="Orchestrates research phase in sequential order"
        )

        # Initialize sub-agents
        self.destination_agent = DestinationIntelligenceAgent()
        self.immigration_agent = ImmigrationSpecialistAgent()
        self.financial_agent = FinancialAdvisorAgent()

        # Track execution order
        self.execution_order = [
            ("destination", self.destination_agent),
            ("immigration", self.immigration_agent),
            ("financial", self.financial_agent)
        ]

    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research agents sequentially.
        Each agent receives data from previous agents.

        Args:
            input_data: Contains destination, citizenship, budget info

        Returns:
            Combined research results from all agents
        """
        results = {}
        accumulated_data = input_data.copy()
        execution_log = []

        logger.info(f"[SEQUENTIAL] Starting research phase with {len(self.execution_order)} agents")

        for step_name, agent in self.execution_order:
            logger.info(f"[SEQUENTIAL] Executing step: {step_name}")

            try:
                # Prepare input for this agent
                agent_input = self._prepare_agent_input(step_name, accumulated_data, results)

                # Execute agent
                result = await agent.execute(agent_input)

                # Store result
                results[step_name] = result

                # Accumulate data for next agent
                accumulated_data = self._accumulate_data(accumulated_data, step_name, result)

                execution_log.append({
                    "step": step_name,
                    "status": "success",
                    "execution_time_ms": result.get("_metadata", {}).get("execution_time_ms", 0)
                })

                logger.info(f"[SEQUENTIAL] Completed step: {step_name}")

            except Exception as e:
                logger.error(f"[SEQUENTIAL] Error in step {step_name}: {e}")
                execution_log.append({
                    "step": step_name,
                    "status": "error",
                    "error": str(e)
                })

                # Decide whether to continue or abort
                if step_name == "destination":
                    # Critical step - abort
                    return {
                        "status": "error",
                        "error": f"Critical step '{step_name}' failed: {e}",
                        "partial_results": results
                    }
                else:
                    # Non-critical - continue with warnings
                    results[step_name] = {"status": "error", "error": str(e)}

        # Compile final research report
        research_report = self._compile_research_report(results, input_data)

        return {
            "status": "success",
            "phase": "research",
            "results": results,
            "execution_log": execution_log,
            "research_report": research_report,
            "total_steps": len(self.execution_order),
            "successful_steps": len([e for e in execution_log if e["status"] == "success"])
        }

    def _prepare_agent_input(
        self,
        step_name: str,
        accumulated: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for each agent based on previous results."""

        if step_name == "destination":
            return {
                "city": accumulated.get("city", ""),
                "country": accumulated.get("country", ""),
                "dates": accumulated.get("dates", {})
            }

        elif step_name == "immigration":
            # Use weather data from destination agent
            dest_result = results.get("destination", {})

            # Check for severe weather warnings
            analysis = dest_result.get("analysis", {})

            return {
                "citizenship": accumulated.get("citizenship", "US"),
                "destination": f"{accumulated.get('city', '')}, {accumulated.get('country', '')}",
                "duration_days": accumulated.get("nights", 7),
                "weather_advisory": analysis.get("warnings", [])
            }

        elif step_name == "financial":
            # Use data from previous agents
            dest_result = results.get("destination", {})
            imm_result = results.get("immigration", {})

            return {
                "destination": f"{accumulated.get('city', '')}, {accumulated.get('country', '')}",
                "from_currency": accumulated.get("from_currency", "USD"),
                "budget": accumulated.get("budget", 3000),
                "travelers": accumulated.get("travelers", 2),
                "nights": accumulated.get("nights", 7),
                "travel_style": accumulated.get("travel_style", "moderate"),
                "visa_required": imm_result.get("visa_requirements", {}).get("required", False)
            }

        return accumulated

    def _accumulate_data(
        self,
        accumulated: Dict[str, Any],
        step_name: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Accumulate data from agent results for next steps."""

        if step_name == "destination":
            # Extract weather info for other agents
            current_weather = result.get("current_weather", {})
            analysis = result.get("analysis", {})

            accumulated["weather"] = current_weather
            accumulated["weather_warnings"] = analysis.get("warnings", [])
            accumulated["packing_list"] = result.get("packing_list", {})

        elif step_name == "immigration":
            # Extract visa info
            visa_req = result.get("visa_requirements", {})
            accumulated["visa_required"] = visa_req.get("required", False)
            accumulated["documents_needed"] = result.get("required_documents", [])

        elif step_name == "financial":
            # Extract budget info
            accumulated["budget_breakdown"] = result.get("budget_breakdown", {})
            accumulated["exchange_rate"] = result.get("currency_info", {}).get("exchange_rate", 1.0)

        return accumulated

    def _compile_research_report(
        self,
        results: Dict[str, Any],
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile a summary research report from all agents."""

        dest_result = results.get("destination", {})
        imm_result = results.get("immigration", {})
        fin_result = results.get("financial", {})

        return {
            "destination_summary": {
                "location": f"{input_data.get('city', '')}, {input_data.get('country', '')}",
                "weather": dest_result.get("current_weather", {}).get("conditions", "N/A"),
                "temperature": dest_result.get("current_weather", {}).get("temperature", "N/A"),
                "travel_conditions": dest_result.get("analysis", {}).get("travel_conditions", "N/A"),
                "best_time": dest_result.get("best_time_to_visit", "N/A")
            },
            "travel_requirements": {
                "visa_required": imm_result.get("visa_requirements", {}).get("required", "Check"),
                "max_stay": imm_result.get("visa_requirements", {}).get("max_stay", "N/A"),
                "documents": imm_result.get("required_documents", [])[:5],  # Top 5
                "warnings": imm_result.get("travel_warnings", [])
            },
            "financial_summary": {
                "total_budget": fin_result.get("budget_breakdown", {}).get("total", 0),
                "per_person": fin_result.get("budget_breakdown", {}).get("per_person", 0),
                "exchange_rate": fin_result.get("currency_info", {}).get("exchange_rate", 1.0),
                "status": fin_result.get("budget_assessment", {}).get("status", "N/A")
            },
            "packing_essentials": dest_result.get("packing_list", {}).get("essentials", [])[:5]
        }
