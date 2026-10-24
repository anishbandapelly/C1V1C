"""Evidence taxonomy shared by every value the engine produces.

The six classes are never silently substituted for one another. Missing values
carry ``value=None`` and a reason; they are never coerced to zero.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Evidence(str, Enum):
    OBSERVED = "observed"        # measured / published source value, used as-is
    DERIVED = "derived"          # deterministic transformation of observed data
    ESTIMATED = "estimated"      # literature value transferred to Bengaluru
    ASSUMED = "assumed"          # declared planning assumption (D grade)
    SYNTHETIC = "synthetic"      # test fixture only; never shown as city data
    MISSING = "missing"          # not available; value is None


LABEL = {
    Evidence.OBSERVED: "Observed",
    Evidence.DERIVED: "Derived",
    Evidence.ESTIMATED: "Estimated",
    Evidence.ASSUMED: "Assumed",
    Evidence.SYNTHETIC: "Synthetic demo",
    Evidence.MISSING: "Missing",
}

# Master plan evidence grades (qualitative, not probabilities).
GRADE = {
    Evidence.OBSERVED: "A",
    Evidence.DERIVED: "B",
    Evidence.ESTIMATED: "C",
    Evidence.ASSUMED: "D",
    Evidence.SYNTHETIC: "D",
    Evidence.MISSING: "-",
}


class Quantity(BaseModel):
    """A number with unit, evidence class and provenance."""

    model_config = ConfigDict(frozen=True)

    value: float | None
    unit: str
    evidence: Evidence
    source_ids: tuple[str, ...] = ()
    note: str = ""
    low: float | None = None
    high: float | None = None
    missing_reason: str | None = None

    @classmethod
    def missing(cls, unit: str, reason: str, source_ids: tuple[str, ...] = ()) -> "Quantity":
        return cls(value=None, unit=unit, evidence=Evidence.MISSING, source_ids=source_ids, missing_reason=reason)

    @property
    def label(self) -> str:
        return LABEL[self.evidence]


def weakest(*classes: Evidence) -> Evidence:
    """The evidence class of a result is the weakest of its inputs."""
    order = [Evidence.OBSERVED, Evidence.DERIVED, Evidence.ESTIMATED, Evidence.ASSUMED, Evidence.SYNTHETIC, Evidence.MISSING]
    return max(classes, key=order.index) if classes else Evidence.MISSING


class DataMode(str, Enum):
    OBSERVED_PILOT = "observed-data pilot"
    MIXED_PILOT = "mixed-evidence pilot"
    SYNTHETIC = "synthetic demonstration"


__all__ = ["Evidence", "LABEL", "GRADE", "Quantity", "weakest", "DataMode", "Field"]
