from pathlib import Path
import streamlit as st

def apply_theme():
    css = (Path(__file__).parent/'tokens.css').read_text()
    st.html('<style>'+css+'''
    .stApp {background:var(--color-bg);color:var(--color-text);font-family:var(--font-body)}
    .stMainBlockContainer {max-width:var(--page-width);padding-top:var(--toolbar-clearance);padding-bottom:var(--space-8)}
    [data-testid=stSidebar] {background:var(--color-surface);border-right:var(--border-width) solid var(--color-border)}
    h1 {font-family:var(--font-display)!important;font-weight:400!important;font-size:var(--text-display)!important}
    h2 {font-size:var(--text-xl)!important} h3 {font-size:var(--text-lg)!important}
    h1,h2,h3 {line-height:var(--leading-tight)!important;letter-spacing:var(--tracking-display)!important}
    p,li {line-height:var(--leading-body)}
    [data-testid=stMetricValue] {font-family:var(--font-display);font-variant-numeric:tabular-nums}
    [data-testid=stMetric] {border-top:var(--border-width) solid var(--color-border);padding-top:var(--space-3)}
    .stButton button,.stDownloadButton button,[data-baseweb=select]>div {min-height:var(--control-height)}
    [data-testid=stRadio] label {min-height:var(--control-height);align-items:center}
    [data-testid=stCheckbox] label {min-height:var(--control-height)}
    [data-testid=stCaptionContainer],[data-testid=stCaptionContainer] p {color:var(--color-text-muted)!important;opacity:1!important}
    [data-testid=stMarkdownContainer] p {font-family:var(--font-body)}
    button:focus-visible,a:focus-visible,input:focus-visible {outline:3px solid var(--color-accent)!important;outline-offset:3px}
    @media(max-width:700px){.stMainBlockContainer{padding:var(--toolbar-clearance) var(--space-4) var(--space-4)}h1{font-size:var(--text-xl)!important}}
    </style>''')

def chart_style(fig, title=None):
    fig.update_layout(template='plotly_white', font=dict(family='Trebuchet MS',size=14,color='#202e28'),
        paper_bgcolor='#f4f1e9',plot_bgcolor='#f4f1e9',margin=dict(l=12,r=12,t=45 if title else 15,b=12),
        title=title, colorway=['#245640','#79520b','#526159'],legend=dict(orientation='h',y=-.2))
    return fig
