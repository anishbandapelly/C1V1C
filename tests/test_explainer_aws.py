"""Decision Explainer grounding and AWS adapter failure handling (all AWS calls are stubbed)."""
import io

import boto3
import pytest
from botocore.exceptions import ReadTimeoutError
from botocore.stub import Stubber

from c1v1c.aws import bedrock
from c1v1c.aws.s3 import FailoverS3, S3Store, S3Unavailable
from c1v1c.aws.status import probe
from c1v1c.config import Settings
from c1v1c.explainer import explain, numbers_supported


@pytest.fixture
def run(engine):
    return engine.run(engine.default_request(budget_inr=12_000_000), use_cache=False)


def names(engine):
    return {z.zone_id: z.name for z in engine.baseline.zones}


def test_explanation_numbers_come_from_the_run(engine, run):
    e = explain(run, names(engine))
    assert e.explanation_source == "deterministic" and e.validation_passed
    assert e.relevant_computed_numbers["capex_inr"] == run.outcome.capex_inr
    assert f"{run.outcome.capex_inr / 1e7:.2f}" in e.headline
    ok, bad = numbers_supported(e.narrative, e)
    assert ok, bad
    assert e.why_rejected == run.rejected
    assert len(e.beneficiaries) == 3 and e.unintended_consequences and e.uncertainties
    assert {a["alternative"] for a in e.alternatives_compared} >= {"No investment"}


def test_invented_numbers_are_rejected(engine, run):
    e = explain(run, names(engine))
    ok, bad = numbers_supported("This plan avoids 98,765 tonnes of carbon and saves INR 4.2 billion.", e)
    assert not ok and "98,765" in bad


def test_infeasible_run_explanation(engine):
    run = engine.run(engine.default_request(budget_inr=6_000_000, committed_counts={"ZA:drainage_upgrade": 1, "ZB:drainage_upgrade": 1}),
                     use_cache=False)
    e = explain(run, names(engine))
    assert e.headline.startswith("No feasible portfolio") and "committed overspend" in " ".join(e.binding_constraints)


def test_shock_findings_flow_into_explanation(engine, run):
    comp = engine.shock(run, "budget_cut", {"budget_factor": 0.4})
    e = explain(run, names(engine), [comp])
    assert e.shock_findings and "Sudden budget cut" in e.shock_findings[0]


def _bedrock_settings(monkeypatch, model="example.model-id"):
    monkeypatch.setenv("C1V1C_OFFLINE_MODE", "false")
    monkeypatch.setenv("BEDROCK_MODEL_ID", model)
    return Settings.load()


def _client():
    return boto3.client("bedrock-runtime", region_name="ap-south-2", aws_access_key_id="testing", aws_secret_access_key="testing")


def test_bedrock_offline_and_unconfigured(engine, run, monkeypatch):
    e = explain(run, names(engine))
    assert "offline" in bedrock.narrate(e, Settings.load()).bedrock_status
    monkeypatch.setenv("C1V1C_OFFLINE_MODE", "false")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "")
    out = bedrock.narrate(e, Settings.load())
    assert out.explanation_source == "deterministic" and "not configured" in out.bedrock_status


def test_bedrock_valid_response_is_accepted(engine, run, monkeypatch):
    s = _bedrock_settings(monkeypatch)
    e = explain(run, names(engine))
    client = _client()
    text = f"The plan spends INR {run.outcome.capex_inr / 1e7:.2f} crore. These are modelled screening estimates."
    with Stubber(client) as st:
        st.add_response("converse", {"output": {"message": {"role": "assistant", "content": [{"text": text}]}},
                                     "stopReason": "end_turn", "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
                                     "metrics": {"latencyMs": 1}})
        out = bedrock.narrate(e, s, client)
    assert out.explanation_source == "bedrock" and out.narrative == text


def test_bedrock_hallucinated_numbers_fall_back(engine, run, monkeypatch):
    s = _bedrock_settings(monkeypatch)
    e = explain(run, names(engine))
    client = _client()
    with Stubber(client) as st:
        st.add_response("converse", {"output": {"message": {"role": "assistant", "content": [{"text": "It prevents 4321 floods."}]}},
                                     "stopReason": "end_turn", "usage": {"inputTokens": 1, "outputTokens": 1, "totalTokens": 2},
                                     "metrics": {"latencyMs": 1}})
        out = bedrock.narrate(e, s, client)
    assert out.explanation_source == "deterministic" and "rejected" in out.bedrock_status and out.narrative == e.narrative


def test_bedrock_access_denied_and_timeout_fall_back(engine, run, monkeypatch):
    s = _bedrock_settings(monkeypatch)
    e = explain(run, names(engine))
    client = _client()
    with Stubber(client) as st:
        st.add_client_error("converse", service_error_code="AccessDeniedException", http_status_code=403)
        out = bedrock.narrate(e, s, client)
    assert out.explanation_source == "deterministic" and "AccessDeniedException" in out.bedrock_status

    class Timeout:
        def converse(self, **_):
            raise ReadTimeoutError(endpoint_url="https://bedrock-runtime.ap-south-2.amazonaws.com")
    out = bedrock.narrate(e, s, Timeout())
    assert out.explanation_source == "deterministic" and "ReadTimeoutError" in out.bedrock_status


def _s3(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "example-bucket")
    client = boto3.client("s3", region_name="ap-south-2", aws_access_key_id="testing", aws_secret_access_key="testing")
    return S3Store(Settings.load(), client), client


def test_s3_put_get_and_permission_failure(monkeypatch):
    store, client = _s3(monkeypatch)
    with Stubber(client) as st:
        st.add_response("put_object", {"VersionId": "v1", "ETag": '"x"'})
        st.add_response("get_object", {"Body": io.BytesIO(b'{"a": 1}')})
        st.add_client_error("put_object", service_error_code="AccessDenied", http_status_code=403)
        ref = store.put_json("runs/x.json", '{"a": 1}')
        assert ref["version_id"] == "v1" and len(ref["sha256"]) == 64
        assert store.get_text("runs/x.json") == '{"a": 1}'
        with pytest.raises(S3Unavailable, match="AccessDenied"):
            store.put_json("runs/y.json", "{}")


def test_s3_failover_keeps_local_run(engine, monkeypatch):
    store, client = _s3(monkeypatch)
    failover = FailoverS3(store)
    with Stubber(client) as st:
        st.add_client_error("put_object", service_error_code="AccessDenied", http_status_code=403)
        engine.store.s3 = failover
        run = engine.run(engine.default_request(budget_inr=3_000_000), use_cache=False)
    assert run.solver_status == "optimal"
    assert failover.last_error and "AccessDenied" in failover.last_error
    assert engine.load_run(run.run_id).run_id == run.run_id  # the local immutable copy exists


def test_s3_requires_bucket(monkeypatch):
    monkeypatch.setenv("S3_BUCKET", "")
    with pytest.raises(S3Unavailable):
        S3Store(Settings.load())


def test_missing_credentials_reported_as_blocked():
    out = probe(Settings.load())
    assert out["credentials"].startswith("BLOCKED") and out["s3"].startswith("BLOCKED") and out["bedrock"].startswith("BLOCKED")
    assert "testing" not in str(out)


def test_cached_runs_are_mirrored_to_s3_once(engine):
    class FakeS3:
        def __init__(self):
            self.objects, self.puts, self.last_error = {}, 0, None

        def put_json(self, key, body):
            self.puts += 1
            self.objects[key] = body
            return {"key": key}

        def get_text(self, key):
            return self.objects.get(key)

    req = engine.default_request(budget_inr=5_000_000)
    run = engine.run(req, use_cache=False)            # stored locally only (no S3 yet)
    fake = FakeS3()
    engine.store.s3 = fake
    engine.run(req)                                    # cache hit -> mirrored
    engine.run(req)                                    # second hit -> no duplicate upload
    key = f"{engine.settings.s3_runs_prefix}runs/{run.run_id}.json"
    assert key in fake.objects and fake.puts == 1
