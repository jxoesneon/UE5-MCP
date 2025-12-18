import time
import uuid
from datetime import UTC, datetime
from typing import Any, cast

from mcp_protocol import (
    Artifact,
    RunManifest,
    ToolError,
    ToolErrorDetail,
    ToolResult,
)
from pydantic import BaseModel

from ..config.settings import settings
from ..observability import get_logger, set_context
from ..policy import policy_engine
from ..registry import registry
from ..storage import artifact_manager

logger = get_logger(__name__)


class ToolExecutor:
    def execute(
        self,
        tool_name: str,
        input_data: BaseModel | dict[str, Any],
        request_id: str | None = None,
        parent_trace_id: str | None = None,
    ) -> ToolResult | ToolError:
        # 1. Setup Context
        run_id = str(uuid.uuid4())
        req_id = request_id or str(uuid.uuid4())
        trace_id = parent_trace_id or str(uuid.uuid4())

        ctx_token = set_context(
            request_id=req_id,
            run_id=run_id,
            trace_id=trace_id,
            tool_name=tool_name,
        )

        start_time = datetime.now(UTC)
        start_ts = time.time()

        logger.info(f"Starting execution of {tool_name}")

        tool_entry = registry.get_tool(tool_name)

        # Manifest preparation
        manifest = RunManifest(
            run_id=run_id,
            request_id=req_id,
            tool_name=tool_name,
            status="pending",
            start_time=start_time.isoformat(),
            end_time="",  # placeholder
            duration_seconds=0.0,
            inputs={},  # populated later
            config_hash=None,  # TODO: implement config hashing
            tool_version=settings.protocol_version,
        )

        try:
            # 2. Tool Lookup
            if not tool_entry:
                raise ValueError(f"Tool '{tool_name}' not found.")

            # 3. Input Validation
            if isinstance(input_data, dict):
                try:
                    input_model = tool_entry.input_model.model_validate(input_data)
                except Exception as e:
                    error_result = self._create_error(
                        tool_name,
                        req_id,
                        run_id,
                        "VALIDATION_ERROR",
                        f"Input validation failed: {str(e)}",
                    )
                    manifest.status = "error"
                    manifest.error = error_result.error.model_dump(mode="json")
                    return error_result
            else:
                if not isinstance(input_data, tool_entry.input_model):
                    error_result = self._create_error(
                        tool_name,
                        req_id,
                        run_id,
                        "VALIDATION_ERROR",
                        f"Input must be of type {tool_entry.input_model.__name__}",
                    )
                    manifest.status = "error"
                    manifest.error = error_result.error.model_dump(mode="json")
                    return error_result
                input_model = input_data

            # Update manifest inputs
            manifest.inputs = input_model.model_dump(mode="json")

            # 4. Policy Check
            policy_engine.check_tool_allowed(tool_name)

            # 5. Execution
            result_or_error = cast(ToolResult | ToolError, tool_entry.handler(input_model))

            # 6. Result Handling
            end_time = datetime.now(UTC)
            duration = time.time() - start_ts

            manifest.end_time = end_time.isoformat()
            manifest.duration_seconds = duration

            if isinstance(result_or_error, ToolError):
                manifest.status = "error"
                manifest.error = result_or_error.error.model_dump(mode="json")
                # Ensure IDs match context
                result_or_error.run_id = run_id
                result_or_error.request_id = req_id
                
                logger.error(f"Tool execution failed: {result_or_error.error.message}")
                return result_or_error

            # It's a ToolResult
            manifest.status = "success"
            manifest.outputs = result_or_error.result
            
            # Ensure IDs match context
            result_or_error.run_id = run_id
            result_or_error.request_id = req_id

            # 7. Artifact Persistence
            stored_artifacts: list[Artifact] = []
            for art in result_or_error.artifacts:
                stored = artifact_manager.store_artifact(run_id, art)
                stored_artifacts.append(stored)

            result_or_error.artifacts = stored_artifacts
            manifest.artifacts = stored_artifacts

            logger.info("Tool execution successful")
            return result_or_error

        except Exception as e:
            logger.exception("Unexpected error during execution")
            end_time = datetime.now(UTC)
            duration = time.time() - start_ts

            error_result = self._create_error(
                tool_name, req_id, run_id, "INTERNAL_ERROR", str(e)
            )

            manifest.status = "error"
            manifest.end_time = end_time.isoformat()
            manifest.duration_seconds = duration
            manifest.error = error_result.error.model_dump(mode="json")

            return error_result

        finally:
            # 8. Write Manifest
            try:
                artifact_manager.write_run_manifest(manifest)
            except Exception as e:
                logger.error(f"Failed to write run manifest: {e}")

            ctx_token.reset()

    def _create_error(
        self, tool: str, req_id: str, run_id: str, code: str, msg: str
    ) -> ToolError:
        return ToolError(
            tool=tool,
            request_id=req_id,
            run_id=run_id,
            error=ToolErrorDetail(code=code, message=msg),
        )


# Global executor
executor = ToolExecutor()
