"""
Base Agent - Foundation class for all specialized agents
Implements A2A communication, callbacks, and observability
"""

import uuid
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from loguru import logger


class AgentMessage:
    """Message structure for Agent-to-Agent communication"""

    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        priority: str = "normal"
    ):
        self.id = str(uuid.uuid4())
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.content = content
        self.priority = priority
        self.timestamp = datetime.utcnow().isoformat()
        self.acknowledged = False


class BaseAgent(ABC):
    """
    Base class for all specialized agents.
    Implements core functionality:
    - Agent-to-Agent (A2A) communication
    - Before/After callbacks
    - Observability (tracing, metrics, logging)
    """

    # Class-level message registry for A2A communication
    _message_registry: Dict[str, List[AgentMessage]] = {}
    _message_handlers: Dict[str, Dict[str, Callable]] = {}

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.metrics = {
            "executions": 0,
            "total_time": 0,
            "errors": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
        self._callbacks = {
            "before_execute": [],
            "after_execute": [],
            "on_error": []
        }

        # Register agent for A2A communication
        if name not in BaseAgent._message_registry:
            BaseAgent._message_registry[name] = []
        if name not in BaseAgent._message_handlers:
            BaseAgent._message_handlers[name] = {}

        logger.info(f"Initialized agent: {name}")

    # ==================== A2A Communication ====================

    def send_message(
        self,
        to_agent: str,
        message_type: str,
        content: Dict[str, Any],
        priority: str = "normal"
    ) -> str:
        """
        Send a message to another agent.

        Args:
            to_agent: Target agent name
            message_type: Type of message (advisory, request, data)
            content: Message content
            priority: Message priority (low, normal, high, critical)

        Returns:
            Message ID
        """
        message = AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority
        )

        # Add to target agent's message queue
        if to_agent not in BaseAgent._message_registry:
            BaseAgent._message_registry[to_agent] = []

        BaseAgent._message_registry[to_agent].append(message)
        self.metrics["messages_sent"] += 1

        logger.info(f"[A2A] {self.name} -> {to_agent}: {message_type}")
        logger.debug(f"[A2A] Content: {content}")

        return message.id

    def receive_messages(self, message_type: Optional[str] = None) -> List[AgentMessage]:
        """
        Receive messages from other agents.

        Args:
            message_type: Filter by message type (optional)

        Returns:
            List of messages
        """
        messages = BaseAgent._message_registry.get(self.name, [])

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        self.metrics["messages_received"] += len(messages)
        return messages

    def process_messages(self) -> List[Dict[str, Any]]:
        """
        Process all pending messages using registered handlers.

        Returns:
            List of processing results
        """
        results = []
        messages = self.receive_messages()

        for message in messages:
            handler = BaseAgent._message_handlers.get(self.name, {}).get(message.message_type)

            if handler:
                try:
                    result = handler(message)
                    message.acknowledged = True
                    results.append({
                        "message_id": message.id,
                        "status": "processed",
                        "result": result
                    })
                    logger.info(f"[A2A] {self.name} processed message from {message.from_agent}")
                except Exception as e:
                    results.append({
                        "message_id": message.id,
                        "status": "error",
                        "error": str(e)
                    })
                    logger.error(f"[A2A] Error processing message: {e}")
            else:
                logger.warning(f"[A2A] No handler for message type: {message.message_type}")

        # Clear processed messages
        BaseAgent._message_registry[self.name] = [
            m for m in BaseAgent._message_registry.get(self.name, [])
            if not m.acknowledged
        ]

        return results

    def register_message_handler(self, message_type: str, handler: Callable):
        """
        Register a handler for a specific message type.

        Args:
            message_type: Type of message to handle
            handler: Callback function
        """
        BaseAgent._message_handlers[self.name][message_type] = handler
        logger.debug(f"[A2A] {self.name} registered handler for: {message_type}")

    # ==================== Callbacks ====================

    def add_callback(self, event: str, callback: Callable):
        """
        Add a callback for an event.

        Args:
            event: Event name (before_execute, after_execute, on_error)
            callback: Callback function
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _run_callbacks(self, event: str, **kwargs) -> Dict[str, Any]:
        """Run all callbacks for an event."""
        results = {}
        for callback in self._callbacks.get(event, []):
            try:
                result = callback(self, **kwargs)
                if result:
                    results.update(result)
            except Exception as e:
                logger.error(f"Callback error ({event}): {e}")
        return results

    # ==================== Execution ====================

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with full callback and observability support.

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution result
        """
        start_time = time.time()
        self.metrics["executions"] += 1

        try:
            # Before callbacks
            before_result = self._run_callbacks(
                "before_execute",
                input_data=input_data
            )

            # Check if execution should proceed
            if before_result.get("cancel", False):
                return {
                    "status": "cancelled",
                    "reason": before_result.get("reason", "Cancelled by callback"),
                    "agent": self.name
                }

            # Modify input if needed
            if "modified_input" in before_result:
                input_data = before_result["modified_input"]

            logger.info(f"[EXECUTE] {self.name} starting execution")

            # Process any pending A2A messages
            message_results = self.process_messages()

            # Run the agent's main logic
            result = await self._execute_impl(input_data)

            # Calculate execution time
            execution_time = time.time() - start_time
            self.metrics["total_time"] += execution_time

            # Add metadata
            result["_metadata"] = {
                "agent": self.name,
                "execution_time_ms": round(execution_time * 1000, 2),
                "timestamp": datetime.utcnow().isoformat(),
                "messages_processed": len(message_results)
            }

            # After callbacks
            after_result = self._run_callbacks(
                "after_execute",
                result=result,
                execution_time=execution_time
            )

            # Enhance result if callback provided modifications
            if "enhanced_result" in after_result:
                result.update(after_result["enhanced_result"])

            logger.info(f"[EXECUTE] {self.name} completed in {execution_time:.3f}s")

            return result

        except Exception as e:
            self.metrics["errors"] += 1
            execution_time = time.time() - start_time

            # Error callbacks
            error_result = self._run_callbacks(
                "on_error",
                error=e,
                input_data=input_data
            )

            logger.error(f"[EXECUTE] {self.name} failed: {e}")

            # Check if error was handled
            if error_result.get("handled", False):
                return error_result.get("result", {"status": "error", "error": str(e)})

            return {
                "status": "error",
                "agent": self.name,
                "error": str(e),
                "execution_time_ms": round(execution_time * 1000, 2)
            }

    @abstractmethod
    async def _execute_impl(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement the agent's main logic.
        Must be overridden by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Execution result
        """
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "agent": self.name,
            "metrics": self.metrics,
            "avg_execution_time": (
                self.metrics["total_time"] / self.metrics["executions"]
                if self.metrics["executions"] > 0 else 0
            )
        }
