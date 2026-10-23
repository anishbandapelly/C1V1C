"""C1V1C frontend approval build. Engine deliberately not connected."""
import streamlit as st
from ui.theme import apply_theme
from ui import views

st.set_page_config(page_title='C1V1C · Tulabhara AI',page_icon=':material/balance:',layout='wide')
apply_theme()
with st.sidebar:
    st.markdown('## C1V1C')
    st.caption('TULABHARA AI')
    st.write('Urban sustainability\n\nBengaluru / Yelahanka pilot')
    page=st.radio('Planning workspace',['City Intelligence','Investment Optimiser','Climate Shock Lab','Decision Intelligence'],label_visibility='collapsed')
    st.divider()
    st.caption('Frontend review / Phase 3')
    st.write('Evidence before investment.')
    st.caption('Local demonstration · no AWS connection')
    with st.expander('About this preview'):
        st.write('Inspect the four workflows. Samples are temporary frontend fixtures, not recommendations. Backend implementation starts only after design approval.')
        st.write('Saved previews last for this browser session. Export a snapshot to retain it.')
st.warning('Demonstration data — not observed Bengaluru conditions. Frontend review only; optimisation and environmental models have not run.',icon=':material/info:')
{'City Intelligence':views.city,'Investment Optimiser':views.optimiser,'Climate Shock Lab':views.shock_lab,'Decision Intelligence':views.decisions}[page]()
st.divider()
st.caption('C1V1C — Tulabhara AI · Evidence grade D unless stated otherwise · Planning estimates require validation before use.')
