import json
import logging

from mcp_core.observability.context import get_current_context, set_context
from mcp_core.observability.logger import JsonFormatter, configure_logging


def test_context_management():
    # Initial state should be empty
    ctx = get_current_context()
    assert ctx.run_id is None
    assert ctx.request_id is None

    # Set context
    token = set_context(run_id="run-123", request_id="req-456")
    ctx = get_current_context()
    assert ctx.run_id == "run-123"
    assert ctx.request_id == "req-456"
    assert ctx.trace_id is None

    # Reset context
    token.reset()
    ctx = get_current_context()
    assert ctx.run_id is None
    assert ctx.request_id is None


def test_json_formatter():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Hello world",
        args=(),
        exc_info=None,
    )

    # Test without context
    output = formatter.format(record)
    data = json.loads(output)
    assert data["message"] == "Hello world"
    assert data["level"] == "INFO"
    assert "run_id" not in data

    # Test with context
    token = set_context(run_id="run-123", tool_name="test-tool")
    output = formatter.format(record)
    data = json.loads(output)
    assert data["run_id"] == "run-123"
    assert data["tool_name"] == "test-tool"
    token.reset()


def test_json_formatter_extra_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test extra",
        args=(),
        exc_info=None,
    )
    # Simulate 'extra' dict passed to logger
    record.props = {"foo": "bar", "count": 42}  # type: ignore

    output = formatter.format(record)
    data = json.loads(output)
    assert data["foo"] == "bar"
    assert data["count"] == 42


def test_configure_logging():
    # Just ensure it doesn't crash and sets a handler
    configure_logging()
    root = logging.getLogger()
    assert len(root.handlers) > 0
