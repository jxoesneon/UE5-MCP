import json
import logging
import sys
from datetime import datetime
from typing import Any

from ..config.settings import settings
from .context import get_current_context


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ctx = get_current_context()

        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add context fields if present
        if ctx.run_id:
            log_entry["run_id"] = ctx.run_id
        if ctx.request_id:
            log_entry["request_id"] = ctx.request_id
        if ctx.trace_id:
            log_entry["trace_id"] = ctx.trace_id
        if ctx.tool_name:
            log_entry["tool_name"] = ctx.tool_name

        # Add extra fields from record
        if hasattr(record, "props") and isinstance(record.props, dict):
            log_entry.update(record.props)

        # Handle exception info
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

def configure_logging():
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set level based on settings
    level_str = settings.logging.level.upper()
    level = getattr(logging, level_str, logging.INFO)
    root_logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)

    if settings.logging.format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        # Simple text format for local dev if requested
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s] %(message)s'
        )
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
