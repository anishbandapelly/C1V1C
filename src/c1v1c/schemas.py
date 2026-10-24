"""Typed engine contracts (master plan §8.4). Pydantic v2, validated before solving."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from c1v1c.evidence import DataMode, Evidence, Quantity

Intervention = Literal["green_roof", "urban_forest", "rainwater_harvesting", "drainage_upgrade"]
INTERVENTIONS: tuple[Intervention, ...] = ("green_roof", "urban_forest", "rainwater_harvesting", "drainage_upgrade")
WEIGHT_KEYS = ("F", "W", "H", "G", "Equity", "LCC")
METRICS = ("F", "W", "H", "G")
METRIC_UNITS = {
    "F": "m3 per design event (retained or newly conveyed)",
    "W": "m3/yr usable water (net of irrigation)",
    "H": "person-index units (heat exposure reduction)",
    "G": "tCO2e over 10 yr (forest sequestration only)",
}
SCENARIO_IDS = ("normal", "extreme_rain", "drought", "budget_cut")
SolverStatus = Literal["optimal", "feasible_time_limit", "infeasible", "error", "not_run"]


class ZoneBaseline(BaseModel):
    """Zone-level inputs for one pilot zone. Every metric is a Quantity with evidence."""

    model_config = ConfigDict(frozen=True)

    zone_id: str
    name: str
    ward_keys: tuple[str, ...]
    gba_corporation: str
    gba_zone_name: str
    centroid_lat: float
    centroid_lon: float
    area_ha: Quantity
    population: Quantity
    sc_st_share: Quantity
    built_fraction: Quantity
    impervious_fraction: Quantity
    vegetation_fraction: Quantity
    runoff_coefficient: Quantity
    eligible_roof_m2: Quantity
    plantable_land_m2: Quantity
    design_p24_mm: Quantity
    design_event_mm: Quantity
    design_event_runoff_m3: Quantity
    summer_tmax_c: Quantity
    heat_index: Quantity
    vulnerability_weight: Quantity
    flood_points: Quantity
    drain_length_m: Quantity
    waterbody_features: Quantity
    rainfall_cell: str
    selection_reason: str = ""


class InterventionSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    intervention_type: Intervention
    label: str
    unit_description: str
    capex_inr: float = Field(ge=0)
    om_fraction: float = Field(ge=0, le=1)
    roof_m2: float = Field(ge=0)
    land_m2: float = Field(ge=0)
    tank_capacity_m3: float = Field(ge=0)
    retention_depth_mm: float = Field(ge=0)
    irrigation_m3_month: float = Field(ge=0)
    drainage_capacity_delta_m3_s: float = Field(ge=0)
    max_units_per_zone: int = Field(ge=0)
    evidence: Evidence = Evidence.ASSUMED
    source: str = ""
    notes: str = ""


class Candidate(BaseModel):
    """One decision variable: repeatable units of one intervention type in one zone."""

    model_config = ConfigDict(frozen=True)

    candidate_id: str
    zone_id: str
    intervention_type: Intervention
    capex_inr: float = Field(ge=0)
    lcc_inr: float = Field(ge=0)
    roof_m2: float = Field(ge=0)
    land_m2: float = Field(ge=0)
    upper_bound: int = Field(ge=0)
    eligibility: Literal["eligible", "ineligible", "not_estimable"]
    eligibility_reason: str
    requires: tuple[str, ...] = ()
    excludes: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


class ScenarioParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    scenario_id: Literal["normal", "extreme_rain", "drought", "budget_cut"]
    name: str
    design_intensity_multiplier: float = Field(gt=0, le=5)
    rainfall_availability_factor: float = Field(ge=0, le=2)
    tree_cooling_factor: float = Field(ge=0, le=1)
    budget_factor: float = Field(ge=0, le=1)
    classification: str = "ILLUSTRATIVE_PLANNING_PRESET"
    source: str = ""


class RunRequest(BaseModel):
    """Planner request. Weights are fractions in order F, W, H, G, Equity, LCC summing to 1."""

    model_config = ConfigDict(frozen=True)

    area_id: str = "bengaluru_gba_pilot"
    baseline_version: str
    project_catalog_version: str
    model_version: str
    budget_inr: float = Field(ge=0, le=1_000_000_000)
    weights: dict[str, float]
    equity_floor: float = Field(default=0.0, ge=0, le=1)
    scenario_id: Literal["normal", "extreme_rain", "drought", "budget_cut"] = "normal"
    overrides: dict[str, float] = Field(default_factory=dict)
    committed_candidate_ids: tuple[str, ...] = ()
    committed_counts: dict[str, int] = Field(default_factory=dict)
    allowed_interventions: tuple[Intervention, ...]
    mode: str = "Custom"

    @field_validator("weights")
    @classmethod
    def _weights(cls, value: dict[str, float]) -> dict[str, float]:
        if set(value) != set(WEIGHT_KEYS):
            raise ValueError(f"weights must contain exactly {WEIGHT_KEYS}")
        if any(v < 0 for v in value.values()):
            raise ValueError("weights must be non-negative")
        if abs(sum(value.values()) - 1.0) > 1e-6:
            raise ValueError("weights must sum to 1")
        return value

    @field_validator("overrides")
    @classmethod
    def _overrides(cls, value: dict[str, float]) -> dict[str, float]:
        allowed = {"design_intensity_multiplier", "rainfall_availability_factor", "tree_cooling_factor", "budget_factor"}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"unknown scenario overrides: {sorted(unknown)}")
        return value

    @model_validator(mode="after")
    def _commitments(self) -> "RunRequest":
        if any(c < 0 for c in self.committed_counts.values()):
            raise ValueError("committed counts must be non-negative")
        return self


class PortfolioOutcome(BaseModel):
    """Independent (non-surrogate) evaluation of one portfolio under one scenario."""

    scenario_id: str
    counts: dict[str, int]
    capex_inr: float
    lcc_inr: float
    metrics: dict[str, float | None]
    metric_components: dict[str, dict[str, float | None]]
    by_zone: dict[str, dict[str, float | None]]
    normalised: dict[str, float]
    score: float
    equity_gain: float
    benefit_gini: float | None
    constraint_checks: dict[str, bool]
    violations: list[str]


class Alternative(BaseModel):
    alternative_id: str
    label: str
    method: str
    counts: dict[str, int]
    outcome: PortfolioOutcome | None
    feasible: bool
    note: str = ""


class RunResult(BaseModel):
    """Immutable run record. Nullable metrics never imply zero."""

    model_config = ConfigDict(frozen=True)

    run_id: str
    input_hash: str
    created_at_utc: str
    request: RunRequest
    data_mode: DataMode
    baseline_version: str
    baseline_sha256: str
    model_version: str
    catalog_version: str
    scenario: ScenarioParams
    solver_status: SolverStatus
    solver_message: str
    solver_runtime_s: float
    budget_available_inr: float
    committed_capex_inr: float
    selected_candidate_counts: dict[str, int]
    capex_by_intervention: dict[str, float]
    capex_by_zone: dict[str, float]
    allocated_inr: float
    unallocated_inr: float
    raw_objectives_with_units: dict[str, dict]
    normalised_components: dict[str, float]
    score_contributions: dict[str, float]
    surrogate_score: float | None
    evaluated_score: float | None
    constraint_slack: dict[str, float]
    binding_constraints: list[str]
    rejected: dict[str, str]
    outcome: PortfolioOutcome | None
    baseline_outcome: PortfolioOutcome | None
    alternatives: list[Alternative]
    outcomes_by_zone: dict[str, dict]
    verification: dict[str, bool]
    assumptions: list[str]
    gaps: list[str]
    source_ids: list[str]
    warnings: list[str]
    parent_run_id: str | None = None
    comparison_role: Literal["optimised", "original_under_shock", "reoptimised_under_shock"] = "optimised"


class ScenarioComparison(BaseModel):
    comparison_id: str
    scenario: ScenarioParams
    original_run_id: str
    a_original_normal: PortfolioOutcome | None
    b_original_under_shock: PortfolioOutcome | None
    b_feasible: bool
    b_notes: list[str]
    c_reoptimised: RunResult
    additions: dict[str, int]
    removals: dict[str, int]
    deltas: dict[str, dict[str, float | None]]
    sensitivity: dict[str, dict[str, float]]


class DecisionExplanation(BaseModel):
    run_id: str
    headline: str
    why_selected: list[str]
    why_rejected: dict[str, str]
    alternatives_compared: list[dict]
    improved: list[str]
    worsened: list[str]
    beneficiaries: list[dict]
    underserved: list[str]
    binding_constraints: list[str]
    shock_findings: list[str]
    assumptions: list[str]
    uncertainties: list[str]
    unintended_consequences: list[str]
    relevant_computed_numbers: dict[str, float | None]
    source_ids: list[str]
    narrative: str
    explanation_source: Literal["deterministic", "bedrock"]
    bedrock_status: str
    validation_passed: bool
