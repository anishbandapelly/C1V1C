"""Frontend review tests; these do not certify the unimplemented engine."""
import pytest
from pathlib import Path
from pydantic import ValidationError
from streamlit.testing.v1 import AppTest
from ui.contracts import ScenarioRequest
from ui.fixtures import preview, LABELS, PORTFOLIOS

def request(**changes):
    values=dict(budget_inr=20_000_000,weights=dict(F=.25,W=.2,H=.2,G=.1,Equity=.15,LCC=.1),allowed_interventions=tuple(LABELS))
    return ScenarioRequest(**(values|changes))

def app(page='City Intelligence'):
    a=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=30).run()
    a.radio[0].set_value(page).run()
    assert not a.exception
    return a

def choose(a,kind,label,value):
    next(x for x in getattr(a,kind) if x.label==label).set_value(value)
    return a.run()

def submit(a):
    next(x for x in a.button if x.label=='Preview allocation').click().run()
    assert not a.exception
    return a

@pytest.mark.parametrize('page',['City Intelligence','Investment Optimiser','Climate Shock Lab','Decision Intelligence'])
def test_navigation_and_honesty(page):
    a=app(page)
    assert any('Demonstration data' in x.value for x in a.warning)

def test_snapshot_cost_and_immutability():
    s=preview(request(),'Mixed investment')
    assert s.cost_inr==11_200_000 and s.solver_status=='not_run'
    assert s.preview_id==preview(request(),'Mixed investment').preview_id
    with pytest.raises(ValidationError):s.cost_inr=0
    assert preview(request(allowed_interventions=()),'Mixed investment').selected_ids==()
    with pytest.raises(ValueError):preview(request(budget_inr=0),'Mixed investment')

def test_contract_rejects_invalid_inputs():
    with pytest.raises(ValidationError):request(budget_inr=-1)
    with pytest.raises(ValidationError):request(weights=dict(F=1))
    with pytest.raises(ValidationError):request(equity_floor=2)

def test_preview_stale_budget_and_recovery():
    a=submit(app('Investment Optimiser'))
    assert a.session_state['active_preview'].cost_inr==11_200_000
    choose(a,'number_input','Capital budget · INR crore',.1)
    assert any('Inputs changed' in x.value for x in a.warning)
    submit(a)
    assert any('above the entered budget' in x.value for x in a.error)
    choose(a,'selectbox','Display portfolio','No investment')
    submit(a)
    assert a.session_state['active_preview'].cost_inr==0

def test_filter_withholds_unrelated_benefits():
    a=app('Investment Optimiser')
    choose(a,'multiselect','Interventions to consider',['urban_forest'])
    submit(a)
    assert a.session_state['active_preview'].selected_ids==('B-urban_forest',)
    assert any('Outcome fixtures are withheld' in x.value for x in a.warning)

@pytest.mark.parametrize('state',['Loading example','Infeasible example','Service error example','Missing data example'])
def test_review_states(state):
    a=app('Investment Optimiser')
    choose(a,'selectbox','Review state',state)
    assert not a.exception

def test_weights_and_equity_validation():
    a=app('Investment Optimiser')
    choose(a,'number_input','Flood weight · %',40)
    submit(a)
    assert any('100%' in x.value for x in a.error)
    choose(a,'number_input','Flood weight · %',25)
    choose(a,'slider','Priority-zone benefit floor · normalised',.5)
    submit(a)
    assert any('cannot verify a benefit floor' in x.value for x in a.error)

@pytest.mark.parametrize('shock',['Extreme rainfall','Drought','Sudden budget cut'])
def test_shocks_preserve_original_selection(shock):
    a=submit(app('Investment Optimiser'))
    original=a.session_state['active_preview']
    a.radio[0].set_value('Climate Shock Lab').run()
    choose(a,'selectbox','Disruption',shock)
    next(b for b in a.button if b.label=='Preview shock comparison').click().run()
    assert not a.exception
    assert a.session_state['shock_preview']['ids']==list(original.selected_ids)
    assert a.session_state['active_preview']==original
    a.radio[0].set_value('Decision Intelligence').run()
    assert not a.exception
    assert len(a.get('download_button'))==2

def test_zone_selection_updates_profile():
    a=app()
    choose(a,'selectbox','Neighbourhood fixture','B')
    assert any(x.value=='6,500' for x in a.metric)
