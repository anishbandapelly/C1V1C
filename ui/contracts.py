"""Versioned UI boundary. No physical models or optimisation implemented here."""
from typing import Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

Intervention = Literal['green_roof', 'urban_forest', 'rainwater_harvesting', 'drainage_upgrade']

class Indicator(BaseModel):
    indicator_id: str
    zone_id: str
    numeric_value: float | None
    unit: str
    better_direction: Literal['higher', 'lower', 'context']
    source_id: str
    observation_period: str | None
    geometry_scale: str
    evidence_grade: Literal['A', 'B', 'C', 'D']
    uncertainty_low: float | None = None
    uncertainty_high: float | None = None
    missing_reason: str | None = None

class ScenarioRequest(BaseModel):
    model_config = ConfigDict(frozen=True)
    area_id: str = 'pilot_yelahanka_demo'
    baseline_version: str = 'synthetic-v1'
    project_catalog_version: str = 'synthetic-catalog-v1'
    model_version: str = 'not-implemented'
    budget_inr: float = Field(ge=0)
    weights: dict[str, float]
    equity_floor: float = Field(default=0, ge=0, le=1)
    scenario_id: Literal['normal', 'extreme_rain', 'drought', 'budget_cut'] = 'normal'
    overrides: dict[str, float] = Field(default_factory=dict)
    committed_candidate_ids: tuple[str, ...] = ()
    allowed_interventions: tuple[Intervention, ...]

    @model_validator(mode='after')
    def valid_weights(self):
        if set(self.weights) != {'F', 'W', 'H', 'G', 'Equity', 'LCC'}:
            raise ValueError('All six objective weights are required.')
        if any(v < 0 for v in self.weights.values()) or abs(sum(self.weights.values()) - 1) > 1e-6:
            raise ValueError('Weights must be nonnegative and sum to one.')
        return self

class CandidateProject(BaseModel):
    candidate_id: str
    zone_id: str
    site_id: str
    type: Intervention
    capex_inr: float = Field(ge=0)
    opex_inr_y: float | None = Field(default=None, ge=0)
    life_y: int | None = Field(default=None, gt=0)
    resource_demands: dict[str, float]
    upper_bound: int = Field(ge=0)
    prerequisites: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()
    coefficients_by_scenario: dict[str, dict]
    source_ids: tuple[str, ...]
    eligibility: Literal['verified', 'ineligible', 'unverified']

class DecisionExplanation(BaseModel):
    selected_and_rejected_reasons: dict[str, str]
    relevant_computed_numbers: dict[str, dict]
    counterfactuals: list[dict]
    limitations: list[str]
    source_ids: list[str]
    explanation_source: Literal['deterministic', 'Bedrock']
    validation_passed: bool

class RunResult(BaseModel):
    """Future engine output; nullable metrics never imply zero."""
    run_id: str
    input_hash: str
    created_at_utc: str
    request: ScenarioRequest
    solver_status: Literal['optimal', 'feasible_time_limit', 'infeasible', 'error', 'not_run']
    selected_candidate_counts: dict[str, int]
    raw_objectives_with_units: dict[str, dict]
    normalised_components: dict[str, float]
    score_contributions: dict[str, float]
    constraint_slack: dict[str, float]
    baseline_and_shock_metrics: dict
    outcomes_by_zone: dict
    assumptions: list[str]
    gaps: list[str]
    source_ids: list[str]
    warnings: list[str]

class EnginePort(Protocol):
    """Bind after frontend approval; never substitute fixture output for this port."""
    def run_scenario(self, request: ScenarioRequest) -> RunResult: ...
    def load_run(self, run_id: str) -> RunResult: ...

class PreviewSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)
    preview_id: str
    request: ScenarioRequest
    selected_ids: tuple[str, ...]
    cost_inr: int
    fixture_name: str
    data_mode: Literal['synthetic demonstration'] = 'synthetic demonstration'
    solver_status: Literal['not_run'] = 'not_run'
    notice: str = 'Frontend fixture only. No optimisation or environmental model has run.'
