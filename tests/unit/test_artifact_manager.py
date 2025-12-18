import json
from pathlib import Path

import pytest
from mcp_core.storage.artifact_manager import ArtifactManager
from mcp_protocol import Artifact, RunManifest


@pytest.fixture
def artifact_manager(tmp_path):
    return ArtifactManager(root_path=tmp_path)

def test_ensure_run_dir(artifact_manager, tmp_path):
    run_id = "test-run-1"
    run_dir = artifact_manager.ensure_run_dir(run_id)

    assert run_dir.exists()
    assert run_dir.is_dir()
    assert run_dir == tmp_path / run_id

def test_store_artifact_text(artifact_manager, tmp_path):
    run_id = "test-run-2"
    artifact = Artifact(type="text/plain", content="Hello World", metadata={"filename": "hello.txt"})

    stored = artifact_manager.store_artifact(run_id, artifact)

    assert stored.content is None
    assert stored.uri is not None

    file_path = Path(stored.uri)
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == "Hello World"
    assert file_path.parent.name == run_id

def test_store_artifact_no_content(artifact_manager):
    run_id = "test-run-3"
    artifact = Artifact(type="text/plain", uri="/some/path")

    stored = artifact_manager.store_artifact(run_id, artifact)

    assert stored == artifact # Should be unchanged

def test_write_run_manifest(artifact_manager, tmp_path):
    run_id = "test-run-4"
    manifest = RunManifest(
        run_id=run_id,
        request_id="req-1",
        tool_name="test.tool",
        status="success",
        start_time="2023-01-01T00:00:00Z",
        end_time="2023-01-01T00:00:01Z",
        duration_seconds=1.0,
        inputs={"foo": "bar"}
    )

    manifest_path = artifact_manager.write_run_manifest(manifest)

    assert manifest_path is not None
    assert manifest_path.exists()

    content = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert content["run_id"] == run_id
    assert content["inputs"]["foo"] == "bar"
