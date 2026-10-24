"""Load declared assumptions (config/) and build the candidate catalogue for a baseline."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from c1v1c.config import ROOT
from c1v1c.evidence import Evidence
from c1v1c.models.cost import lifecycle_cost_inr
from c1v1c.schemas import INTERVENTIONS, Candidate, InterventionSpec, ScenarioParams, ZoneBaseline

CONFIG = ROOT / "config"


@dataclass(frozen=True)
class Parameter:
    key: str
    value: object
    unit: str
    evidence: Evidence
    source: str
    low: float | None = None
    high: float | None = None


@dataclass(frozen=True)
class ModelParameters:
    version: str
    values: dict[str, Parameter]
    modes: dict[str, tuple[float, ...]]
    solver: dict

    def __getitem__(self, key: str):
        return self.values[key].value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=4)
def load_parameters(path: Path = CONFIG / "model_parameters.json") -> ModelParameters:
    raw = json.loads(path.read_text(encoding="utf-8"))
    values = {
        k: Parameter(k, v["value"], v["unit"], Evidence(v["evidence"]), v["source"], v.get("low"), v.get("high"))
        for k, v in raw["parameters"].items()
    }
    modes = {k: tuple(v) for k, v in raw["priority_modes"].items() if k != "note"}
    for name, w in modes.items():
        if len(w) != 6 or abs(sum(w) - 1) > 1e-9 or min(w) < 0:
            raise ValueError(f"priority mode {name} must have six non-negative weights summing to 1")
    return ModelParameters(raw["version"], values, modes, raw["solver"])


@lru_cache(maxsize=4)
def load_interventions(path: Path = CONFIG / "intervention_assumptions.csv") -> dict[str, InterventionSpec]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    specs = {}
    for r in rows:
        specs[r["intervention_type"]] = InterventionSpec(
            intervention_type=r["intervention_type"],
            label=r["label"],
            unit_description=r["unit_description"],
            capex_inr=float(r["capex_inr"]),
            om_fraction=float(r["om_fraction_of_capex_per_year"]),
            roof_m2=float(r["roof_m2"]),
            land_m2=float(r["land_m2"]),
            tank_capacity_m3=float(r["tank_capacity_m3"]),
            retention_depth_mm=float(r["retention_depth_mm"]),
            irrigation_m3_month=float(r["irrigation_m3_month"]),
            drainage_capacity_delta_m3_s=float(r["drainage_capacity_delta_m3_s"]),
            max_units_per_zone=int(r["max_units_per_zone"]),
            evidence=Evidence(r["capex_evidence"]),
            source=r["capex_source"],
            notes=r["notes"],
        )
    if set(specs) != set(INTERVENTIONS):
        raise ValueError("intervention catalogue must define exactly the four mandatory interventions")
    return specs


@lru_cache(maxsize=4)
def load_scenarios(path: Path = CONFIG / "scenarios.csv") -> dict[str, ScenarioParams]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {
        r["scenario_id"]: ScenarioParams(
            scenario_id=r["scenario_id"],
            name=r["scenario_name"],
            design_intensity_multiplier=float(r["rainfall_multiplier"]),
            rainfall_availability_factor=float(r["rainfall_availability_factor"]),
            tree_cooling_factor=float(r["tree_cooling_factor"]),
            budget_factor=float(r["budget_factor"]),
            classification=r["classification"],
            source=r["source"],
        )
        for r in rows
    }


def catalog_version() -> str:
    """Content hash of the declared assumption files (changes whenever any assumption changes)."""
    digest = hashlib.sha256()
    for name in ("intervention_assumptions.csv", "model_parameters.json", "scenarios.csv"):
        digest.update(_sha(CONFIG / name).encode())
    return "catalog-" + digest.hexdigest()[:12]


def build_candidates(zones: list[ZoneBaseline], specs: dict[str, InterventionSpec], params: ModelParameters,
                     allowed: tuple[str, ...] = INTERVENTIONS) -> list[Candidate]:
    """One integer decision variable per (zone, intervention). Upper bounds come from
    physical capacity (roof, land) and the programme cap; missing capacity is NOT_ESTIMABLE."""
    rate, years = params["discount_rate"], params["lcc_horizon_y"]
    out = []
    for z in zones:
        for t in INTERVENTIONS:
            s = specs[t]
            ub, status, reason = s.max_units_per_zone, "eligible", "within programme cap"
            caps = []
            if s.roof_m2 > 0:
                roof = z.eligible_roof_m2.value
                if roof is None:
                    status, reason, ub = "not_estimable", "eligible roof area not estimable from current evidence", 0
                else:
                    caps.append(math.floor(roof / s.roof_m2))
            if s.land_m2 > 0:
                land = z.plantable_land_m2.value
                if land is None:
                    status, reason, ub = "not_estimable", "plantable land not estimable from current evidence", 0
                else:
                    caps.append(math.floor(land / s.land_m2))
            if status == "eligible" and caps:
                ub = min([ub, *caps])
                if ub == 0:
                    status, reason = "ineligible", "assumed eligible area smaller than one unit"
                elif ub < s.max_units_per_zone:
                    reason = "limited by assumed eligible area"
            if t not in allowed:
                status, reason, ub = "ineligible", "excluded by planner selection", 0
            out.append(Candidate(
                candidate_id=f"{z.zone_id}:{t}",
                zone_id=z.zone_id,
                intervention_type=t,
                capex_inr=s.capex_inr,
                lcc_inr=lifecycle_cost_inr(s.capex_inr, s.capex_inr * s.om_fraction, rate, years),
                roof_m2=s.roof_m2,
                land_m2=s.land_m2,
                upper_bound=ub,
                eligibility=status,
                eligibility_reason=reason,
                source_ids=("CFG_INTERVENTIONS",),
            ))
    return out
