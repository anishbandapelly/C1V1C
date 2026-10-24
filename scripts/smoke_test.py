"""Post-deployment smoke test against a running deployment (Streamlit UI + HTTP API).

Usage: python scripts/smoke_test.py [--ui http://localhost:8501] [--api http://localhost:8000]
Exits non-zero on any failure. Never prints credentials; checks responses for credential-like strings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request

SECRET = re.compile(r"(AKIA[0-9A-Z]{16}|aws_secret_access_key|AWS_SECRET_ACCESS_KEY\s*=)")


def http(method: str, url: str, body: dict | None = None, timeout: float = 60) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ui", default="http://localhost:8501")
    ap.add_argument("--api", default="http://localhost:8000")
    a = ap.parse_args()
    results = []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}{' - ' + detail if detail else ''}", flush=True)

    for _ in range(60):  # wait for startup
        try:
            if http("GET", a.ui + "/_stcore/health", timeout=5)[1] == "ok" and http("GET", a.api + "/health", timeout=5)[0] == 200:
                break
        except Exception:
            pass
        time.sleep(2)
    s, body = http("GET", a.ui + "/_stcore/health")
    check("UI health endpoint", s == 200 and body == "ok", body)
    s, page = http("GET", a.ui + "/")
    check("UI page served", s == 200 and ("<title>" in page.lower() or "streamlit" in page.lower()), f"HTTP {s}")
    s, body = http("GET", a.api + "/health")
    h = json.loads(body)
    check("API health and baseline loaded", s == 200 and h.get("status") == "ok",
          f"{h.get('baseline_version')} · {h.get('data_mode')} · model {h.get('model_version')}")
    zones = json.loads(http("GET", a.api + "/zones")[1])["zones"]
    check("Real pilot zones served", len(zones) == 3 and all(z["gba_zone_name"] == "Yelahanka" for z in zones),
          ", ".join(z["name"] for z in zones))
    req = json.loads(http("GET", a.api + "/defaults")[1])["request"]
    t = time.perf_counter()
    s, body = http("POST", a.api + "/runs", req)
    run = json.loads(body)
    check("Solver executes in the deployment", s == 200 and run["solver_status"] == "optimal" and all(run["verification"].values()),
          f"{run.get('run_id')} · {run.get('solver_status')} · INR {run.get('allocated_inr', 0):,.0f} of "
          f"{run.get('budget_available_inr', 0):,.0f} · {time.perf_counter() - t:.1f}s")
    check("Budget respected", run["allocated_inr"] <= run["budget_available_inr"])
    s, body = http("GET", f"{a.api}/runs/{run['run_id']}")
    check("Saved run retrievable", s == 200 and json.loads(body)["input_hash"] == run["input_hash"])
    for sc in ("extreme_rain", "drought", "budget_cut"):
        s, body = http("POST", f"{a.api}/runs/{run['run_id']}/shocks", {"scenario_id": sc})
        comp = json.loads(body)
        check(f"Shock {sc}: A/B/C computed", s == 200 and comp["c_reoptimised"]["run_id"] != run["run_id"],
              f"B feasible={comp.get('b_feasible')} · C {comp['c_reoptimised']['solver_status']}" if s == 200 else body[:200])
    s, body = http("GET", f"{a.api}/runs/{run['run_id']}/explanation?narrate=true")
    exp = json.loads(body)
    check("Explanation with honest Bedrock status", s == 200 and exp["validation_passed"] and exp["bedrock_status"],
          f"source={exp.get('explanation_source')} · {exp.get('bedrock_status')}")
    s, body = http("POST", a.api + "/runs", {**req, "budget_inr": -1})
    check("Invalid input rejected", s == 422, f"HTTP {s}")
    infeasible = {**req, "budget_inr": 6_000_000, "committed_counts": {f"{zones[0]['zone_id']}:drainage_upgrade": 1,
                                                                       f"{zones[1]['zone_id']}:drainage_upgrade": 1}}
    s, body = http("POST", a.api + "/runs", infeasible)
    inf = json.loads(body)
    check("Infeasible request reported honestly", s == 200 and inf["solver_status"] == "infeasible" and inf["outcome"] is None,
          "; ".join(inf.get("binding_constraints", []))[:160])
    s, body = http("GET", a.api + "/aws/status")
    aws = json.loads(body)
    check("AWS status probe answers", s == 200, json.dumps({k: v for k, v in aws.items() if k in ("credentials", "s3", "bedrock")}))
    check("No credential material in responses", not any(SECRET.search(x) for x in (body, json.dumps(run), json.dumps(exp))))
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} smoke checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
