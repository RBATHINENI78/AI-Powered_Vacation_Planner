"""
Tool Callbacks - Before/After execution hooks for tools
"""

import time
from datetime import datetime
from typing import Dict, Any, Callable
from loguru import logger


class ToolCallbackManager:
    """
    Manages before/after callbacks for tool execution
    """

    def __init__(self):
        self.event_log = []
        self.metrics = {}

    def before_tool_execute(
        self,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Called before tool execution.
        Can validate, modify args, or cancel execution.

        Args:
            tool_name: Name of the tool
            tool_args: Arguments passed to tool

        Returns:
            Modified args and proceed flag
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "before_tool_execute",
            "tool": tool_name,
            "args": tool_args
        }
        self.event_log.append(event)

        logger.info(f"[BEFORE] Tool: {tool_name}")
        logger.debug(f"[BEFORE] Args: {tool_args}")

        # Start timing
        self.metrics[tool_name] = {
            "start_time": time.time(),
            "call_count": self.metrics.get(tool_name, {}).get("call_count", 0) + 1
        }

        # Validation examples
        if tool_name == "get_weather_info":
            if not tool_args.get("city"):
                logger.warning(f"[BEFORE] Missing city for weather tool")
                return {"proceed": False, "error": "City is required"}

        if tool_name == "get_currency_exchange":
            if not tool_args.get("from_currency") or not tool_args.get("to_currency"):
                logger.warning(f"[BEFORE] Missing currency codes")
                return {"proceed": False, "error": "Currency codes required"}

        return {
            "proceed": True,
            "modified_args": tool_args,
            "request_id": f"{tool_name}_{int(time.time())}"
        }

    def after_tool_execute(
        self,
        tool_name: str,
        tool_result: Any,
        error: Exception = None
    ) -> Any:
        """
        Called after tool execution.
        Can modify results, log metrics, trigger alerts.

        Args:
            tool_name: Name of the tool
            tool_result: Result from tool execution
            error: Any exception that occurred

        Returns:
            Modified result
        """
        # Calculate execution time
        start_time = self.metrics.get(tool_name, {}).get("start_time", time.time())
        execution_time = time.time() - start_time

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "after_tool_execute",
            "tool": tool_name,
            "execution_time_ms": round(execution_time * 1000, 2),
            "success": error is None
        }
        self.event_log.append(event)

        # Update metrics
        if tool_name in self.metrics:
            self.metrics[tool_name]["last_execution_time"] = execution_time
            self.metrics[tool_name]["last_success"] = error is None

        logger.info(f"[AFTER] Tool: {tool_name} completed in {execution_time:.3f}s")

        # Handle errors
        if error:
            logger.error(f"[AFTER] Tool {tool_name} failed: {error}")
            return {
                "error": str(error),
                "tool": tool_name,
                "status": "error"
            }

        # Enhance result with metadata
        if isinstance(tool_result, dict):
            tool_result["_metadata"] = {
                "tool_name": tool_name,
                "execution_time_ms": round(execution_time * 1000, 2),
                "processed_at": datetime.utcnow().isoformat()
            }

        # Alert on slow tools
        if execution_time > 5.0:
            logger.warning(f"[ALERT] Slow tool: {tool_name} took {execution_time:.2f}s")

        return tool_result

    def get_metrics(self) -> Dict[str, Any]:
        """Get all tool metrics"""
        return {
            "tools": self.metrics,
            "total_events": len(self.event_log)
        }

    def get_event_log(self) -> list:
        """Get the event log"""
        return self.event_log


# Global callback manager instance
callback_manager = ToolCallbackManager()


def with_callbacks(tool_func: Callable) -> Callable:
    """
    Decorator to wrap tools with before/after callbacks.

    Usage:
        @with_callbacks
        def my_tool(arg1, arg2):
            return result
    """
    def wrapper(*args, **kwargs):
        tool_name = tool_func.__name__

        # Before callback
        before_result = callback_manager.before_tool_execute(tool_name, kwargs or {"args": args})

        if not before_result.get("proceed", True):
            return {"error": before_result.get("error", "Execution cancelled"), "status": "cancelled"}

        # Execute tool
        error = None
        result = None
        try:
            result = tool_func(*args, **kwargs)
        except Exception as e:
            error = e
            result = None

        # After callback
        final_result = callback_manager.after_tool_execute(tool_name, result, error)

        return final_result

    wrapper.__name__ = tool_func.__name__
    wrapper.__doc__ = tool_func.__doc__
    return wrapper
