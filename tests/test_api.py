"""HTTP API contract tests through real requests (FastAPI TestClient) on the synthetic baseline."""
import pytest
from fastapi.testclient import TestClient

from c1v1c import api


@pytest.fixture
def client(engine, monkeypatch):
    monkeypatch.setattr(api, "get_engine", lambda: engine)
    return TestClient(api.app)


def test_health_and_metadata(client):
    r = client.get("/health").json()
    assert r["status"] == "ok" and r["data_mode"] == "synthetic demonstration" and r["offline_mode"] is True
    assert len(client.get("/zones").json()["zones"]) == 3
    assert len(client.get("/candidates").json()) == 12


def test_run_shock_explain_round_trip(client):
    req = client.get("/defaults").json()["request"]
    req["budget_inr"] = 12_000_000
    run = client.post("/runs", json=req).json()
    assert run["solver_status"] == "optimal" and run["allocated_inr"] <= 12_000_000
    assert client.get(f"/runs/{run['run_id']}").json()["run_id"] == run["run_id"]
    comp = client.post(f"/runs/{run['run_id']}/shocks", json={"scenario_id": "budget_cut", "overrides": {"budget_factor": 0.5}}).json()
    assert comp["original_run_id"] == run["run_id"] and comp["c_reoptimised"]["budget_available_inr"] == 6_000_000
    exp = client.get(f"/runs/{run['run_id']}/explanation").json()
    assert exp["explanation_source"] == "deterministic" and exp["run_id"] == run["run_id"]


def test_invalid_requests_are_rejected(client):
    req = client.get("/defaults").json()["request"]
    assert client.post("/runs", json={**req, "budget_inr": -1}).status_code == 422
    assert client.post("/runs", json={**req, "weights": {"F": 1}}).status_code == 422
    assert client.post("/runs", json={**req, "baseline_version": "other"}).status_code == 422
    assert client.get("/runs/run-doesnotexist").status_code == 404
    run = client.post("/runs", json=req).json()
    assert client.post(f"/runs/{run['run_id']}/shocks", json={"scenario_id": "hurricane"}).status_code == 422


def test_aws_status_reports_blocked_without_credentials(client):
    r = client.get("/aws/status").json()
    assert r["credentials"].startswith("BLOCKED")
