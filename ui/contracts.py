"""Versioned UI boundary. The frontend consumes the engine's typed contracts directly."""
from typing import Protocol

from c1v1c.schemas import (  # noqa: F401  (re-exported for the views and tests)
    INTERVENTIONS, Candidate, DecisionExplanation, Intervention, PortfolioOutcome, RunRequest, RunResult,
    ScenarioComparison, ZoneBaseline,
)

ScenarioRequest = RunRequest


class EnginePort(Protocol):
    """Implemented by c1v1c.engine.Engine."""

    def run(self, request: RunRequest) -> RunResult: ...

    def load_run(self, run_id: str) -> RunResult: ...

    def shock(self, original: RunResult, scenario_id: str, overrides: dict[str, float] | None = None,
              committed_counts: dict[str, int] | None = None) -> ScenarioComparison: ...
