"""Streamlit-native component shell; no authentication or engine implementation."""
from pathlib import Path
import streamlit as st
from pydantic import BaseModel

ROOT=Path(__file__).parent
PAGES=('Home','City Intelligence','Investment Optimiser','Climate Shock Lab','Decision Intelligence')

class ProfileView(BaseModel):
    """Map a future trusted auth adapter to this presentation-only contract."""
    authenticated: bool = False
    display_name: str = 'Guest workspace'
    initials: str = 'G'
    detail: str = 'Not signed in'

_shell=st.components.v2.component('c1v1c_workspace_shell',
    html='<div id="civic-shell"></div>',
    js=(ROOT/'shell.js').read_text(encoding='utf-8'),isolate_styles=False)

def navigate(page):
    if page in PAGES:
        st.session_state['page']=page

def render_shell():
    st.session_state.setdefault('page','Home')
    st.session_state.setdefault('theme','light')
    profile=ProfileView()  # No authentication service exists in this review build.
    result=_shell(key='workspace_shell',data={'page':st.session_state['page'],'theme':st.session_state['theme'],
        'pages':PAGES,'profile':profile.model_dump()},
        on_action_change=lambda:None,on_appearance_change=lambda:None,height=0)
    if result.action and result.action in PAGES:
        navigate(result.action)
        st.rerun()
    if result.appearance and result.appearance.get('resolved') in ('light','dark'):
        if st.session_state['theme']!=result.appearance['resolved']:
            st.session_state['theme']=result.appearance['resolved']
            st.rerun()
    return st.session_state['page']
