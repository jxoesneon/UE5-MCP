from pathlib import Path

from mcp_protocol import Artifact, RunManifest

from ..config.settings import settings


class ArtifactManager:
    def __init__(self, root_path: Path | None = None):
        self.root = root_path or settings.artifacts.root
        self.write_manifests = settings.artifacts.write_manifests

    def ensure_run_dir(self, run_id: str) -> Path:
        """Ensure the directory for a specific run exists."""
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def store_artifact(self, run_id: str, artifact: Artifact) -> Artifact:
        """
        Store an artifact's content to disk if it has content, and update its URI.
        Returns the updated artifact (with URI set if stored).
        """
        if not artifact.content:
            return artifact

        run_dir = self.ensure_run_dir(run_id)
        
        # Determine filename. Use a sanitized name from metadata or default.
        filename = "artifact"
        if artifact.metadata and "filename" in artifact.metadata:
            filename = artifact.metadata["filename"]
        elif artifact.uri:
            # If URI is already set (e.g. input path), use basename
            filename = Path(artifact.uri).name
        
        # Simple sanitization
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        # Avoid collisions? For now, simplistic overwrite or append timestamp could work.
        # Let's trust the tool provided a unique name or accept overwrite.
        
        file_path = run_dir / filename
        
        # Write content
        # Assuming content is text for now as per Artifact model (str | None)
        # If we handle binary, we might need to change model or encode as base64
        file_path.write_text(artifact.content, encoding="utf-8")
        
        # Update artifact to reference the file URI
        return artifact.model_copy(update={"uri": str(file_path), "content": None})

    def write_run_manifest(self, manifest: RunManifest) -> Path | None:
        """Write the run manifest to the run directory."""
        if not self.write_manifests:
            return None

        run_dir = self.ensure_run_dir(manifest.run_id)
        manifest_path = run_dir / "run_manifest.json"
        
        manifest_json = manifest.model_dump_json(indent=2)
        manifest_path.write_text(manifest_json, encoding="utf-8")
        
        return manifest_path

    def get_run_dir(self, run_id: str) -> Path:
        return self.root / run_id

# Global artifact manager
artifact_manager = ArtifactManager()
