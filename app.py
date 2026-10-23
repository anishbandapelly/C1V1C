"""C1V1C frontend approval build. Engine deliberately not connected."""
import streamlit as st
from ui.theme import apply_theme
from ui.shell import render_shell
from ui import views

st.set_page_config(page_title='C1V1C · Tulabhara AI',page_icon=':material/balance:',layout='wide',initial_sidebar_state='collapsed')
apply_theme()
# Preserve named planning inputs across routes (Streamlit otherwise cleans up
# widgets that are absent on a page). Snapshots remain independent copies.
for key in list(st.session_state):
    if key in ('budget','mode') or key.startswith(('input_','Balanced-','Flood-first-','Water-first-','Heat-first-','Equity-first-')):
        st.session_state[key]=st.session_state[key]
page=render_shell()
st.warning('Demonstration data — not observed Bengaluru conditions. Models and optimisation have not run.',icon=':material/info:')
{'Home':views.home,'City Intelligence':views.city,'Investment Optimiser':views.optimiser,'Climate Shock Lab':views.shock_lab,'Decision Intelligence':views.decisions}[page]()
st.divider()
st.caption('C1V1C — Tulabhara AI · Bengaluru pilot / frontend review · Evidence and assumptions travel with every decision.')
