"""
Metrics Collection - Performance monitoring and statistics
"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class MetricsCollector:
    """
    Metrics collector for performance monitoring.
    Supports counters, gauges, and histograms.
    """

    def __init__(self, namespace: str = "vacation_planner"):
        self.namespace = namespace
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.labels: Dict[str, Dict[str, str]] = {}

    # ==================== Counters ====================

    def increment(
        self,
        name: str,
        value: int = 1,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Increment a counter.

        Args:
            name: Counter name
            value: Increment value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self.counters[key] = self.counters.get(key, 0) + value

        if labels:
            self.labels[key] = labels

        logger.debug(f"[METRICS] Counter {name}: +{value} = {self.counters[key]}")

    def get_counter(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> int:
        """Get counter value."""
        key = self._make_key(name, labels)
        return self.counters.get(key, 0)

    # ==================== Gauges ====================

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Set a gauge value.

        Args:
            name: Gauge name
            value: Current value
            labels: Optional labels
        """
        key = self._make_key(name, labels)
        self.gauges[key] = value

        if labels:
            self.labels[key] = labels

        logger.debug(f"[METRICS] Gauge {name}: {value}")

    def get_gauge(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> float:
        """Get gauge value."""
        key = self._make_key(name, labels)
        return self.gauges.get(key, 0.0)

    # ==================== Histograms ====================

    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Record a value in a histogram.

        Args:
            name: Histogram name
            value: Value to record
            labels: Optional labels
        """
        key = self._make_key(name, labels)

        if key not in self.histograms:
            self.histograms[key] = []

        self.histograms[key].append(value)

        if labels:
            self.labels[key] = labels

        logger.debug(f"[METRICS] Histogram {name}: recorded {value}")

    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """
        Get histogram statistics.

        Args:
            name: Histogram name
            labels: Optional labels

        Returns:
            Statistics dict with count, sum, avg, min, max, p50, p95, p99
        """
        key = self._make_key(name, labels)
        values = self.histograms.get(key, [])

        if not values:
            return {
                "count": 0,
                "sum": 0,
                "avg": 0,
                "min": 0,
                "max": 0
            }

        sorted_values = sorted(values)
        count = len(values)

        return {
            "count": count,
            "sum": sum(values),
            "avg": sum(values) / count,
            "min": min(values),
            "max": max(values),
            "p50": self._percentile(sorted_values, 50),
            "p95": self._percentile(sorted_values, 95),
            "p99": self._percentile(sorted_values, 99)
        }

    # ==================== Timing ====================

    def time_operation(self, name: str, labels: Optional[Dict[str, str]] = None):
        """
        Context manager for timing operations.

        Usage:
            with metrics.time_operation("agent_execution"):
                # do work
        """
        return TimingContext(self, name, labels)

    # ==================== Export ====================

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        return {
            "namespace": self.namespace,
            "timestamp": datetime.utcnow().isoformat(),
            "counters": {
                key: {
                    "value": value,
                    "labels": self.labels.get(key, {})
                }
                for key, value in self.counters.items()
            },
            "gauges": {
                key: {
                    "value": value,
                    "labels": self.labels.get(key, {})
                }
                for key, value in self.gauges.items()
            },
            "histograms": {
                key: {
                    "stats": self.get_histogram_stats(key.split("{")[0]),
                    "labels": self.labels.get(key, {})
                }
                for key in self.histograms.keys()
            }
        }

    def reset(self):
        """Reset all metrics."""
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.labels = {}

    # ==================== Helpers ====================

    def _make_key(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a unique key for the metric."""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _percentile(self, sorted_values: List[float], p: int) -> float:
        """Calculate percentile value."""
        if not sorted_values:
            return 0

        index = (len(sorted_values) - 1) * p / 100
        lower = int(index)
        upper = lower + 1

        if upper >= len(sorted_values):
            return sorted_values[-1]

        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


class TimingContext:
    """Context manager for timing operations."""

    def __init__(
        self,
        collector: MetricsCollector,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time: float = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        self.collector.record(f"{self.name}_duration_ms", duration_ms, self.labels)

        if exc_type:
            self.collector.increment(f"{self.name}_errors", 1, self.labels)
        else:
            self.collector.increment(f"{self.name}_success", 1, self.labels)


# Global metrics instance
metrics = MetricsCollector()
