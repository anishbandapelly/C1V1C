import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "src"), str(ROOT / "tests")]

from c1v1c.baseline import _load  # noqa: E402
from c1v1c.config import Settings  # noqa: E402
from c1v1c.engine import Engine  # noqa: E402
from synthetic_baseline import build  # noqa: E402

REAL_BASELINE = ROOT / "data" / "curated" / "bengaluru_pilot_v1"
RAW = ROOT / "data" / "raw" / "drive"
requires_real = pytest.mark.skipif(not (REAL_BASELINE / "baseline_manifest.json").exists(),
                                   reason="curated Bengaluru baseline not built (run the data pipeline)")
requires_raw = pytest.mark.skipif(not (RAW / "raw/boundaries/gba-369-wards-december-2025.kml").exists(),
                                  reason="raw Drive dataset not downloaded")


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Every test writes runs to its own folder and never touches AWS unless it stubs a client."""
    monkeypatch.setenv("C1V1C_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("C1V1C_OFFLINE_MODE", "true")
    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN", "AWS_PROFILE"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", str(tmp_path / "no-credentials"))
    monkeypatch.setenv("AWS_CONFIG_FILE", str(tmp_path / "no-config"))
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    yield


@pytest.fixture
def synthetic_dir(tmp_path):
    return build(tmp_path / "synthetic_baseline")


@pytest.fixture
def engine(synthetic_dir):
    _load.cache_clear()
    from c1v1c.baseline import load_baseline
    return Engine(Settings.load(), baseline=load_baseline(synthetic_dir))


@pytest.fixture
def real_engine():
    if not (REAL_BASELINE / "baseline_manifest.json").exists():
        pytest.skip("curated Bengaluru baseline not built")
    _load.cache_clear()
    from c1v1c.baseline import load_baseline
    return Engine(Settings.load(), baseline=load_baseline(REAL_BASELINE))


def pytest_configure(config):
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
