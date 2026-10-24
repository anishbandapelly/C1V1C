"""Frontend integration tests: real UI controls drive real engine runs (synthetic baseline unless stated)."""
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from conftest import requires_real
from ui.backend import KEYS, LABELS

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def synthetic_ui(synthetic_dir, monkeypatch):
    monkeypatch.setenv("C1V1C_CURATED_DIR", str(synthetic_dir.parent))
    monkeypatch.setenv("C1V1C_BASELINE_VERSION", synthetic_dir.name)
    st.cache_resource.clear()
    from c1v1c.baseline import _load
    _load.cache_clear()
    yield
    st.cache_resource.clear()


def app(page='City Intelligence'):
    a = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=120).run()
    a.session_state['page'] = page
    a.run()
    assert not a.exception, a.exception
    return a


def choose(a, kind, label, value):
    next(x for x in getattr(a, kind) if x.label == label).set_value(value)
    a.run()
    assert not a.exception, a.exception
    return a


def submit(a):
    next(x for x in a.button if x.label == 'Run optimisation').click().run()
    assert not a.exception, a.exception
    return a


def set_budget(a, text):
    """Drive the custom budget component through its own state, which then flows through parse_budget."""
    a.session_state['capital_budget'] = {'value': text}
    a.run()
    assert not a.exception, a.exception
    return a


def shock(a, kind):
    a.session_state['page'] = 'Climate Shock Lab'
    a.run()
    choose(a, 'selectbox', 'Disruption', kind)
    next(b for b in a.button if b.label == 'Run shock comparison').click().run()
    assert not a.exception, a.exception
    return a


@pytest.mark.parametrize('page', ['Home', 'City Intelligence', 'Investment Optimiser', 'Climate Shock Lab', 'Decision Intelligence'])
def test_every_page_states_its_data_mode(page):
    a = app(page)
    assert any('synthetic demonstration' in x.value.lower() for x in a.info)


def test_optimiser_runs_the_real_solver_and_verifies():
    a = submit(app('Investment Optimiser'))
    run = a.session_state['active_run']
    assert run.solver_status == 'optimal' and run.run_id.startswith('run-')
    assert run.allocated_inr <= run.budget_available_inr and all(run.verification.values())
    assert any('Optimal (CBC, proven)' in c.value for c in a.caption)
    assert any(m.label == 'Capital · INR crore' for m in a.metric)
    assert run.run_id in a.session_state['history']


def test_budget_input_conversion_reaches_the_solver():
    a = app('Investment Optimiser')
    set_budget(a, '0.5')
    submit(a)
    run = a.session_state['active_run']
    assert run.request.budget_inr == 5_000_000 and run.allocated_inr <= 5_000_000


def test_inputs_changed_warning_and_zero_budget():
    a = submit(app('Investment Optimiser'))
    choose(a, 'selectbox', 'Priority mode', 'Water-first')
    assert any('Inputs changed' in x.value for x in a.warning)
    set_budget(a, '0')
    submit(a)
    assert a.session_state['active_run'].selected_candidate_counts == {}


def test_intervention_filter_limits_the_solver():
    a = app('Investment Optimiser')
    for key in ['green_roof', 'rainwater_harvesting', 'drainage_upgrade']:
        choose(a, 'checkbox', LABELS[key], False)
    submit(a)
    run = a.session_state['active_run']
    assert run.selected_candidate_counts and all(k.endswith('urban_forest') for k in run.selected_candidate_counts)


def test_weights_must_total_100_and_infeasible_floor_is_reported():
    a = app('Investment Optimiser')
    choose(a, 'number_input', 'Flood weight · %', 40)
    submit(a)
    assert any('100%' in x.value for x in a.error)
    choose(a, 'number_input', 'Flood weight · %', 25)
    set_budget(a, '0.1')
    choose(a, 'slider', 'Priority-zone benefit floor · normalised', 0.5)
    submit(a)
    run = a.session_state['active_run']
    assert run.solver_status == 'infeasible' and run.outcome is None
    assert any('No feasible portfolio' in x.value for x in a.error)


@pytest.mark.parametrize('kind', ['Extreme rainfall', 'Drought', 'Sudden budget cut', 'Normal baseline'])
def test_shocks_keep_original_and_reoptimise(kind):
    a = submit(app('Investment Optimiser'))
    original = a.session_state['active_run']
    shock(a, kind)
    comp = a.session_state['shock_results'][a.session_state['active_shock']]
    assert comp.original_run_id == original.run_id
    assert comp.b_original_under_shock.counts == original.selected_candidate_counts
    assert a.session_state['active_run'] == original
    assert comp.c_reoptimised.run_id in a.session_state['history']
    assert any('comparison' in h.value for h in a.header)
    a.session_state['page'] = 'Decision Intelligence'
    a.run()
    assert not a.exception
    assert len(a.get('download_button')) == 2


def test_decision_intelligence_is_grounded_and_has_sources():
    a = submit(app('Investment Optimiser'))
    shock(a, 'Sudden budget cut')
    a.session_state['page'] = 'Decision Intelligence'
    a.run()
    assert not a.exception
    assert any('deterministic explainer' in c.value for c in a.caption)
    assert any(e.label == 'Sources & assumptions' for e in a.expander)
    assert any(e.label == 'Under climate shocks' for e in a.expander)
    assert not a.json  # no raw developer dumps in the main UI


def test_zone_selection_updates_profile():
    a = app()
    choose(a, 'selectbox', 'Pilot ward', 'ZB')
    assert any(x.value == '6,500' for x in a.metric)  # synthetic fixture population for zone B


def test_home_entry_points_and_guest_contract():
    from ui.shell import ProfileView
    a = app('Home')
    next(x for x in a.button if x.label == 'Explore the pilot').click().run()
    assert a.session_state['page'] == 'City Intelligence'
    assert not ProfileView().authenticated and ProfileView().display_name == 'Guest workspace'


def test_planning_inputs_survive_navigation():
    a = app('Investment Optimiser')
    choose(a, 'selectbox', 'Priority mode', 'Water-first')
    a.session_state['page'] = 'Home'
    a.run()
    a.session_state['page'] = 'Investment Optimiser'
    a.run()
    assert next(x for x in a.selectbox if x.label == 'Priority mode').value == 'Water-first'


@pytest.mark.parametrize('page', ['Climate Shock Lab', 'Decision Intelligence'])
def test_preanalysis_has_a_working_next_action(page):
    a = app(page)
    a.button[0].click().run()
    assert a.session_state['page'] == 'Investment Optimiser'


@pytest.mark.parametrize('mode', ['Balanced', 'Flood-first', 'Water-first', 'Heat-first', 'Equity-first'])
def test_priority_presets_propagate(mode):
    from c1v1c.catalogue import load_parameters
    a = app('Investment Optimiser')
    choose(a, 'selectbox', 'Priority mode', mode)
    submit(a)
    run = a.session_state['active_run']
    assert run.request.weights == dict(zip(KEYS, load_parameters().modes[mode])) and run.request.mode == mode


def test_incompatible_saved_versions_are_excluded():
    a = submit(app('Investment Optimiser'))
    original = a.session_state['active_run']
    other = original.model_copy(update={'run_id': 'run-other', 'baseline_version': 'different-baseline'})
    a.session_state['history'] = {original.run_id: original, other.run_id: other}
    a.session_state['page'] = 'Decision Intelligence'
    a.run()
    choose(a, 'multiselect', 'Saved runs to compare', [original.run_id, other.run_id])
    assert any('Incompatible' in w.value for w in a.warning)


def test_theme_palettes_meet_text_contrast_and_chart_remap():
    from ui.theme import PALETTES

    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return sum((v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) * w for v, w in zip(c, [.2126, .7152, .0722]))
    for p in PALETTES.values():
        for x, y in [('text', 'bg'), ('muted', 'bg'), ('text', 'surface'), ('muted', 'surface'), ('accent-fg', 'accent'), ('link', 'bg')]:
            lo, hi = sorted([lum(p[x]), lum(p[y])])
            assert (hi + .05) / (lo + .05) >= 4.5


@pytest.mark.parametrize('text,amount', [('2', 20000000), ('2.2', 22000000), ('2.4', 24000000), ('10.5', 105000000), ('0', 0),
                                         ('100', 1000000000), ('0.0000001', 1)])
def test_exact_budget(text, amount):
    from ui.budget import parse_budget
    assert parse_budget(text) == amount


@pytest.mark.parametrize('text', ['', '2,2', '-1', '101', 'NaN', '1e3', '0.00000001'])
def test_invalid_budget(text):
    from ui.budget import parse_budget
    with pytest.raises(ValueError):
        parse_budget(text)


def test_missing_baseline_shows_honest_error(monkeypatch, tmp_path):
    monkeypatch.setenv('C1V1C_CURATED_DIR', str(tmp_path / 'nowhere'))
    st.cache_resource.clear()
    a = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60).run()
    a.session_state['page'] = 'Investment Optimiser'
    a.run()
    assert not a.exception
    assert any('could not load its Bengaluru baseline' in e.value for e in a.error)


@requires_real
def test_end_to_end_on_real_bengaluru_baseline(monkeypatch):
    """Hero -> City -> Optimiser -> Shock Lab -> Decision Intelligence on the real curated baseline."""
    monkeypatch.setenv('C1V1C_CURATED_DIR', str(ROOT / 'data' / 'curated'))
    monkeypatch.setenv('C1V1C_BASELINE_VERSION', 'bengaluru_pilot_v1')
    st.cache_resource.clear()
    from c1v1c.baseline import _load
    _load.cache_clear()
    a = app('Home')
    assert any('mixed-evidence pilot' in x.value.lower() for x in a.info)
    next(x for x in a.button if x.label == 'Explore the pilot').click().run()
    assert a.session_state['page'] == 'City Intelligence' and not a.exception
    assert all('Yelahanka' in o for o in a.selectbox(key='input_zone').options)
    a.session_state['page'] = 'Investment Optimiser'
    a.run()
    submit(a)
    run = a.session_state['active_run']
    assert run.solver_status == 'optimal' and run.data_mode.value == 'mixed-evidence pilot'
    assert run.baseline_version == 'bengaluru_pilot_v1'
    for kind in ('Extreme rainfall', 'Drought', 'Sudden budget cut'):
        shock(a, kind)
    a.session_state['page'] = 'Decision Intelligence'
    a.run()
    assert not a.exception
    assert run.run_id in a.session_state['history'] and a.session_state['active_run'].run_id == run.run_id
    assert any(run.run_id in str(o) for o in a.selectbox[0].options)
