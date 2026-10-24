"""Engine facade: baseline -> catalogue -> coefficients -> MILP -> evaluation -> immutable run.

Implements the master plan §8.5 interfaces (run_scenario, load_run, evaluate_portfolio) used
by the Streamlit UI and the HTTP API.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from functools import cached_property

from c1v1c import MODEL_VERSION
from c1v1c.baseline import Baseline, load_baseline
from c1v1c.catalogue import build_candidates, catalog_version, load_interventions, load_parameters, load_scenarios
from c1v1c.config import Settings
from c1v1c.evaluate import Scales, build_coefficients, evaluate_portfolio, reference_scales, surrogate_score
from c1v1c.evidence import Evidence
from c1v1c.optimiser import solve, unit_value
from c1v1c.run_store import RunStore, canonical_hash
from c1v1c.schemas import (
    INTERVENTIONS, METRIC_UNITS, METRICS, WEIGHT_KEYS, Alternative, Candidate, PortfolioOutcome, RunRequest,
    RunResult, ScenarioComparison, ScenarioParams,
)

SENSITIVITY_CASES = (
    ("design storm -10%", {"design_intensity_multiplier": 0.9}),
    ("design storm +10%", {"design_intensity_multiplier": 1.1}),
    ("rainfall availability -20%", {"rainfall_availability_factor": 0.8}),
    ("tree cooling -30%", {"tree_cooling_factor": 0.7}),
)


class Engine:
    def __init__(self, settings: Settings | None = None, baseline: Baseline | None = None, s3=None):
        self.settings = settings or Settings.load()
        self.baseline = baseline or load_baseline()
        self.params = load_parameters()
        self.specs = load_interventions()
        self.scenarios = load_scenarios()
        self.catalog_version = catalog_version()
        if s3 is None and not self.settings.offline_mode and self.settings.s3_bucket:
            from c1v1c.aws.s3 import FailoverS3, S3Store, S3Unavailable
            try:  # online: mirror every immutable run to S3; failures are recorded, never fatal
                s3 = FailoverS3(S3Store(self.settings))
            except S3Unavailable:
                s3 = None
        self.store = RunStore(self.settings, s3)
        self.all_candidates = build_candidates(list(self.baseline.zones), self.specs, self.params)
        self.scales: Scales = reference_scales(self.baseline, self.all_candidates, self.specs, self.params, self.scenarios["normal"])

    # ------------------------------------------------------------------ helpers
    def weights_for(self, mode: str) -> dict[str, float]:
        return dict(zip(WEIGHT_KEYS, self.params.modes[mode]))

    def default_request(self, budget_inr: float = 20_000_000, mode: str = "Balanced", **kw) -> RunRequest:
        return RunRequest(baseline_version=self.baseline.version, project_catalog_version=self.catalog_version,
                          model_version=MODEL_VERSION, budget_inr=budget_inr, weights=self.weights_for(mode),
                          allowed_interventions=INTERVENTIONS, mode=mode, **kw)

    def scenario_for(self, request: RunRequest) -> ScenarioParams:
        base = self.scenarios[request.scenario_id]
        return base.model_copy(update=request.overrides) if request.overrides else base

    def candidates_for(self, request: RunRequest) -> list[Candidate]:
        return build_candidates(list(self.baseline.zones), self.specs, self.params, tuple(request.allowed_interventions))

    def input_hash(self, request: RunRequest) -> str:
        return canonical_hash({"request": request.model_dump(mode="json"), "baseline_sha256": self.baseline.sha256,
                               "catalog": self.catalog_version, "params": self.params.version, "model": MODEL_VERSION})

    @cached_property
    def assumptions(self) -> list[str]:
        out = []
        for p in self.params.values.values():
            if p.evidence in (Evidence.ASSUMED, Evidence.ESTIMATED):
                rng = f" (range {p.low}-{p.high})" if p.low is not None else ""
                out.append(f"[{p.evidence.value}] {p.key} = {p.value} {p.unit}{rng}: {p.source}")
        for s in self.specs.values():
            out.append(f"[{s.evidence.value}] {s.label}: {s.unit_description}, capex INR {s.capex_inr:,.0f}, "
                       f"O&M {s.om_fraction:.0%}/yr of capex; {s.source}")
        out.append(f"Normalisation tau (fixed across portfolios and shocks): "
                   + ", ".join(f"{m}={self.scales.tau[m]:.4g} {METRIC_UNITS[m]}" for m in METRICS)
                   + f"; equity={self.scales.tau_equity:.4g}; cost={self.scales.tau_cost:,.0f} INR (reference budget INR 2 crore)")
        return out

    @cached_property
    def gaps(self) -> list[str]:
        return list(self.baseline.manifest.get("known_gaps", [])) + [
            "Unit costs, O&M, retention depth, tank size and drainage conveyance per unit are master-plan illustrative "
            "assumptions, not Bengaluru-validated engineering estimates.",
            "Existing drainage capacity is not measured; the flood metric counts retained or newly conveyed design-event "
            "runoff and assumes the existing network is at capacity during the design event.",
            "Carbon covers urban-forest sequestration only (IPCC crown-cover default); embodied and avoided-energy "
            "emissions are not estimated.",
            "Heat is a screening exposure index (person-index units), not a temperature forecast.",
        ]

    # ------------------------------------------------------------------ core run
    def run(self, request: RunRequest, *, parent_run_id: str | None = None,
            role: str = "optimised", use_cache: bool = True) -> RunResult:
        if request.baseline_version != self.baseline.version:
            raise ValueError(f"request baseline {request.baseline_version} does not match loaded baseline {self.baseline.version}")
        ih = self.input_hash(request)
        run_id = "run-" + ih[:16]
        if use_cache:
            try:
                cached = self.store.load("runs", run_id, RunResult)
                self.store.mirror("runs", run_id)
                return cached
            except KeyError:
                pass
        scenario = self.scenario_for(request)
        weights = request.weights
        candidates = self.candidates_for(request)
        by_id = {c.candidate_id: c for c in candidates}
        committed = self._committed(request)
        available = math.floor(request.budget_inr * scenario.budget_factor)
        coeffs = build_coefficients(self.baseline, candidates, self.specs, self.params, scenario, self.scales)
        sol = solve(self.baseline, candidates, coeffs, self.scales, weights, available, equity_floor=request.equity_floor,
                    committed=committed, time_limit_s=float(self.params.solver["time_limit_s"]))
        baseline_outcome = evaluate_portfolio(self.baseline, candidates, {}, self.specs, self.params, scenario,
                                              self.scales, weights, available)
        warnings: list[str] = []
        outcome = None
        verification: dict[str, bool] = {}
        alternatives: list[Alternative] = []
        sur = None
        if sol.status in ("optimal", "feasible_time_limit"):
            outcome = evaluate_portfolio(self.baseline, candidates, sol.counts, self.specs, self.params, scenario,
                                         self.scales, weights, available, committed)
            verification = dict(outcome.constraint_checks)
            verification["solver_feasible"] = not outcome.violations
            if outcome.violations:  # never present a violating portfolio as feasible
                warnings.extend(outcome.violations)
                sol.status, sol.message = "error", "Independent verification rejected the solver output: " + "; ".join(outcome.violations)
                outcome = None
            else:
                sur = surrogate_score(sol.counts, coeffs, self.scales, weights)
                if abs(sur - outcome.score) > 1e-6:
                    warnings.append(f"Surrogate score {sur:.4f} differs from evaluated score {outcome.score:.4f} because "
                                    "physical caps bind in the independent evaluation.")
                alternatives = self._alternatives(request, scenario, candidates, coeffs, weights, available, committed, sol.counts)
        counts = sol.counts if outcome is not None else {}
        capex_by_type = {t: sum(by_id[k].capex_inr * n for k, n in counts.items() if by_id[k].intervention_type == t) for t in INTERVENTIONS}
        capex_by_zone = {z.zone_id: sum(by_id[k].capex_inr * n for k, n in counts.items() if by_id[k].zone_id == z.zone_id)
                         for z in self.baseline.zones}
        allocated = sum(capex_by_type.values())
        raw = {}
        if outcome is not None:
            for m in METRICS:
                raw[m] = {"value": outcome.metrics[m], "unit": METRIC_UNITS[m], "baseline": 0.0,
                          "evidence": "modelled with assumed coefficients"}
            raw["LCC"] = {"value": outcome.lcc_inr, "unit": "INR (10-yr lifecycle, 5% real discount)"}
            raw["capex"] = {"value": outcome.capex_inr, "unit": "INR"}
        norm = dict(outcome.normalised) if outcome else {}
        contrib = {}
        if outcome:
            contrib = {m: weights[m] * norm[m] for m in METRICS}
            contrib["Equity"] = weights["Equity"] * norm["Equity"]
            contrib["LCC"] = -weights["LCC"] * norm["LCC"]
        result = RunResult(
            run_id=run_id, input_hash=ih, created_at_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            request=request, data_mode=self.baseline.data_mode, baseline_version=self.baseline.version,
            baseline_sha256=self.baseline.sha256, model_version=MODEL_VERSION, catalog_version=self.catalog_version,
            scenario=scenario, solver_status=sol.status, solver_message=sol.message, solver_runtime_s=round(sol.runtime_s, 4),
            budget_available_inr=available,
            committed_capex_inr=sum(by_id[k].capex_inr * n for k, n in committed.items() if k in by_id),
            selected_candidate_counts=counts, capex_by_intervention=capex_by_type, capex_by_zone=capex_by_zone,
            allocated_inr=allocated, unallocated_inr=available - allocated, raw_objectives_with_units=raw,
            normalised_components=norm, score_contributions=contrib, surrogate_score=sur,
            evaluated_score=outcome.score if outcome else None, constraint_slack=sol.slack,
            binding_constraints=sol.binding if outcome else sol.diagnosis,
            rejected=self._rejected(candidates, counts, coeffs, weights, available, sol.binding),
            outcome=outcome, baseline_outcome=baseline_outcome, alternatives=alternatives,
            outcomes_by_zone=outcome.by_zone if outcome else {}, verification=verification,
            assumptions=self.assumptions, gaps=self.gaps,
            source_ids=sorted(set(self.baseline.provenance["source_id"].astype(str)) | {"CFG_INTERVENTIONS", "CFG_PARAMETERS", "CFG_SCENARIOS"}),
            warnings=warnings, parent_run_id=parent_run_id, comparison_role=role,
        )
        try:
            stored = self.store.load("runs", run_id, RunResult)
        except KeyError:
            self.store.save("runs", run_id, result)
            return result
        # Replay: identical inputs must reproduce the stored record exactly (apart from timing metadata).
        fresh, old = result.model_dump(mode="json"), stored.model_dump(mode="json")
        for meta in ("created_at_utc", "solver_runtime_s"):
            fresh.pop(meta), old.pop(meta)
        if fresh != old:
            diff = sorted(k for k in fresh if fresh[k] != old.get(k))
            raise RuntimeError(f"run {run_id} is not reproducible: fields {diff} differ from the stored record")
        self.store.mirror("runs", run_id)
        return stored

    def _committed(self, request: RunRequest) -> dict[str, int]:
        committed = dict(request.committed_counts)
        for k in request.committed_candidate_ids:
            committed.setdefault(k, 1)
        return committed

    def _alternatives(self, request, scenario, candidates, coeffs, weights, available, committed, best) -> list[Alternative]:
        alts: list[Alternative] = []
        seen = [dict(best)]

        def add(aid, label, method, counts, note=""):
            if any(dict(counts) == s for s in seen) and method != "baseline":
                return
            out = evaluate_portfolio(self.baseline, candidates, counts, self.specs, self.params, scenario, self.scales,
                                     weights, available, committed)
            alts.append(Alternative(alternative_id=aid, label=label, method=method, counts=counts, outcome=out,
                                    feasible=not out.violations, note=note))
            seen.append(dict(counts))

        n_alt = int(self.params.solver["alternatives"])
        dist = int(self.params.solver["min_alternative_distance_units"])
        excluded = [dict(best)]
        for i in range(n_alt):
            sol = solve(self.baseline, candidates, coeffs, self.scales, weights, available, equity_floor=request.equity_floor,
                        committed=committed, exclude_solutions=excluded, min_distance=dist,
                        time_limit_s=float(self.params.solver["time_limit_s"]))
            if sol.status not in ("optimal", "feasible_time_limit"):
                break
            excluded.append(sol.counts)
            add(f"next-best-{i + 1}", f"Next-best feasible plan #{i + 1}", "milp_no_good_cut", sol.counts,
                f"Best plan differing by at least {dist} units from every better plan")
        for mode in self.params.modes:
            mw = self.weights_for(mode)
            if all(abs(mw[k] - weights[k]) < 1e-9 for k in WEIGHT_KEYS):
                continue
            mco = build_coefficients(self.baseline, candidates, self.specs, self.params, scenario, self.scales)
            sol = solve(self.baseline, candidates, mco, self.scales, mw, available, equity_floor=request.equity_floor,
                        committed=committed, time_limit_s=float(self.params.solver["time_limit_s"]))
            if sol.status in ("optimal", "feasible_time_limit"):
                add(f"mode-{mode}", f"{mode} optimum", "milp_mode_preset", sol.counts,
                    f"Optimal under {mode} weights, scored here under the requested weights")
        add("baseline-none", "No investment", "baseline", {}, "Same horizon and evaluator; zero spend")
        eq = self._equal_spend(candidates, available, committed)
        add("baseline-equal-spend", "Equal-spend conventional plan", "baseline", eq,
            "Budget split equally across the selected intervention types, units spread across zones")
        return alts

    def _equal_spend(self, candidates: list[Candidate], available: float, committed: dict[str, int]) -> dict[str, int]:
        """Conventional heuristic baseline: equal capital per selected type, round-robin over zones, respecting caps."""
        by_type = {t: [c for c in candidates if c.intervention_type == t and c.upper_bound > 0] for t in INTERVENTIONS}
        by_type = {t: cs for t, cs in by_type.items() if cs}
        counts = dict(committed)
        spent = sum(next(c.capex_inr for c in candidates if c.candidate_id == k) * n for k, n in committed.items())
        if not by_type:
            return counts
        share = max(0.0, available - spent) / len(by_type)
        roof = {z.zone_id: float(z.eligible_roof_m2.value or 0) for z in self.baseline.zones}
        land = {z.zone_id: float(z.plantable_land_m2.value or 0) for z in self.baseline.zones}
        for k, n in committed.items():
            c = next(c for c in candidates if c.candidate_id == k)
            roof[c.zone_id] -= c.roof_m2 * n
            land[c.zone_id] -= c.land_m2 * n
        for t, cs in by_type.items():
            budget_t, i, stalled = share, 0, 0
            while stalled < len(cs):
                c = cs[i % len(cs)]
                i += 1
                ok = (c.capex_inr <= budget_t and counts.get(c.candidate_id, 0) < c.upper_bound
                      and roof[c.zone_id] >= c.roof_m2 and land[c.zone_id] >= c.land_m2)
                if ok:
                    counts[c.candidate_id] = counts.get(c.candidate_id, 0) + 1
                    budget_t -= c.capex_inr
                    roof[c.zone_id] -= c.roof_m2
                    land[c.zone_id] -= c.land_m2
                    stalled = 0
                else:
                    stalled += 1
        return {k: n for k, n in counts.items() if n > 0}

    def _rejected(self, candidates, counts, coeffs, weights, available, binding) -> dict[str, str]:
        out = {}
        chosen_vals = [unit_value(k, coeffs, self.scales, weights) / max(coeffs.capex[k], 1) for k in counts]
        floor_val = min(chosen_vals) if chosen_vals else None
        spent = sum(coeffs.capex[k] * n for k, n in counts.items())
        for c in candidates:
            k = c.candidate_id
            n = counts.get(k, 0)
            if c.eligibility != "eligible":
                out[k] = f"Not considered: {c.eligibility_reason}."
                continue
            if n >= c.upper_bound:
                continue
            v = unit_value(k, coeffs, self.scales, weights)
            per_crore = v / c.capex_inr * 1e7
            if v <= 0:
                out[k] = (f"Each unit lowers the weighted score ({v:+.4f}): its lifecycle-cost penalty outweighs the weighted "
                          f"benefit under the current priorities.")
            elif c.capex_inr > available - spent + 1e-6:
                lead = "Partly selected; further units" if n else "Not selected:"
                out[k] = (f"{lead} would need INR {c.capex_inr:,.0f} but only INR {available - spent:,.0f} remains unallocated "
                          f"(score {per_crore:.4f} per crore).")
            elif any(b.startswith(("roof:", "land:")) and b.endswith(c.zone_id) for b in binding) and (c.roof_m2 or c.land_m2):
                out[k] = f"Eligible {'roof' if c.roof_m2 else 'land'} area in {c.zone_id} is already used by higher-scoring units."
            elif floor_val is not None and per_crore < floor_val * 1e7:
                out[k] = (f"Lower score per crore ({per_crore:.4f}) than the selected projects (lowest selected "
                          f"{floor_val * 1e7:.4f}); the budget is better spent elsewhere.")
            else:
                out[k] = f"Not selected by the optimiser; score {per_crore:.4f} per crore."
        return out

    # ------------------------------------------------------------------ scenarios
    def evaluate_counts(self, counts: dict[str, int], request: RunRequest, scenario: ScenarioParams,
                        committed: dict[str, int] | None = None) -> PortfolioOutcome:
        candidates = self.candidates_for(request.model_copy(update={"allowed_interventions": INTERVENTIONS}))
        available = math.floor(request.budget_inr * scenario.budget_factor)
        return evaluate_portfolio(self.baseline, candidates, counts, self.specs, self.params, scenario, self.scales,
                                  request.weights, available, committed)

    def shock(self, original: RunResult, scenario_id: str, overrides: dict[str, float] | None = None,
              committed_counts: dict[str, int] | None = None) -> ScenarioComparison:
        """A: original under normal; B: unchanged original under shock; C: fresh re-optimisation under shock."""
        if original.outcome is None:
            raise ValueError("the original run has no feasible portfolio to stress-test")
        overrides = overrides or {}
        committed_counts = {k: v for k, v in (committed_counts or {}).items() if v > 0}
        for k, n in committed_counts.items():
            if original.selected_candidate_counts.get(k, 0) < n:
                raise ValueError(f"commitment {k} x{n} is not part of the original portfolio")
        shock_req = original.request.model_copy(update={"scenario_id": scenario_id, "overrides": overrides,
                                                         "committed_counts": committed_counts, "committed_candidate_ids": ()})
        RunRequest.model_validate(shock_req.model_dump())
        scenario = self.scenario_for(shock_req)
        normal = self.scenarios["normal"]
        a = self.evaluate_counts(original.selected_candidate_counts, original.request, normal)
        b = self.evaluate_counts(original.selected_candidate_counts, shock_req, scenario, committed_counts)
        notes = []
        if not b.constraint_checks["budget"]:
            notes.append(f"The unchanged plan costs INR {b.capex_inr:,.0f}, above the revised envelope of "
                         f"INR {math.floor(shock_req.budget_inr * scenario.budget_factor):,.0f}: it is no longer affordable.")
        c = self.run(shock_req, parent_run_id=original.run_id, role="reoptimised_under_shock")
        c_counts = c.selected_candidate_counts
        keys = sorted(set(c_counts) | set(original.selected_candidate_counts))  # stable order across processes
        additions = {k: c_counts.get(k, 0) - original.selected_candidate_counts.get(k, 0) for k in keys
                     if c_counts.get(k, 0) > original.selected_candidate_counts.get(k, 0)}
        removals = {k: original.selected_candidate_counts.get(k, 0) - c_counts.get(k, 0) for k in keys
                    if c_counts.get(k, 0) < original.selected_candidate_counts.get(k, 0)}
        deltas = {}
        for m in METRICS:
            av, bv = a.metrics[m], b.metrics[m]
            cv = c.outcome.metrics[m] if c.outcome else None
            deltas[m] = {"A": av, "B": bv, "C": cv, "B_minus_A": None if av is None or bv is None else bv - av,
                         "C_minus_B": None if cv is None or bv is None else cv - bv}
        def residual(o):
            return None if o is None else sum(z["residual_runoff_m3"] for z in o.by_zone.values())
        deltas["residual_runoff_m3"] = {"A": residual(a), "B": residual(b), "C": residual(c.outcome)}
        deltas["capex_inr"] = {"A": a.capex_inr, "B": b.capex_inr, "C": c.outcome.capex_inr if c.outcome else None}
        deltas["score"] = {"A": a.score, "B": b.score, "C": c.evaluated_score}
        deltas["equity_gain"] = {"A": a.equity_gain, "B": b.equity_gain, "C": c.outcome.equity_gain if c.outcome else None}
        sens = self._sensitivity(original, c, scenario, shock_req)
        cid = "cmp-" + canonical_hash({"orig": original.run_id, "c": c.run_id})[:16]
        comp = ScenarioComparison(comparison_id=cid, scenario=scenario, original_run_id=original.run_id,
                                  a_original_normal=a, b_original_under_shock=b, b_feasible=not b.violations,
                                  b_notes=notes + [v for v in b.violations if not v.startswith("capital ")],
                                  c_reoptimised=c, additions=additions, removals=removals, deltas=deltas, sensitivity=sens)
        self.store.save("comparisons", cid, comp)
        return comp

    def _sensitivity(self, original: RunResult, c: RunResult, scenario: ScenarioParams, req: RunRequest) -> dict:
        """Score range of each plan across disclosed perturbations (sensitivity ranges, not confidence intervals)."""
        plans = {"original": original.selected_candidate_counts}
        if c.outcome is not None:
            plans["reoptimised"] = c.selected_candidate_counts
        scores: dict[str, list[float]] = {p: [] for p in plans}
        for _, delta in SENSITIVITY_CASES:
            update = {}
            for key, factor in delta.items():
                update[key] = min(getattr(scenario, key) * factor, 1.0) if key == "tree_cooling_factor" else getattr(scenario, key) * factor
            sc = scenario.model_copy(update=update)
            for p, counts in plans.items():
                scores[p].append(self.evaluate_counts(counts, req, sc).score)
        out = {}
        for p, vals in scores.items():
            out[p] = {"min": min(vals), "mean": sum(vals) / len(vals), "max": max(vals), "cases": len(vals)}
        if "reoptimised" in scores:
            out["max_regret_of_original"] = {"value": max(r - o for r, o in zip(scores["reoptimised"], scores["original"]))}
        return out

    def load_run(self, run_id: str) -> RunResult:
        return self.store.load("runs", run_id, RunResult)
