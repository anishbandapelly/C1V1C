"""Runtime settings. Paths are repository-relative; secrets never live here."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Repository root (config/, data/). Override with C1V1C_ROOT when the package is installed elsewhere.
ROOT = Path(os.environ.get("C1V1C_ROOT") or Path(__file__).resolve().parents[2])


def _load_dotenv(path: Path) -> None:
    """Load non-secret KEY=VALUE pairs from an ignored local .env without overriding the environment."""
    if not path.exists() or os.environ.get("C1V1C_SKIP_DOTENV") == "1":
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def _flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    return default if raw is None or raw == "" else raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    root: Path
    raw_dir: Path
    curated_dir: Path
    config_dir: Path
    runs_dir: Path
    aws_region: str
    s3_bucket: str
    s3_curated_prefix: str
    s3_runs_prefix: str
    bedrock_model_id: str
    offline_mode: bool
    baseline_version: str
    model_version: str
    aws_timeout_s: float

    @classmethod
    def load(cls) -> "Settings":
        _load_dotenv(ROOT / ".env")
        from c1v1c import MODEL_VERSION

        env = os.environ.get
        return cls(
            root=ROOT,
            raw_dir=Path(env("C1V1C_RAW_DIR", ROOT / "data" / "raw" / "drive")),
            curated_dir=Path(env("C1V1C_CURATED_DIR", ROOT / "data" / "curated")),
            config_dir=ROOT / "config",
            runs_dir=Path(env("C1V1C_RUNS_DIR", ROOT / "runs")),
            aws_region=env("AWS_REGION", "ap-south-2"),
            s3_bucket=env("S3_BUCKET", ""),
            s3_curated_prefix=env("S3_CURATED_PREFIX", "input/curated/"),
            s3_runs_prefix=env("S3_RUNS_PREFIX", "runs/"),
            bedrock_model_id=env("BEDROCK_MODEL_ID", ""),
            offline_mode=_flag("C1V1C_OFFLINE_MODE", True),
            baseline_version=env("C1V1C_BASELINE_VERSION", "bengaluru_pilot_v1"),
            model_version=MODEL_VERSION,
            aws_timeout_s=float(env("C1V1C_AWS_TIMEOUT_S", "8")),
        )
