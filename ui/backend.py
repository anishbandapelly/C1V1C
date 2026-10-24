"""Adapter between the Streamlit views and the decision engine (single cached instance)."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from c1v1c.baseline import BaselineUnavailable
from c1v1c.config import Settings
from c1v1c.engine import Engine
from c1v1c.evidence import GRADE, LABEL, Evidence, Quantity
from c1v1c.explainer import explain
from c1v1c.schemas import INTERVENTIONS, WEIGHT_KEYS, DecisionExplanation, RunResult, ScenarioComparison

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'green_roof': 'Green roofs', 'urban_forest': 'Urban forests',
          'rainwater_harvesting': 'Rainwater harvesting', 'drainage_upgrade': 'Drainage improvements'}
KEYS = list(WEIGHT_KEYS)
WEIGHT_LABELS = ['Flood', 'Water', 'Heat', 'Carbon', 'Equity', 'Lifecycle cost']
SHOCKS = {'Extreme rainfall': 'extreme_rain', 'Drought': 'drought', 'Sudden budget cut': 'budget_cut', 'Normal baseline': 'normal'}


@st.cache_resource(show_spinner='Loading the Bengaluru baseline…')
def _engine() -> Engine:
    return Engine(Settings.load())  # the engine attaches S3 itself when online


def engine() -> Engine | None:
    """The engine, or None with the reason recorded for an honest error state."""
    try:
        return _engine()
    except BaselineUnavailable as exc:
        st.session_state['engine_error'] = str(exc)
        return None


def weights_pct(eng: Engine) -> dict[str, list[int]]:
    return {mode: [round(v * 100) for v in w] for mode, w in eng.params.modes.items()}


def zone_names(eng: Engine) -> dict[str, str]:
    return {z.zone_id: z.name for z in eng.baseline.zones}


def candidate_label(eng: Engine, cid: str) -> str:
    zone, kind = cid.split(':', 1)
    return f'{LABELS[kind]} · {zone_names(eng).get(zone, zone)}'


def evidence_text(q: Quantity) -> str:
    return f'{GRADE[q.evidence]} · {LABEL[q.evidence]}'


def fmt_value(q: Quantity, digits: int = 2) -> str:
    if q.value is None:
        return 'Not available'
    v = q.value
    if abs(v) >= 1000:
        return f'{v:,.0f}'
    return f'{v:,.{digits}f}'.rstrip('0').rstrip('.') if digits else f'{v:,.0f}'


def explanation_for(eng: Engine, run: RunResult) -> DecisionExplanation:
    comparisons = [c for c in st.session_state.get('shock_results', {}).values() if c.original_run_id == run.run_id]
    e = explain(run, zone_names(eng), comparisons)
    settings = eng.settings
    if not settings.offline_mode and settings.bedrock_model_id:
        from c1v1c.aws.bedrock import narrate
        key = ('narration', run.run_id, len(comparisons))
        cache = st.session_state.setdefault('narrations', {})
        if key not in cache:
            cache[key] = narrate(e, settings)
        return cache[key]
    reason = 'offline mode' if settings.offline_mode else 'BEDROCK_MODEL_ID not configured'
    return e.model_copy(update={'bedrock_status': f'{reason}: deterministic explanation shown'})


def save_run(run: RunResult) -> None:
    st.session_state['active_run'] = run
    st.session_state.setdefault('history', {})[run.run_id] = run


def save_comparison(comp: ScenarioComparison) -> None:
    st.session_state.setdefault('shock_results', {})[comp.comparison_id] = comp
    st.session_state['active_shock'] = comp.comparison_id
    st.session_state.setdefault('history', {})[comp.c_reoptimised.run_id] = comp.c_reoptimised


__all__ = ['engine', 'LABELS', 'KEYS', 'WEIGHT_LABELS', 'SHOCKS', 'INTERVENTIONS', 'Evidence', 'weights_pct', 'zone_names',
           'candidate_label', 'evidence_text', 'fmt_value', 'explanation_for', 'save_run', 'save_comparison', 'ROOT']
