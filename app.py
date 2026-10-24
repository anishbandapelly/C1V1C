"""C1V1C - Tulabhara AI: Streamlit workspace over the decision engine."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))  # allow `streamlit run app.py` without installing

import streamlit as st  # noqa: E402

from ui import views  # noqa: E402
from ui.backend import engine  # noqa: E402
from ui.shell import render_shell  # noqa: E402
from ui.theme import apply_theme  # noqa: E402

st.set_page_config(page_title='C1V1C · Tulabhara AI', page_icon=':material/balance:', layout='wide', initial_sidebar_state='collapsed')
apply_theme()
# Preserve named planning inputs across routes (Streamlit otherwise cleans up
# widgets that are absent on a page). Saved runs remain immutable records.
for key in list(st.session_state):
    if key in ('budget_text', 'budget_draft', 'capital_budget', 'mode') or key.startswith(('input_', 'shock_', 'Balanced-', 'Flood-first-', 'Water-first-', 'Heat-first-', 'Equity-first-')):
        st.session_state[key] = st.session_state[key]
page = render_shell()
eng = engine()
if eng is not None:
    st.info(f'{eng.baseline.data_mode.value.capitalize()} · real GBA ward, footprint, hazard and IMD climate data; intervention '
            'costs and effects are declared assumptions. Results are modelled screening estimates, not forecasts.', icon=':material/info:')
{'Home': views.home, 'City Intelligence': views.city, 'Investment Optimiser': views.optimiser, 'Climate Shock Lab': views.shock_lab, 'Decision Intelligence': views.decisions}[page]()
st.divider()
st.caption('C1V1C — Tulabhara AI · Bengaluru pilot · Evidence and assumptions travel with every decision.')
