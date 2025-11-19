"""
Distributed Tracing - Track execution flow across agents
"""

import uuid
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from contextlib import contextmanager


class Span:
    """Represents a single span in a trace."""

    def __init__(
        self,
        name: str,
        trace_id: str,
        parent_id: Optional[str] = None
    ):
        self.span_id = str(uuid.uuid4())[:8]
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.status = "running"
        self.attributes: Dict[str, Any] = {}
        self.events: List[Dict[str, Any]] = []

    def set_attribute(self, key: str, value: Any):
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": datetime.utcnow().isoformat(),
            "attributes": attributes or {}
        })

    def end(self, status: str = "ok"):
        """End the span."""
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events
        }


class TracingProvider:
    """
    Distributed tracing provider.
    Tracks execution flow across agents and tools.
    """

    def __init__(self, service_name: str = "vacation_planner"):
        self.service_name = service_name
        self.traces: Dict[str, List[Span]] = {}
        self.active_spans: Dict[str, Span] = {}

    def start_trace(self, name: str) -> str:
        """
        Start a new trace.

        Args:
            name: Name of the trace

        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())[:16]
        self.traces[trace_id] = []

        logger.debug(f"[TRACE] Started trace: {trace_id} ({name})")
        return trace_id

    def start_span(
        self,
        name: str,
        trace_id: str,
        parent_id: Optional[str] = None
    ) -> Span:
        """
        Start a new span within a trace.

        Args:
            name: Span name
            trace_id: Parent trace ID
            parent_id: Parent span ID (for nested spans)

        Returns:
            New Span object
        """
        span = Span(name, trace_id, parent_id)

        if trace_id in self.traces:
            self.traces[trace_id].append(span)

        self.active_spans[span.span_id] = span

        logger.debug(f"[TRACE] Started span: {span.span_id} ({name})")
        return span

    def end_span(self, span: Span, status: str = "ok"):
        """
        End a span.

        Args:
            span: Span to end
            status: Final status (ok, error)
        """
        span.end(status)

        if span.span_id in self.active_spans:
            del self.active_spans[span.span_id]

        logger.debug(f"[TRACE] Ended span: {span.span_id} ({span.duration_ms:.2f}ms)")

    @contextmanager
    def span_context(
        self,
        name: str,
        trace_id: str,
        parent_id: Optional[str] = None
    ):
        """
        Context manager for spans.

        Usage:
            with tracer.span_context("my_operation", trace_id) as span:
                # do work
                span.set_attribute("key", "value")
        """
        span = self.start_span(name, trace_id, parent_id)
        try:
            yield span
            self.end_span(span, "ok")
        except Exception as e:
            span.add_event("error", {"message": str(e)})
            self.end_span(span, "error")
            raise

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        Get all spans for a trace.

        Args:
            trace_id: Trace ID

        Returns:
            List of span dictionaries
        """
        spans = self.traces.get(trace_id, [])
        return [span.to_dict() for span in spans]

    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """
        Get summary of a trace.

        Args:
            trace_id: Trace ID

        Returns:
            Trace summary
        """
        spans = self.traces.get(trace_id, [])

        if not spans:
            return {"trace_id": trace_id, "status": "not_found"}

        total_duration = sum(span.duration_ms for span in spans)
        error_count = len([s for s in spans if s.status == "error"])

        return {
            "trace_id": trace_id,
            "service": self.service_name,
            "span_count": len(spans),
            "total_duration_ms": round(total_duration, 2),
            "error_count": error_count,
            "status": "error" if error_count > 0 else "ok"
        }

    def export_traces(self) -> Dict[str, Any]:
        """Export all traces for analysis."""
        return {
            "service": self.service_name,
            "trace_count": len(self.traces),
            "traces": {
                trace_id: self.get_trace(trace_id)
                for trace_id in self.traces
            }
        }


# Global tracer instance
tracer = TracingProvider()
