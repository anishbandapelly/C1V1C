from pathlib import Path
import json
import streamlit as st

ROOT=Path(__file__).parent
PALETTES=json.loads((ROOT/'palette.json').read_text())

def palette():
    return PALETTES[st.session_state.get('theme','light')]

def apply_theme():
    def variables(theme):
        return ''.join('--color-'+k+':'+v+';' for k,v in PALETTES[theme].items() if k!='map-style')
    colors=':root{'+variables('light')+'}@media(prefers-color-scheme:dark){:root:not([data-theme]){'+variables('dark')+'}}'+''.join(':root[data-theme='+t+']{'+variables(t)+'}' for t in PALETTES)
    css=(ROOT/'tokens.css').read_text()+(ROOT/'shell.css').read_text()+(ROOT/'workspace.css').read_text()
    bootstrap="""<script>(()=>{let c='system';try{c=localStorage.getItem('c1v1c-theme')||'system';document.documentElement.dataset.compact=localStorage.getItem('c1v1c-compact')||'false'}catch{};const t=c==='dark'||c==='light'?c:matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light';document.documentElement.dataset.theme=t;document.documentElement.style.colorScheme=t})()</script>"""
    st.html('<style>'+colors+css+'</style>'+bootstrap,unsafe_allow_javascript=True)

def chart_style(fig,title=None):
    p=palette()
    fig.update_layout(template='plotly_dark' if st.session_state.get('theme')=='dark' else 'plotly_white',
        font=dict(family='Outfit',size=14,color=p['text']),paper_bgcolor=p['bg'],plot_bgcolor=p['bg'],
        margin=dict(l=16,r=16,t=45 if title else 20,b=32),title=title,
        colorway=[p['accent'],p['link'],p['muted']],legend=dict(orientation='h',y=-.25),
        hoverlabel=dict(bgcolor=p['surface'],font_color=p['text']))
    fig.update_xaxes(gridcolor=p['rule'],zerolinecolor=p['rule'],automargin=True)
    fig.update_yaxes(gridcolor=p['rule'],zerolinecolor=p['rule'],automargin=True)
    return fig
