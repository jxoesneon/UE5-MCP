from contextvars import ContextVar
from typing import NamedTuple


class ExecutionContext(NamedTuple):
    request_id: str | None
    run_id: str | None
    trace_id: str | None
    tool_name: str | None

# Context variables with default None
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
_run_id_ctx: ContextVar[str | None] = ContextVar("run_id", default=None)
_trace_id_ctx: ContextVar[str | None] = ContextVar("trace_id", default=None)
_tool_name_ctx: ContextVar[str | None] = ContextVar("tool_name", default=None)

def get_current_context() -> ExecutionContext:
    return ExecutionContext(
        request_id=_request_id_ctx.get(),
        run_id=_run_id_ctx.get(),
        trace_id=_trace_id_ctx.get(),
        tool_name=_tool_name_ctx.get(),
    )

class ContextToken:
    def __init__(self, tokens: dict):
        self.tokens = tokens

    def reset(self):
        for var, token in self.tokens.items():
            var.reset(token)

def set_context(
    request_id: str | None = None,
    run_id: str | None = None,
    trace_id: str | None = None,
    tool_name: str | None = None,
) -> ContextToken:
    tokens = {}
    if request_id is not None:
        tokens[_request_id_ctx] = _request_id_ctx.set(request_id)
    if run_id is not None:
        tokens[_run_id_ctx] = _run_id_ctx.set(run_id)
    if trace_id is not None:
        tokens[_trace_id_ctx] = _trace_id_ctx.set(trace_id)
    if tool_name is not None:
        tokens[_tool_name_ctx] = _tool_name_ctx.set(tool_name)

    return ContextToken(tokens)
