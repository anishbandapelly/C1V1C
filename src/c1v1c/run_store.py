"""Immutable run persistence: local JSON (always) and S3 (when enabled and authorised)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel

from c1v1c.config import Settings


def canonical_hash(payload: dict) -> str:
    """Deterministic SHA-256 over a JSON payload with sorted keys."""
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()


class RunStore:
    def __init__(self, settings: Settings | None = None, s3=None):
        self.settings = settings or Settings.load()
        self.dir = Path(self.settings.runs_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.s3 = s3

    def _path(self, kind: str, run_id: str) -> Path:
        if not run_id.replace("-", "").replace("_", "").isalnum():
            raise ValueError("invalid run id")
        return self.dir / kind / f"{run_id}.json"

    def save(self, kind: str, run_id: str, record: BaseModel) -> dict:
        """Write once. An existing identical record is accepted; a different one is refused."""
        path = self._path(kind, run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        body = record.model_dump_json(indent=1)
        if path.exists():
            if json.loads(path.read_text(encoding="utf-8")) != json.loads(body):  # compare content, not key order
                raise FileExistsError(f"run {run_id} already exists with different content; runs are immutable")
        else:
            path.write_text(body, encoding="utf-8")
        ref = {"local_path": str(path.relative_to(self.settings.root)) if path.is_relative_to(self.settings.root) else str(path),
               "sha256": hashlib.sha256(body.encode()).hexdigest(), "s3": None}
        if self.s3 is not None:
            ref["s3"] = self.s3.put_json(f"{self.settings.s3_runs_prefix}{kind}/{run_id}.json", body)
        return ref

    def load(self, kind: str, run_id: str, model: type[BaseModel]) -> BaseModel:
        path = self._path(kind, run_id)
        if path.exists():
            return model.model_validate_json(path.read_text(encoding="utf-8"))
        if self.s3 is not None:
            body = self.s3.get_text(f"{self.settings.s3_runs_prefix}{kind}/{run_id}.json")
            if body is not None:
                return model.model_validate_json(body)
        raise KeyError(f"run {run_id} not found")

    def list(self, kind: str) -> list[str]:
        folder = self.dir / kind
        return sorted(p.stem for p in folder.glob("*.json")) if folder.exists() else []
