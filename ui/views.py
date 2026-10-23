"""Four frontend views; no backend/model execution in this phase."""
import json
from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from .contracts import ScenarioRequest
from .fixtures import LABELS, WEIGHTS, KEYS, PORTFOLIOS, DISPLAY_OUTCOMES, catalogue, zones, preview, ROOT
from .theme import chart_style, palette
from .shell import navigate

def ledger(rows):
    if not rows:
        st.caption('No items selected.')
        return
    # Semantic tables expose all values to assistive technology and theme reliably.
    table=pd.DataFrame(rows).to_html(index=False,escape=True,border=0)
    st.html('<div class="data-ledger" role="region" aria-label="Data table" tabindex="0">'+table+'</div>')

def preflight(title,description,steps):
    st.html('<section class="preflight"><h2>'+escape(title)+'</h2><p>'+escape(description)+'</p><ol>'+''.join('<li>'+escape(s)+'</li>' for s in steps)+'</ol></section>')

def home():
    st.html('''<section class="hero"><div><img class="hero-logo logo-light" src="/app/static/brand/logo-light.png" alt="C1V1C — Tulabhara AI"><img class="hero-logo logo-dark" src="/app/static/brand/logo-dark.png" alt="C1V1C — Tulabhara AI"><p class="hero-kicker">Bengaluru pilot · urban decision intelligence</p><h1>Every investment has a trade-off.</h1><p class="lead">Cooler streets, less flooding, more water. A city needs all three—but land and budgets are finite.</p><p>C1V1C brings risks, investment choices and climate stresses into one evidence-led workspace, so planners can see what a decision costs, who it serves and what it leaves unresolved.</p></div><div class="balance-board"><h2>The sustainability paradox</h2><div class="balance-row"><strong>More tree cover</strong><b>↔</b><span>Irrigation during drought</span></div><div class="balance-row"><strong>Green roofs</strong><b>↔</b><span>Space for water capture</span></div><div class="balance-row"><strong>Better drainage</strong><b>↔</b><span>Downstream capacity</span></div><div class="balance-row"><strong>Limited capital</strong><b>↔</b><span>Benefits across neighbourhoods</span></div><p class="balance-note">Compare the whole decision—not a single environmental score.</p></div></section>''')
    a,b=st.columns([1,1])
    a.button('Explore the pilot',type='primary',on_click=navigate,args=('City Intelligence',),width='stretch')
    b.button('Build an investment preview',on_click=navigate,args=('Investment Optimiser',),width='stretch')
    st.html('''<section class="workflow-strip" aria-label="Planning workflow"><div class="workflow-step"><span>01 / Understand</span><strong>City Intelligence</strong><p>See where risks differ and which inputs still need evidence.</p></div><div class="workflow-step"><span>02 / Allocate</span><strong>Investment Optimiser</strong><p>Compare choices within a budget and inspect who receives investment.</p></div><div class="workflow-step"><span>03 / Stress-test</span><strong>Climate Shock Lab</strong><p>Review a plan under rainfall, drought or a smaller budget.</p></div><div class="workflow-step"><span>04 / Explain</span><strong>Decision Intelligence</strong><p>Keep assumptions, limitations and evidence alongside the decision.</p></div></section>''')
    a,b=st.columns(2)
    a.button('Explore climate scenarios',on_click=navigate,args=('Climate Shock Lab',),width='stretch')
    b.button('Inspect the decision trail',on_click=navigate,args=('Decision Intelligence',),width='stretch')
    with st.expander('What is available in this frontend review?'):
        st.write('All four workflows are interactive previews. Costs and profiles are synthetic fixtures, not observed Bengaluru data. The scientific engine and AI optimisation are not connected yet. Start with City Intelligence or create a display portfolio to inspect the later steps.')

def outcomes(fixture):
    st.caption('Display-only outcome fixture · invented for UI review, not model calculations.')
    vals = DISPLAY_OUTCOMES[fixture]
    cols = st.columns(4)
    for col,label,value in zip(cols,['Peak exceedance reduction · m³/s','Usable water · m³/year','Heat exposure reduction · person-index','Net carbon · tCO₂e / 10 years'],[f'{vals[0]:.2f}',str(vals[1]),str(vals[2]),'Not estimated']):
        col.metric(label,value)

def city():
    st.title('Where does the city need attention?')
    st.write('Compare the Yelahanka fixture profiles, then inspect the evidence behind each indicator.')
    left,right = st.columns([2.2,1], gap='large')
    with left:
        c1,c2=st.columns(2)
        layer=c1.selectbox('Geographic layer',['Heat exposure','Runoff coefficient','Population','Eligible roof','Plantable land','Source coverage'],key='input_layer')
        tiles=c2.toggle('Online street basemap',value=True,help='Uses CARTO / OpenStreetMap tiles. Turn off for the offline coordinate view.',key='input_tiles')
        field={'Heat exposure':'heat_index','Runoff coefficient':'runoff_coefficient','Population':'population','Eligible roof':'suitable_roof_m2','Plantable land':'plantable_land_m2','Source coverage':None}[layer]
        zz=zones()
        values=[float(z[field]) if field else 0 for z in zz]
        # Approximate display markers only. These are NOT zone centroids/boundaries.
        fig=go.Figure(go.Scattermap(lat=[13.106,13.096,13.087],lon=[77.592,77.609,77.586],
            mode='markers+text',text=['A · rain fixture','B · heat fixture','C · water fixture'],
            customdata=['A','B','C'],marker=dict(size=28,color=values,colorscale=[[0,palette()['chart-soft']],[1,palette()['accent']]],showscale=bool(field),colorbar=dict(title=dict(text=layer,side='bottom'),orientation='h',thickness=12)),
            textfont=dict(color=palette()['text']),
            hovertemplate='%{text}<br>Illustrative marker, not a surveyed site<extra></extra>'))
        fig.update_layout(map=dict(style=palette()['map-style'] if tiles else {'version':8,'sources':{},'layers':[{'id':'background','type':'background','paint':{'background-color':palette()['surface']}}]},center=dict(lat=13.097,lon=77.596),zoom=12),height=410)
        chart_style(fig)
        st.plotly_chart(fig,width='stretch',key='pilot_map',config={'displayModeBar':False,'scrollZoom':True})
        st.caption('Yelahanka context · WGS84. Pan, zoom or hover; use the profile selector to inspect A/B/C. Markers are illustrative, not verified boundaries.')
        if not tiles:
            st.info('Offline coordinate view: street tiles are disabled. Marker positions are display assumptions only.')
    with right:
        zone=st.selectbox('Neighbourhood fixture',['A','B','C'],format_func=lambda x:{'A':'A — Rain stress','B':'B — Heat stress','C':'C — Water stress'}[x],key='input_zone')
        z=next(z for z in zz if z['zone_id']==zone)
        st.subheader('Planning profile')
        st.caption('D · synthetic fixture / no observation date')
        st.metric('Residents · illustrative',f"{int(z['population']):,}")
        st.metric('Heat exposure index · 0–1',z['heat_index'])
        ledger([{'Resource':'Area','Availability':z['area_ha']+' ha'},
                {'Resource':'Suitable roof','Availability':z['suitable_roof_m2']+' m²'},
                {'Resource':'Plantable land','Availability':z['plantable_land_m2']+' m²'},
                {'Resource':'Drainage capacity','Availability':z['drainage_capacity_m3_s']+' m³/s'}])
        st.caption('No surveyed eligibility, structural capacity or official neighbourhood boundaries have been verified.')
    st.subheader('Risk indicators & evidence')
    ledger([{'Indicator':'Runoff coefficient','Value':z['runoff_coefficient'],'Unit':'dimensionless','Source':'Master §3.4','Status':'D · synthetic'},
            {'Indicator':'Heat exposure','Value':z['heat_index'],'Unit':'index 0–1, not °C','Source':'Master §3.4','Status':'D · synthetic'},
            {'Indicator':'Water demand','Value':'Not available','Unit':'m³ / period','Source':'Missing','Status':'Blocks water model'},
            {'Indicator':'Carbon factors','Value':'Not available','Unit':'tCO₂e / pathway','Source':'Missing','Status':'Not estimated'}])
    with st.expander('Candidate sites and physical availability'):
        ledger([{k:v for k,v in row.items() if k!='type'} for row in catalogue() if row['Zone']==zone])
        st.warning('All candidate locations and eligibility are unverified. The frontend catalogue is not an engineering suitability assessment.')
    with st.expander('Source register · leads, coverage and provenance'):
        st.write('Verified pilot coverage: no downloaded, validated Bengaluru inputs in this repository yet.')
        ledger(pd.read_csv(ROOT/'data/source_registry.csv').fillna('Not recorded').to_dict('records'))
        st.download_button('Download source register',(ROOT/'data/source_registry.csv').read_bytes(),'source-register.csv','text/csv')

def optimiser():
    st.title('What can your investment include?')
    st.write('Set the budget, choose a display portfolio and compare its costs before reviewing the trade-offs.')
    controls,result=st.columns([1,1.65],gap='large')
    with controls:
        st.subheader('Investment envelope')
        budget=st.number_input('Capital budget · INR crore',min_value=0.0,max_value=100.0,value=2.0,step=.1,key='budget')
        mode=st.selectbox('Priority mode',list(WEIGHTS),key='mode')
        with st.expander('Inspect or edit objective weights'):
            raw=[st.number_input(label+' weight · %',0,100,v,key=f'{mode}-{k}') for k,label,v in zip(KEYS,['Flood','Water','Heat','Carbon','Equity','Lifecycle cost'],WEIGHTS[mode])]
            total=sum(raw)
            st.caption(f'Total: {total}%. Must equal 100%. These are policy preferences, not extra physical benefits.')
        types=st.multiselect('Interventions to consider',list(LABELS),default=list(LABELS),format_func=LABELS.get,key='input_types')
        with st.expander('Equity safeguard'):
            floor=st.slider('Priority-zone benefit floor · normalised',0.0,1.0,0.0,.05,help='Future hard constraint. The display fixture cannot verify a nonzero floor.',key='input_floor')
        fixture=st.selectbox('Display portfolio',list(PORTFOLIOS),help='Manually authored examples, not computed recommendations.',key='input_fixture')
        with st.expander('Frontend review states'):
            view_state=st.selectbox('Review state',['Ready','Loading example','Infeasible example','Service error example','Missing data example'],help='Explicit frontend QA controls; no service is contacted.',key='input_review_state')
        clicked=st.button('Preview allocation',type='primary',width='stretch')
        st.caption('No optimiser is connected in this review build. Only the displayed project cost is summed.')
    request=None
    if total==100:
        request=ScenarioRequest(budget_inr=budget*10_000_000,weights=dict(zip(KEYS,[v/100 for v in raw])),equity_floor=floor,allowed_interventions=tuple(types))
    if clicked:
        st.session_state.pop('active_preview',None)
        if not request: st.session_state['preview_error']='Objective weights must add up to 100%.'
        elif floor>0: st.session_state['preview_error']='This frontend fixture cannot verify a benefit floor. Set zero to inspect the layout; hard equity constraints require the backend.'
        elif view_state=='Ready':
            try:
                snap=preview(request,fixture)
                st.session_state['active_preview']=snap
                st.session_state.setdefault('history',{})[snap.preview_id]=snap
                st.session_state.pop('preview_error',None)
            except ValueError as e: st.session_state['preview_error']=str(e)
    with result:
        st.subheader('Allocation ledger')
        if view_state=='Loading example':
            st.info('Loading state demonstration · awaiting a future engine response.')
            st.progress(35,text='Example progress only — no model running')
            return
        if view_state=='Infeasible example':
            st.error('Infeasible state example: priority-zone benefit floor exceeds eligible capacity. No constraints were relaxed.')
            st.write('Recovery: review the threshold, candidate eligibility and budget before requesting a new run.')
            return
        if view_state=='Service error example':
            st.error('Service failure example: no result available. Previous saved previews remain accessible in Decision Intelligence.')
            if st.button('Dismiss service error example'): st.info('Select Ready and preview again. No external request was sent.')
            return
        if view_state=='Missing data example':
            st.warning('Missing data example: rainfall time series and site eligibility are unavailable. Water and feasibility outputs must remain blocked.')
            return
        if st.session_state.get('preview_error'): st.error(st.session_state['preview_error'])
        snap=st.session_state.get('active_preview')
        if not snap:
            preflight('Start with the investment envelope','A useful plan makes its constraints visible before showing any outcomes.',[
                'Set the capital budget and choose which interventions to consider.',
                'Choose a display portfolio and preview its total cost.',
                'Compare alternatives, then take the saved selection into Climate Shock Lab.'])
            st.subheader('The four choices in this catalogue')
            ledger([{'Intervention':LABELS[t],'Unit cost · INR lakh':v/100000,'Main constraint':c} for t,v,c in [('green_roof',3000000,'Shared roof area'),('urban_forest',2000000,'Land and irrigation'),('rainwater_harvesting',1200000,'Catchment and storage'),('drainage_upgrade',5000000,'Eligible drainage asset')]])
            st.caption('Synthetic catalogue · Master §5.1a. Preview checks costs only; it does not solve or validate environmental outcomes.')
            return
        stale=(request is None or request!=snap.request or fixture!=snap.fixture_name)
        if stale: st.warning('Inputs changed. Showing the saved preview below; use Preview allocation to apply current controls.')
        st.caption(snap.preview_id+' · solver: NOT RUN')
        c1,c2,c3=st.columns(3)
        c1.metric('Capital · INR crore',f'{snap.cost_inr/10_000_000:.2f}')
        c2.metric('Unallocated · INR crore',f'{(snap.request.budget_inr-snap.cost_inr)/10_000_000:.2f}')
        c3.metric('Projects in preview',len(snap.selected_ids))
        chosen=[r for r in catalogue() if r['ID'] in snap.selected_ids]
        if chosen:
            ledger([{k:v for k,v in r.items() if k!='type'} for r in chosen])
            fig=go.Figure(go.Bar(x=[r['Capital · INR']/1e6 for r in chosen],y=[r['ID'] for r in chosen],orientation='h',marker_color=palette()['accent']))
            fig.update_layout(xaxis_title='Capital cost · INR million',height=280)
            st.plotly_chart(chart_style(fig),width='stretch')
        else: st.info('No projects selected. Zero investment is a valid display baseline.')
        complete=tuple(PORTFOLIOS[snap.fixture_name])==snap.selected_ids
        if complete: outcomes(snap.fixture_name)
        else: st.warning('Intervention filter changed the example portfolio. Outcome fixtures are withheld to avoid attaching unrelated benefits to this selection.')
        with st.expander('Constraint review and model boundary'):
            ledger([{'Constraint':'Capital budget','Status':'Checked against fixture costs'},
                    {'Constraint':'Roof / land / eligibility','Status':'Awaiting engine validation'},
                    {'Constraint':'Equity floor','Status':'Not evaluated'},
                    {'Constraint':'Lifecycle cost / carbon','Status':'Not estimated — coefficients missing'}])
            st.write('No global optimum, Pareto frontier or physical feasibility is claimed by this preview.')
        st.subheader('Compare alternative display portfolios')
        comparisons=st.multiselect('Alternatives',list(PORTFOLIOS),default=['Water emphasis','No investment'])
        rows=[]
        for name in comparisons:
            ids=PORTFOLIOS[name]
            cost=sum(r['Capital · INR'] for r in catalogue() if r['ID'] in ids)
            rows.append({'Plan':name,'Capital · INR':cost,'Within entered budget':cost<=snap.request.budget_inr,'Status':'Display fixture · not an evaluated baseline'})
        if rows: ledger(rows)
        if comparisons:
            st.caption('Outcome comparison specimen · manually authored UI values, not evaluated alternatives. All fixtures use the same display units; carbon is withheld.')
            metric=st.selectbox('Comparison metric',['Peak exceedance reduction · m³/s','Usable water · m³/year','Heat exposure reduction · person-index'])
            idx=['Peak exceedance reduction · m³/s','Usable water · m³/year','Heat exposure reduction · person-index'].index(metric)
            fig=go.Figure(go.Bar(x=comparisons,y=[DISPLAY_OUTCOMES[n][idx] for n in comparisons],marker_color=palette()['accent']))
            fig.update_layout(yaxis_title=metric,height=280)
            st.plotly_chart(chart_style(fig),width='stretch')

def shock_lab():
    st.title('Will the plan hold under pressure?')
    st.write('Keep the original selection fixed, change one stress condition and inspect what must be reconsidered.')
    snap=st.session_state.get('active_preview')
    if not snap:
        preflight('First, give the lab a plan to test','The comparison needs a saved selection so the original plan cannot quietly change during a stress test.',[
            'Extreme rainfall: inspect runoff and drainage capacity under a stronger storm.',
            'Drought: examine water availability, irrigation and cooling assumptions.',
            'Budget cut: check the revised envelope while retaining committed costs.'])
        st.button('Create an investment preview',type='primary',on_click=navigate,args=('Investment Optimiser',))
        st.caption('No scenario has run. These are user-defined stress conditions, not forecasts.')
        return
    st.caption('Frozen original selection: '+snap.preview_id)
    c1,c2=st.columns([1,2],gap='large')
    with c1:
        shock=st.selectbox('Disruption',['Extreme rainfall','Drought','Sudden budget cut'])
        if shock=='Extreme rainfall':
            factors={'rainfall_multiplier':st.slider('Storm intensity multiplier',1.0,2.5,1.3,.05)}
        elif shock=='Drought':
            factors={'rainfall_factor':st.slider('Rainfall availability factor',0.0,1.0,.6,.05),
                     'cooling_factor':st.slider('Tree cooling retention factor',0.0,1.0,.7,.05)}
        else:
            factors={'budget_factor':st.slider('Retained budget · fraction',0.0,1.0,.7,.05)}
        commitments=st.multiselect('Committed projects',list(snap.selected_ids),help='Future replanning must retain these projects and account for obligated capital.')
        st.caption('User-defined stress assumptions, not forecasts. Environmental effects await the Python engine.')
        if st.button('Preview shock comparison',type='primary'):
            st.session_state['shock_preview']={'original_id':snap.preview_id,'shock':shock,'factors':factors,'commitments':commitments,'ids':list(snap.selected_ids)}
    with c2:
        saved=st.session_state.get('shock_preview')
        if not saved or saved['original_id']!=snap.preview_id:
            preflight('One original plan. Two comparisons.','Submit the stress settings to preserve a clear before-and-after record.',[
                'Original plan: the saved budget and selected project IDs.',
                'Original under shock: the same selection against changed conditions.',
                'Replanned alternative: reserved for a separately computed solver result after integration.'])
            st.caption('Your current selection stays frozen. Parameter records and budget arithmetic work now; environmental calculations remain unavailable.')
            return
        if saved['shock']!=shock or saved['factors']!=factors or saved['commitments']!=commitments:
            st.warning('Stress controls changed. The table retains the last submitted preview.')
        st.subheader(saved['shock']+' · comparison')
        st.caption('No scenario model or reoptimisation has run. The same original project IDs are preserved.')
        revised=snap.request.budget_inr*saved['factors'].get('budget_factor',1)
        committed_cost=sum(r['Capital · INR'] for r in catalogue() if r['ID'] in saved['commitments'])
        ledger([{'Measure':'Capital envelope · INR','Original plan':f'{snap.request.budget_inr:,.0f}','Original under shock':f'{revised:,.0f}','Reoptimised alternative':'Awaiting solver'},
                {'Measure':'Project selection','Original plan':', '.join(snap.selected_ids) or 'None','Original under shock':'Unchanged','Reoptimised alternative':'Not computed'},
                {'Measure':'Runoff / water / heat','Original plan':'Display fixtures only','Original under shock':'Not evaluated','Reoptimised alternative':'Not evaluated'},
                {'Measure':'Carbon · 10 years','Original plan':'Not estimated','Original under shock':'Not estimated','Reoptimised alternative':'Not estimated'}])
        if snap.cost_inr>revised: st.error('Original fixture portfolio exceeds the revised capital envelope. This is a budget check, not a solver feasibility result.')
        if committed_cost>revised: st.error('Committed fixture cost exceeds the revised envelope; commitments cannot be silently removed.')
        st.metric('Remaining after commitments · INR',f'{revised-committed_cost:,.0f}')
        fig=go.Figure(go.Bar(x=['Original envelope','Revised envelope','Original fixture cost'],y=[snap.request.budget_inr/1e6,revised/1e6,snap.cost_inr/1e6],marker_color=[palette()['muted'],palette()['accent'],palette()['warning']]))
        fig.update_layout(yaxis_title='INR million',height=280)
        st.plotly_chart(chart_style(fig),width='stretch')
        with st.expander('Inspect environmental comparison layout · static demonstration'):
            st.warning('The following values are invented layout specimens. They do not respond to stress parameters and are not results for your saved selection.')
            metric=st.selectbox('Shock comparison specimen',['Peak exceedance · m³/s','Usable water · m³/year','Heat exposure · person-index'])
            examples={'Peak exceedance · m³/s':[.3,.5,.35],'Usable water · m³/year':[270,160,190],'Heat exposure · person-index':[900,1100,950]}
            labels=['Original / normal','Original / shock','Replanned / shock']
            fig=go.Figure(go.Bar(x=labels,y=examples[metric],marker_color=[palette()['muted'],palette()['warning'],palette()['accent']]))
            fig.update_layout(yaxis_title=metric,height=290)
            st.plotly_chart(chart_style(fig),width='stretch')
            ledger([{'State':label,metric:value,'Evidence':'D · UI specimen'} for label,value in zip(labels,examples[metric])])
            st.write('Project change specimen: retain A drainage; add C harvesting; defer B forest. These are layout examples only, not changes to the frozen selection.')
        with st.expander('Parameter record and required model updates'):
            st.json(saved)
            st.write({'Extreme rainfall':'Recompute peak runoff and capacity exceedance while keeping the original project counts frozen.',
                      'Drought':'Recompute tank time series, irrigation demand and bounded heat exposure effects.',
                      'Sudden budget cut':'Re-solve with the revised envelope, preserving commitments and explicitly reporting overspend.'}[saved['shock']])

def decisions():
    st.title('What supports this decision?')
    st.write('Follow the selection, its distribution and its evidence before exporting a review brief.')
    history=st.session_state.get('history',{})
    if not history:
        preflight('A decision trail starts with a selection','Save an allocation preview to inspect the reasons, assumptions and distribution in one place.',[
            'Selection: which projects are included, and what do their fixture costs add up to?',
            'Distribution: how much investment reaches each synthetic neighbourhood?',
            'Evidence: what is known, what is assumed and what must be validated?'])
        st.button('Build the first decision preview',type='primary',on_click=navigate,args=('Investment Optimiser',))
        with st.expander('What will the exported brief contain?'):
            st.write('The saved preview ID, budget, selected projects, objective weights, source and model versions, and explicit limitations. Export never upgrades demonstration values into measured results.')
        return
    selected=st.selectbox('Saved preview',list(history),format_func=lambda k:f'{history[k].fixture_name} / {k}')
    snap=history[selected]
    st.caption('Session-only review snapshot · '+snap.data_mode+' · solver NOT RUN')
    c1,c2=st.columns([1.5,1],gap='large')
    with c1:
        st.subheader('What this selection means')
        st.write(f'The manually authored {snap.fixture_name.lower()} example contains {len(snap.selected_ids)} projects with fixture capital costs totalling INR {snap.cost_inr:,.0f}. It is not a recommendation.')
        project=st.selectbox('Inspect selected or excluded project',[r['ID'] for r in catalogue()])
        if project in snap.selected_ids:
            st.info('Included by the selected display fixture. A computed marginal contribution, binding constraint and counterfactual explanation will appear here after engine integration.')
        else:
            st.info('Absent from the display fixture or filtered by intervention selection. No optimisation rejection reason is claimed.')
        st.subheader('Whose neighbourhood receives investment?')
        rows=[]
        for z in zones():
            amount=sum(r['Capital · INR'] for r in catalogue() if r['ID'] in snap.selected_ids and r['Zone']==z['zone_id'])
            rows.append({'Zone':z['zone_id'],'Residents · synthetic':int(z['population']),'Capital · INR':amount,'INR / resident':round(amount/int(z['population']),2),'Environmental benefit':'Not evaluated'})
        ledger(rows)
        st.caption('Investment per resident is not an equity outcome. Population-weighted environmental benefits and residual risks require the evaluator.')
        st.subheader('Declared priorities')
        fig=go.Figure(go.Bar(x=list(snap.request.weights),y=list(snap.request.weights.values()),marker_color=palette()['accent']))
        fig.update_layout(yaxis_title='Requested objective weight',height=260)
        st.plotly_chart(chart_style(fig),width='stretch')
        st.caption('Weights are shown, not score contributions. Contribution and constraint-slack data are unavailable until the solver runs.')
    with c2:
        st.subheader('Uncertainty & consequences')
        for title,body in [
            ('Evidence limits','All three profiles and costs are synthetic. No local construction quotation, field eligibility or observed climate series has been validated.'),
            ('Water and maintenance','Trees can require irrigation during drought. Ongoing maintenance and lifecycle cost must accompany capital allocations.'),
            ('Shared physical capacity','Green roofs and harvesting share roof resources. Drainage increases conveyance and must not be counted as reduced runoff generation.'),
            ('Distribution and displacement','Unequal access to greening and possible displacement are risks to investigate, not predicted neighbourhood outcomes.'),
            ('Sensitivity, not confidence','Future coefficient low/high tests are sensitivity ranges, not calibrated confidence intervals. Carbon remains not estimated.')]:
            with st.expander(title,expanded=title=='Evidence limits'):st.write(body)
        st.subheader('Evidence lineage')
        st.write('Source: Master plan §§3.4, 5.1a. Grade D. Observation date: none. Geometry: illustrative. Dataset: synthetic-v1. Model: not implemented.')
        st.caption('AWS: not connected · Bedrock: not invoked. No cloud action occurs in the frontend review.')
    with st.expander('Compare saved preview inputs'):
        others=st.multiselect('Saved previews to compare',list(history),default=[selected])
        ledger([{'Preview':k,'Fixture':history[k].fixture_name,'Budget · INR':history[k].request.budget_inr,'Capital · INR':history[k].cost_inr,'Solver':'not_run'} for k in others])
    st.subheader('Decision summary')
    brief=f'''# C1V1C — frontend review brief

DEMONSTRATION DATA — not observed Bengaluru conditions.
Preview: {snap.preview_id}
Fixture: {snap.fixture_name}
Capital budget: INR {snap.request.budget_inr:,.0f}
Selected fixture cost: INR {snap.cost_inr:,.0f}
Projects: {', '.join(snap.selected_ids) or 'None'}
Weights: {json.dumps(snap.request.weights)}
Source: Master plan §§3.4 / 5.1a; grade D, no observation date.
Baseline: {snap.request.baseline_version}; catalogue: {snap.request.project_catalog_version}.
Model: not implemented; solver: NOT RUN.
No scientific feasibility, environmental impact or optimality is claimed.
Costs are synthetic. Carbon, LCC and environmental benefits are not evaluated.
Review site eligibility, rainfall timing, shared roof limits and population-weighted equity before a planning decision.
'''
    a,b=st.columns(2)
    a.download_button('Export review brief · Markdown',brief,f'{selected}.md','text/markdown',width='stretch')
    b.download_button('Export preview snapshot · JSON',snap.model_dump_json(indent=2),f'{selected}.json','application/json',width='stretch')
    with st.expander('Inspect saved contract'):st.json(snap.model_dump())
