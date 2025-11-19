"""
Structured Logging Configuration
"""

import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class StructuredLogger:
    """
    Structured logger for consistent log formatting.
    Outputs JSON logs for easy parsing and analysis.
    """

    def __init__(self, service_name: str = "vacation_planner"):
        self.service_name = service_name
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set persistent context for all logs."""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear logging context."""
        self.context = {}

    def _format_log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format log entry as structured JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": self.service_name,
            "message": message,
            **self.context
        }

        if extra:
            log_entry.update(extra)

        return log_entry

    def info(self, message: str, **kwargs):
        """Log info message."""
        log_entry = self._format_log("INFO", message, kwargs)
        logger.info(json.dumps(log_entry))

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        log_entry = self._format_log("DEBUG", message, kwargs)
        logger.debug(json.dumps(log_entry))

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        log_entry = self._format_log("WARNING", message, kwargs)
        logger.warning(json.dumps(log_entry))

    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message."""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_message"] = str(error)

        log_entry = self._format_log("ERROR", message, kwargs)
        logger.error(json.dumps(log_entry))

    def metric(self, name: str, value: float, unit: str = "", **kwargs):
        """Log a metric value."""
        kwargs["metric_name"] = name
        kwargs["metric_value"] = value
        if unit:
            kwargs["metric_unit"] = unit

        log_entry = self._format_log("METRIC", f"{name}={value}", kwargs)
        logger.info(json.dumps(log_entry))

    def event(self, event_name: str, **kwargs):
        """Log an event."""
        kwargs["event_name"] = event_name
        log_entry = self._format_log("EVENT", event_name, kwargs)
        logger.info(json.dumps(log_entry))


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: Optional[str] = None
):
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: Output logs as JSON
        log_file: Optional file path for logs
    """
    # Remove default logger
    logger.remove()

    # Console format
    if json_output:
        console_format = "{message}"
    else:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    # Add console handler
    logger.add(
        sys.stderr,
        format=console_format,
        level=level,
        colorize=not json_output
    )

    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level=level,
            rotation="10 MB",
            retention="7 days",
            compression="gz"
        )

    logger.info(f"Logging configured: level={level}, json={json_output}")


# Global structured logger instance
structured_logger = StructuredLogger()
