"""HTTP API over the engine (FastAPI). Same contracts as the Streamlit UI.

Run locally:  uvicorn c1v1c.api:app --port 8000
"""
from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from c1v1c import MODEL_VERSION
from c1v1c.baseline import BaselineUnavailable
from c1v1c.engine import Engine
from c1v1c.explainer import explain
from c1v1c.schemas import DecisionExplanation, RunRequest, RunResult, ScenarioComparison

app = FastAPI(title="C1V1C - Tulabhara AI decision engine", version=MODEL_VERSION)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return Engine()


def _engine() -> Engine:
    try:
        return get_engine()
    except BaselineUnavailable as exc:
        raise HTTPException(status_code=503, detail=f"baseline unavailable: {exc}") from None


class ShockRequest(BaseModel):
    scenario_id: str = Field(pattern="^(normal|extreme_rain|drought|budget_cut)$")
    overrides: dict[str, float] = Field(default_factory=dict)
    committed_counts: dict[str, int] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict:
    try:
        e = get_engine()
    except BaselineUnavailable as exc:
        return {"status": "degraded", "detail": str(exc), "model_version": MODEL_VERSION}
    return {"status": "ok", "model_version": MODEL_VERSION, "baseline_version": e.baseline.version,
            "baseline_sha256": e.baseline.sha256, "data_mode": e.baseline.data_mode.value, "catalog_version": e.catalog_version,
            "offline_mode": e.settings.offline_mode,
            "s3_runs": ("disabled" if e.store.s3 is None else f"error: {e.store.s3.last_error}" if e.store.s3.last_error else "enabled"),
            "bedrock_model_configured": bool(e.settings.bedrock_model_id)}


@app.get("/zones")
def zones() -> dict:
    e = _engine()
    return {"baseline_version": e.baseline.version, "zones": [z.model_dump(mode="json") for z in e.baseline.zones],
            "geojson": e.baseline.geojson}


@app.get("/candidates")
def candidates() -> list[dict]:
    return [c.model_dump(mode="json") for c in _engine().all_candidates]


@app.get("/defaults")
def defaults() -> dict:
    e = _engine()
    return {"request": e.default_request().model_dump(mode="json"), "priority_modes": e.params.modes,
            "scenarios": {k: v.model_dump(mode="json") for k, v in e.scenarios.items()}}


@app.post("/runs", response_model=RunResult)
def create_run(request: RunRequest) -> RunResult:
    e = _engine()
    try:
        return e.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@app.get("/runs/{run_id}", response_model=RunResult)
def get_run(run_id: str) -> RunResult:
    try:
        return _engine().load_run(run_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="run not found") from None


@app.post("/runs/{run_id}/shocks", response_model=ScenarioComparison)
def shock(run_id: str, body: ShockRequest) -> ScenarioComparison:
    e = _engine()
    original = get_run(run_id)
    try:
        return e.shock(original, body.scenario_id, body.overrides, body.committed_counts)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@app.get("/runs/{run_id}/explanation", response_model=DecisionExplanation)
def explanation(run_id: str, narrate: bool = False) -> DecisionExplanation:
    e = _engine()
    run = get_run(run_id)
    exp = explain(run, {z.zone_id: z.name for z in e.baseline.zones})
    if narrate:
        from c1v1c.aws.bedrock import narrate as bedrock_narrate
        exp = bedrock_narrate(exp, e.settings)
    return exp


@app.get("/aws/status")
def aws_status() -> dict:
    from c1v1c.aws.status import probe
    return probe()
