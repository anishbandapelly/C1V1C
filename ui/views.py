"""Four workspace views wired to the C1V1C engine (data engine, MILP, scenarios, explainer)."""
import json
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from c1v1c.schemas import METRIC_UNITS, METRICS, RunRequest
from .backend import (KEYS, LABELS, SHOCKS, WEIGHT_LABELS, candidate_label, engine, evidence_text, explanation_for,
                      fmt_value, save_comparison, save_run, weights_pct, zone_names)
from .budget import budget_input
from .shell import navigate
from .theme import chart_style, palette

METRIC_TITLES = {'F': 'Flood · design-event runoff retained or conveyed', 'W': 'Water · usable water, net of irrigation',
                 'H': 'Heat · exposure reduction', 'G': 'Carbon · forest sequestration, 10 yr'}
SHORT_UNITS = {'F': 'm³ / event', 'W': 'm³ / yr', 'H': 'person-index', 'G': 'tCO₂e / 10 yr'}
STATUS_TEXT = {'optimal': 'Optimal (CBC, proven)', 'feasible_time_limit': 'Feasible (time limit reached, not proven optimal)',
               'infeasible': 'No feasible portfolio', 'error': 'Solver or verification error', 'not_run': 'Not run'}


def ledger(rows):
    if not rows:
        st.caption('No items selected.')
        return
    # Semantic tables expose all values to assistive technology and theme reliably.
    table = pd.DataFrame(rows).to_html(index=False, escape=True, border=0)
    st.html('<div class="data-ledger" role="region" aria-label="Data table" tabindex="0">' + table + '</div>')


def preflight(title, description, steps):
    st.html('<section class="preflight"><h2>' + escape(title) + '</h2><p>' + escape(description) + '</p><ol>'
            + ''.join('<li>' + escape(s) + '</li>' for s in steps) + '</ol></section>')


def crore(v):
    return f'{v / 10_000_000:,.2f}'


def num(v, digits=1):
    if v is None:
        return 'Not estimated'
    return f'{v:,.{digits}f}'


def engine_unavailable():
    st.error('The decision engine could not load its Bengaluru baseline. ' + st.session_state.get('engine_error', '')
             + ' Run `python -m c1v1c.pipeline` to rebuild the curated inputs. No results are shown rather than placeholders.')


def home():
    st.html('''<section class="hero"><div><img class="hero-logo logo-light" src="/app/static/brand/logo-light.png" alt="C1V1C — Tulabhara AI"><img class="hero-logo logo-dark" src="/app/static/brand/logo-dark.png" alt="C1V1C — Tulabhara AI"><p class="hero-kicker">Bengaluru pilot · urban decision intelligence</p><h1>Every investment has a trade-off.</h1><p class="lead">Cooler streets, less flooding, more water. A city needs all three—but land and budgets are finite.</p><p>C1V1C brings risks, investment choices and climate stresses into one evidence-led workspace, so planners can see what a decision costs, who it serves and what it leaves unresolved.</p></div><div class="balance-board"><h2>The sustainability paradox</h2><div class="balance-row"><strong>More tree cover</strong><b>↔</b><span>Irrigation during drought</span></div><div class="balance-row"><strong>Green roofs</strong><b>↔</b><span>Space for water capture</span></div><div class="balance-row"><strong>Better drainage</strong><b>↔</b><span>Downstream capacity</span></div><div class="balance-row"><strong>Limited capital</strong><b>↔</b><span>Benefits across neighbourhoods</span></div><p class="balance-note">Compare the whole decision—not a single environmental score.</p></div></section>''')
    a, b = st.columns([1, 1])
    a.button('Explore the pilot', type='primary', on_click=navigate, args=('City Intelligence',), width='stretch')
    b.button('Build an investment plan', on_click=navigate, args=('Investment Optimiser',), width='stretch')
    st.html('''<section class="workflow-strip" aria-label="Planning workflow"><div class="workflow-step"><span>01 / Understand</span><strong>City Intelligence</strong><p>See where risks differ and which inputs still need evidence.</p></div><div class="workflow-step"><span>02 / Allocate</span><strong>Investment Optimiser</strong><p>Compare choices within a budget and inspect who receives investment.</p></div><div class="workflow-step"><span>03 / Stress-test</span><strong>Climate Shock Lab</strong><p>Review a plan under rainfall, drought or a smaller budget.</p></div><div class="workflow-step"><span>04 / Explain</span><strong>Decision Intelligence</strong><p>Keep assumptions, limitations and evidence alongside the decision.</p></div></section>''')
    a, b = st.columns(2)
    a.button('Explore climate scenarios', on_click=navigate, args=('Climate Shock Lab',), width='stretch')
    b.button('Inspect the decision trail', on_click=navigate, args=('Decision Intelligence',), width='stretch')
    with st.expander('What is real in this pilot, and what is assumed?'):
        st.write('Ward boundaries and population (GBA, Dec 2025), building footprints (Microsoft ML), flood hazard markers, '
                 'storm-water drains, tanks and ponds, and IMD rainfall and temperature grids are real Bengaluru data. '
                 'Intervention unit costs, retention, tank sizes, conveyance gains and eligible-area fractions are declared '
                 'planning assumptions from the master plan. Every result is a modelled screening estimate computed by a '
                 'mixed-integer optimiser, labelled with its evidence class—not a validated engineering forecast.')


def city():
    eng = engine()
    if eng is None:
        return engine_unavailable()
    b = eng.baseline
    st.title('Where does the city need attention?')
    st.write('Compare three real Yelahanka-zone wards, then inspect the evidence behind each indicator.')
    names = zone_names(eng)
    left, right = st.columns([2.2, 1], gap='large')
    layers = {'Heat exposure': 'heat_index', 'Runoff coefficient': 'runoff_coefficient', 'Population': 'population',
              'Eligible roof': 'eligible_roof_m2', 'Plantable land': 'plantable_land_m2', 'Flood hazard markers': 'flood_points',
              'Source coverage': None}
    with left:
        c1, c2 = st.columns(2)
        layer = c1.selectbox('Geographic layer', list(layers), key='input_layer')
        tiles = c2.toggle('Online street basemap', value=True, key='input_tiles')
        field = layers[layer]
        ids = [z.zone_id for z in b.zones]
        if field:
            values = [getattr(z, field).value for z in b.zones]
            unit = getattr(b.zones[0], field).unit
        else:  # share of zone indicators backed by observed or derived evidence
            values = [sum(1 for f in ('area_ha', 'population', 'built_fraction', 'runoff_coefficient', 'design_p24_mm',
                                      'summer_tmax_c', 'flood_points', 'drain_length_m', 'eligible_roof_m2', 'plantable_land_m2')
                          if getattr(z, f).evidence.value in ('observed', 'derived')) / 10 for z in b.zones]
            unit = 'share of indicators observed or derived'
        p = palette()
        fig = go.Figure(go.Choroplethmap(
            geojson=b.geojson, locations=ids, featureidkey='properties.zone_id', z=values,
            colorscale=[[0, p['chart-soft']], [1, p['accent']]], marker_opacity=0.65, marker_line_width=1.5,
            marker_line_color=p['text'], text=[names[i] for i in ids],
            colorbar=dict(title=dict(text=f'{layer} · {unit}', side='bottom'), orientation='h', thickness=12),
            hovertemplate='%{text}<br>' + layer + ': %{z:,.3~f}<extra></extra>'))
        sites = b.sites[(b.sites['usable_for_counts'] == True) & b.sites['pilot_zone_id'].notna()]  # noqa: E712
        if len(sites):
            fig.add_trace(go.Scattermap(lat=sites['lat'], lon=sites['lon'], mode='markers', name='Flood hazard marker',
                                        marker=dict(size=10, color=p['danger']),
                                        text=sites['name'].fillna(sites['point_class']),
                                        hovertemplate='%{text}<br>Hazard marker (not a construction site)<extra></extra>'))
        lat = sum(z.centroid_lat for z in b.zones) / 3
        lon = sum(z.centroid_lon for z in b.zones) / 3
        fig.update_layout(map=dict(style=p['map-style'] if tiles else {'version': 8, 'sources': {}, 'layers': [
            {'id': 'background', 'type': 'background', 'paint': {'background-color': p['surface']}}]},
            center=dict(lat=lat, lon=lon), zoom=12.3), height=430, showlegend=bool(len(sites)))
        chart_style(fig)
        st.plotly_chart(fig, width='stretch', key='pilot_map', config={'displayModeBar': False, 'scrollZoom': True})
        st.caption('GBA 369-ward boundaries (Dec 2025) · WGS84. Red points are validated flood / low-lying hazard markers, '
                   'not verified construction sites. Climate inputs come from one IMD grid cell shared by all three wards.')
        if not tiles:
            st.info('Offline view: street tiles are disabled; ward polygons are still drawn from the boundary file.')
    with right:
        zone = st.selectbox('Pilot ward', ids, format_func=lambda x: f'{x} — {names[x]}', key='input_zone')
        z = b.zone(zone)
        st.header('Planning profile')
        st.caption(z.selection_reason)
        st.metric('Residents · GBA delimitation', f'{int(z.population.value):,}')
        st.caption(z.population.note)
        st.metric('Heat exposure index · 0–1', f'{z.heat_index.value:.3f}')
        ledger([{'Resource': 'Area', 'Availability': f'{z.area_ha.value:,.1f} ha', 'Evidence': evidence_text(z.area_ha)},
                {'Resource': 'Eligible roof', 'Availability': f'{z.eligible_roof_m2.value:,.0f} m²', 'Evidence': evidence_text(z.eligible_roof_m2)},
                {'Resource': 'Plantable land', 'Availability': f'{z.plantable_land_m2.value:,.0f} m²', 'Evidence': evidence_text(z.plantable_land_m2)},
                {'Resource': 'Drainage capacity', 'Availability': 'Not available', 'Evidence': '– · Missing'}])
        st.caption('Eligible roof and land are assumed fractions of mapped area. Structural capacity, ownership and drain '
                   'hydraulic capacity have not been surveyed.')
    st.header('Risk indicators & evidence')
    rows = []
    for label, f in [('Population', 'population'), ('SC/ST population share', 'sc_st_share'), ('Built-up (footprint) fraction', 'built_fraction'),
                     ('Impervious fraction', 'impervious_fraction'), ('Runoff coefficient', 'runoff_coefficient'),
                     ('Mean annual max daily rainfall', 'design_p24_mm'), ('Design storm depth', 'design_event_mm'),
                     ('Design-event runoff volume', 'design_event_runoff_m3'), ('Summer max temperature', 'summer_tmax_c'),
                     ('Heat exposure index', 'heat_index'), ('Flood hazard markers', 'flood_points'), ('Storm-water drain length', 'drain_length_m'),
                     ('Tanks and ponds', 'waterbody_features'), ('Vulnerability weight', 'vulnerability_weight')]:
        q = getattr(z, f)
        rows.append({'Indicator': label, 'Value': fmt_value(q, 3), 'Unit': q.unit, 'Evidence': evidence_text(q),
                     'Source': ', '.join(q.source_ids) or '—', 'Basis': q.note or q.missing_reason or ''})
    rows.append({'Indicator': 'Ward water demand', 'Value': 'Not available', 'Unit': 'm³ / day', 'Evidence': '– · Missing',
                 'Source': '—', 'Basis': 'City-level supply tables cannot be allocated to wards defensibly'})
    ledger(rows)
    st.header('Compare the three pilot wards')
    ledger([{'Ward': f'{w.zone_id} — {w.name}', 'Residents': f'{int(w.population.value):,}', 'Area · ha': f'{w.area_ha.value:,.1f}',
             'Built fraction': f'{w.built_fraction.value:.2f}', 'Hazard markers': int(w.flood_points.value),
             'Drains · km': f'{w.drain_length_m.value / 1000:.2f}', 'Runoff · m³ / event': f'{w.design_event_runoff_m3.value:,.0f}',
             'SC/ST share': f'{w.sc_st_share.value:.1%}', 'Heat index': f'{w.heat_index.value:.3f}'} for w in b.zones])
    st.header('Historical climate')
    rain = b.rain[z.rainfall_cell]
    annual = pd.DataFrame({'year': rain.years, 'mm': rain.rain_mm}).groupby('year')['mm'].sum()
    fig = go.Figure(go.Bar(x=annual.index, y=annual.values, marker_color=palette()['accent'], name='Annual rainfall'))
    fig.add_hline(y=float(annual.mean()), line_dash='dash', line_color=palette()['muted'],
                  annotation_text=f'1971–2005 mean {annual.mean():,.0f} mm')
    fig.update_layout(yaxis_title='mm / year', height=280)
    st.plotly_chart(chart_style(fig), width='stretch', key='rain_history')
    st.caption(f'Observed IMD 0.5° gridded daily rainfall, cell {z.rainfall_cell} (1971–2005; dates reconstructed from the '
               'source file header). Historical observations, not a forecast. No 2006–2025 gridded series is in the collection.')
    with st.expander('Candidate projects and physical availability'):
        ledger([{'Candidate': candidate_label(eng, c.candidate_id), 'Max units': c.upper_bound, 'Eligibility': c.eligibility,
                 'Reason': c.eligibility_reason, 'Capital · INR': f'{c.capex_inr:,.0f}', 'Roof · m²': c.roof_m2,
                 'Land · m²': c.land_m2, 'Evidence': 'D · Assumed unit'} for c in eng.all_candidates if c.zone_id == zone])
        pts = b.sites[(b.sites['pilot_zone_id'] == zone)]
        if len(pts):
            st.caption('Hazard markers inside this ward (exposure evidence, not intervention sites):')
            ledger(pts[['site_id', 'point_class', 'name', 'lat', 'lon', 'duplicate_of']].fillna('—').to_dict('records'))
        st.warning('Candidate units are planning units, not surveyed sites. Eligibility here means "within assumed area"; '
                   'it does not certify engineering suitability.')
    with st.expander('Source register · coverage, quality checks and provenance'):
        st.write(f'Baseline {b.version} · {b.data_mode.value} · checksum {b.sha256[:12]}')
        ledger(b.provenance[['source_id', 'dataset_name', 'observation_period', 'spatial_resolution', 'evidence_class', 'licence']]
               .rename(columns={'source_id': 'Source', 'dataset_name': 'Dataset', 'observation_period': 'Period',
                                'spatial_resolution': 'Resolution', 'evidence_class': 'Class', 'licence': 'Licence / caveat'})
               .to_dict('records'))
        st.caption('Data-quality checks run by the pipeline:')
        ledger([{'Dataset': c['dataset'], 'Check': c['check'], 'Status': c['status'], 'Detail': c['detail']} for c in b.quality['checks']])
        st.download_button('Download provenance register', b.provenance.to_csv(index=False), 'provenance.csv', 'text/csv')


def optimiser():
    eng = engine()
    if eng is None:
        return engine_unavailable()
    st.title('What can your investment include?')
    st.write('Set the budget and priorities, then let the mixed-integer optimiser choose a feasible combination.')
    presets = weights_pct(eng)
    controls, result = st.container(), st.container()
    with controls:
        st.header('Investment envelope')
        envelope, preferences = st.columns(2, gap='large')
        with envelope:
            budget = budget_input()
        with preferences:
            mode = st.selectbox('Priority mode', list(presets), key='mode')
            with st.expander('Inspect or edit objective weights'):
                raw = [st.number_input(label + ' weight · %', 0, 100, v, key=f'{mode}-{k}')
                       for k, label, v in zip(KEYS, WEIGHT_LABELS, presets[mode])]
                total = sum(raw)
                st.caption(f'Total: {total}%. Must equal 100%. These are policy preferences, not extra physical benefits.')
        st.header('Interventions to consider')
        st.caption('One planning unit per intervention per ward (12 candidates, master plan §5.2). Costs and effects are '
                   'declared assumptions; selection does not certify site feasibility.')
        types = []
        for kind, label in LABELS.items():
            s = eng.specs[kind]
            with st.container(key='intervention_' + kind):
                included = st.checkbox(label, value=True, key='input_include_' + kind)
                if included:
                    types.append(kind)
                detail = {'green_roof': f'retains {s.retention_depth_mm:g} mm per event · {s.roof_m2:g} m² shared roof',
                          'urban_forest': f'{s.land_m2:g} m² planting · {s.irrigation_m3_month:g} m³/month irrigation',
                          'rainwater_harvesting': f'{s.tank_capacity_m3:g} m³ tank · {s.roof_m2:g} m² shared roof',
                          'drainage_upgrade': f'+{s.drainage_capacity_delta_m3_s:g} m³/s conveyance, not runoff reduction'}[kind]
                st.caption(('Requested' if included else 'Excluded by you') + f' · {s.unit_description}; {detail} · '
                           f'INR {s.capex_inr / 1e5:g} lakh / unit · D · Assumed')
        with st.expander('Equity safeguard'):
            floor = st.slider('Priority-zone benefit floor · normalised', 0.0, 1.0, 0.0, .05, key='input_floor')
            priority = max(eng.baseline.zones, key=lambda z: z.vulnerability_weight.value)
            st.caption(f'Share of weighted benefit that must reach the most vulnerable ward ({priority.name}, highest SC/ST share). '
                       '0 disables the floor. An unreachable floor returns "no feasible portfolio"; it is never relaxed.')
        clicked = st.button('Run optimisation', type='primary', width='stretch')
        st.caption('Runs PuLP/CBC on the current inputs, then re-checks every hard constraint independently.')
    request = None
    if total == 100 and budget is not None:
        request = RunRequest(baseline_version=eng.baseline.version, project_catalog_version=eng.catalog_version,
                             model_version=eng.settings.model_version, budget_inr=budget,
                             weights=dict(zip(KEYS, [v / 100 for v in raw])), equity_floor=floor,
                             allowed_interventions=tuple(types), mode=mode if raw == presets[mode] else 'Custom')
    if clicked:
        st.session_state.pop('preview_error', None)
        if budget is None:
            st.session_state['preview_error'] = 'Enter a valid capital budget before running the optimiser.'
        elif total != 100:
            st.session_state['preview_error'] = 'Objective weights must add up to 100%.'
        else:
            with result, st.spinner('Solving the portfolio with CBC and verifying constraints…'):
                try:
                    save_run(eng.run(request))
                except Exception as exc:  # surface engine failures honestly; previous runs stay available
                    st.session_state['preview_error'] = f'The engine failed: {exc}. Saved runs remain available in Decision Intelligence.'
    with result:
        st.header('Allocation ledger')
        if st.session_state.get('preview_error'):
            st.error(st.session_state['preview_error'])
        run = st.session_state.get('active_run')
        if not run:
            st.info('Choose the inputs above, then Run optimisation. The result will show the solver status, selected '
                    'projects, costs, modelled benefits by ward, binding constraints and evaluated alternatives.')
            return
        if request is None or request != run.request:
            st.warning('Inputs changed. Showing the last run below; use Run optimisation to apply current controls.')
        st.caption(f'{run.run_id} · {run.data_mode.value} · scenario {run.scenario.name} · solver {STATUS_TEXT[run.solver_status]} '
                   f'in {run.solver_runtime_s:.2f} s')
        if run.outcome is None:
            st.error(f'{STATUS_TEXT[run.solver_status]}: {run.solver_message}')
            if run.binding_constraints:
                ledger([{'Reason': r} for r in run.binding_constraints])
            st.write('Recovery: lower the equity floor, raise the budget, include more intervention types or remove '
                     'commitments. No constraint was relaxed and no portfolio is shown.')
            return
        o = run.outcome
        c1, c2, c3 = st.columns(3)
        c1.metric('Capital · INR crore', crore(o.capex_inr))
        c2.metric('Unallocated · INR crore', crore(run.unallocated_inr))
        c3.metric('Projects selected', sum(run.selected_candidate_counts.values()))
        if run.unallocated_inr > 0 and 'capital' not in run.binding_constraints:
            st.caption('Budget is not binding: every eligible requested unit with a positive score is already selected.')
        rows = []
        for cid, n in sorted(run.selected_candidate_counts.items()):
            c = next(c for c in eng.all_candidates if c.candidate_id == cid)
            rows.append({'Project': candidate_label(eng, cid), 'Units': n, 'Capital · INR': f'{c.capex_inr * n:,.0f}',
                         'Lifecycle · INR (10 yr)': f'{c.lcc_inr * n:,.0f}'})
        if rows:
            ledger(rows)
        else:
            st.info('The optimiser selected no projects: no requested unit improves the weighted score under these settings.')
        st.header('Modelled outcomes versus no investment')
        base = run.baseline_outcome
        ledger([{'Objective': METRIC_TITLES[m], 'No investment': num(base.metrics[m] if base else 0.0),
                 'Optimised plan': num(o.metrics[m]), 'Unit': METRIC_UNITS[m], 'Weight': f"{run.request.weights[m]:.0%}",
                 'Score contribution': f'{run.score_contributions.get(m, 0):+.4f}'} for m in METRICS]
               + [{'Objective': 'Equity · vulnerability-weighted benefit', 'No investment': '0.0', 'Optimised plan': f'{o.equity_gain:.3f}',
                   'Unit': 'normalised', 'Weight': f"{run.request.weights['Equity']:.0%}",
                   'Score contribution': f"{run.score_contributions.get('Equity', 0):+.4f}"},
                  {'Objective': 'Lifecycle cost (penalty)', 'No investment': '0', 'Optimised plan': f'{o.lcc_inr:,.0f}',
                   'Unit': 'INR, 10 yr, 5% real', 'Weight': f"{run.request.weights['LCC']:.0%}",
                   'Score contribution': f"{run.score_contributions.get('LCC', 0):+.4f}"}])
        st.caption('Modelled with observed ward data and assumed intervention coefficients (evidence grade D). Carbon counts '
                   'forest sequestration only; heat is a screening index, not °C.')
        st.header('Who receives investment and benefit?')
        names = zone_names(eng)
        ledger([{'Ward': f'{zid} — {names[zid]}', 'Residents': f"{int(z['population']):,}", 'Capital · INR': f"{z['capex_inr']:,.0f}",
                 'Runoff handled · % of design event': f"{(z['event_runoff_managed_share'] or 0):.1%}",
                 'Water · m³/yr per 1,000': f"{z['water_per_1000_residents_m3_yr']:,.1f}",
                 'Heat reduction per 1,000': f"{z['heat_reduction_per_1000_residents']:.3f}"} for zid, z in run.outcomes_by_zone.items()])
        with st.expander('Constraint review and verification'):
            slack_rows = []
            for name, s in run.constraint_slack.items():
                unit = 'INR' if name == 'capital' else 'm²' if name.startswith(('roof', 'land')) else ''
                slack_rows.append({'Constraint': name, 'Slack': f'{s:,.0f} {unit}'.strip(),
                                   'Binding': 'Yes' if name in run.binding_constraints else 'No'})
            ledger(slack_rows)
            ledger([{'Independent check': k.replace('_', ' '), 'Result': 'Pass' if v else 'FAIL'} for k, v in run.verification.items()])
            st.caption(f'Surrogate (MILP) score {run.surrogate_score:.4f}; independently evaluated score {run.evaluated_score:.4f}. '
                       'Optimality is among the declared candidate units and assumptions only.')
        with st.expander('Why other projects were not selected'):
            ledger([{'Project': candidate_label(eng, k), 'Reason': v} for k, v in run.rejected.items()])
        st.header('Compare evaluated alternatives')
        alt_rows = [{'Plan': 'Selected plan', 'Method': 'MILP optimum', 'Capital · INR': f'{o.capex_inr:,.0f}',
                     'Score': f'{o.score:.4f}', **{SHORT_UNITS[m]: num(o.metrics[m]) for m in METRICS}, 'Feasible': 'Yes'}]
        for a in run.alternatives:
            ao = a.outcome
            alt_rows.append({'Plan': a.label, 'Method': a.method.replace('_', ' '), 'Capital · INR': f'{ao.capex_inr:,.0f}',
                             'Score': f'{ao.score:.4f}', **{SHORT_UNITS[m]: num(ao.metrics[m]) for m in METRICS},
                             'Feasible': 'Yes' if a.feasible else 'No'})
        ledger(alt_rows)
        st.caption('All plans are scored with the same weights, normalisation, budget and evaluator. "Best" means best among '
                   'these evaluated feasible plans, not a full Pareto frontier.')


def shock_lab():
    eng = engine()
    if eng is None:
        return engine_unavailable()
    st.title('Will the plan hold under pressure?')
    st.write('Keep the original selection fixed, change one stress condition and compare it with a fresh re-optimisation.')
    run = st.session_state.get('active_run')
    if not run or run.outcome is None:
        preflight('First, give the lab a plan to test', 'The comparison needs a feasible optimised plan so the original selection cannot quietly change during a stress test.', [
            'Extreme rainfall: re-evaluate runoff handling under a stronger design storm.',
            'Drought: re-run the daily tank balance with less rain and weaker tree cooling.',
            'Budget cut: check whether the plan still fits the revised envelope, keeping commitments.'])
        st.button('Create an investment plan', type='primary', on_click=navigate, args=('Investment Optimiser',))
        st.caption('No scenario has run. These are user-defined stress conditions, not forecasts.')
        return
    names = zone_names(eng)
    st.caption(f'Original plan {run.run_id} · {run.request.mode} · INR {crore(run.request.budget_inr)} crore · selection frozen')
    c1, c2 = st.container(), st.container()
    with c1:
        shock = st.selectbox('Disruption', list(SHOCKS), key='shock_kind')
        preset = eng.scenarios[SHOCKS[shock]]
        if shock == 'Extreme rainfall':
            factors = {'design_intensity_multiplier': st.slider('Storm intensity multiplier', 1.0, 2.5, preset.design_intensity_multiplier, .05, key='shock_rain')}
        elif shock == 'Drought':
            factors = {'rainfall_availability_factor': st.slider('Rainfall availability factor', 0.0, 1.0, preset.rainfall_availability_factor, .05, key='shock_avail'),
                       'tree_cooling_factor': st.slider('Tree cooling retention factor', 0.0, 1.0, preset.tree_cooling_factor, .05, key='shock_cool')}
        elif shock == 'Sudden budget cut':
            factors = {'budget_factor': st.slider('Retained budget · fraction', 0.0, 1.0, preset.budget_factor, .05, key='shock_budget')}
        else:
            factors = {}
        commitments = st.multiselect('Committed projects', sorted(run.selected_candidate_counts), key='shock_commit',
                                     format_func=lambda k: candidate_label(eng, k))
        st.caption('Committed projects keep their capital and must stay in the re-optimised plan.')
        st.caption('User-defined stress assumptions applied to the historical baseline, not forecasts.')
        if st.button('Run shock comparison', type='primary'):
            with st.spinner('Evaluating the frozen plan and re-optimising under the shock…'):
                try:
                    comp = eng.shock(run, SHOCKS[shock], factors, {k: run.selected_candidate_counts[k] for k in commitments})
                    save_comparison(comp)
                    st.session_state['shock_inputs'] = (run.run_id, shock, factors, commitments)
                    st.session_state.pop('shock_error', None)
                except Exception as exc:
                    st.session_state['shock_error'] = f'Shock evaluation failed: {exc}'
    with c2:
        if st.session_state.get('shock_error'):
            st.error(st.session_state['shock_error'])
        cid = st.session_state.get('active_shock')
        comp = st.session_state.get('shock_results', {}).get(cid)
        if not comp or comp.original_run_id != run.run_id:
            st.caption('Submit to compare (A) the plan under normal conditions, (B) the same plan under the shock and '
                       '(C) a new plan optimised for the shock.')
            return
        if st.session_state.get('shock_inputs') != (run.run_id, shock, factors, commitments):
            st.warning('Stress controls changed. The table shows the last submitted comparison.')
        st.header(comp.scenario.name + ' · comparison')
        a, bo, c = comp.a_original_normal, comp.b_original_under_shock, comp.c_reoptimised
        co = c.outcome
        rows = [{'Measure': 'Capital envelope · INR', 'A · original, normal': f'{run.budget_available_inr:,.0f}',
                 'B · original under shock': f'{c.budget_available_inr:,.0f}', 'C · re-optimised': f'{c.budget_available_inr:,.0f}'},
                {'Measure': 'Plan capital · INR', 'A · original, normal': f'{a.capex_inr:,.0f}', 'B · original under shock': f'{bo.capex_inr:,.0f}',
                 'C · re-optimised': f'{co.capex_inr:,.0f}' if co else '—'},
                {'Measure': 'Feasible?', 'A · original, normal': 'Yes', 'B · original under shock': 'Yes' if comp.b_feasible else 'No',
                 'C · re-optimised': STATUS_TEXT[c.solver_status]}]
        for m in METRICS:
            d = comp.deltas[m]
            rows.append({'Measure': f'{METRIC_TITLES[m]} · {SHORT_UNITS[m]}', 'A · original, normal': num(d['A']),
                         'B · original under shock': num(d['B']), 'C · re-optimised': num(d['C'])})
        res = comp.deltas.get('residual_runoff_m3')
        if res:
            rows.append({'Measure': 'Design-event runoff left unmanaged · m³ / event (residual risk)', 'A · original, normal': num(res['A'], 0),
                         'B · original under shock': num(res['B'], 0), 'C · re-optimised': num(res['C'], 0)})
        rows.append({'Measure': 'Weighted score (same scales)', 'A · original, normal': f"{comp.deltas['score']['A']:.4f}",
                     'B · original under shock': f"{comp.deltas['score']['B']:.4f}",
                     'C · re-optimised': f"{comp.deltas['score']['C']:.4f}" if comp.deltas['score']['C'] is not None else '—'})
        ledger(rows)
        for note in comp.b_notes:
            st.error(note)
        if co is None:
            st.error(f'Re-optimisation: {c.solver_message}')
        else:
            change = []
            for k, n in comp.additions.items():
                change.append({'Change': 'Added', 'Project': candidate_label(eng, k), 'Units': n})
            for k, n in comp.removals.items():
                change.append({'Change': 'Removed', 'Project': candidate_label(eng, k), 'Units': n})
            st.subheader('How the re-optimised plan differs')
            if change:
                ledger(change)
            else:
                st.caption('The re-optimised plan keeps the original selection.')
        fig = go.Figure()
        labels = ['A · normal', 'B · shock, same plan', 'C · re-optimised']
        for m, color in zip(('F', 'W', 'H'), (palette()['accent'], palette()['link'], palette()['warning'])):
            vals = [comp.deltas[m]['A'], comp.deltas[m]['B'], comp.deltas[m]['C']]
            norm = [None if v is None else v / eng.scales.tau[m] for v in vals]
            fig.add_trace(go.Bar(name=METRIC_TITLES[m].split(' ·')[0], x=labels, y=norm, marker_color=color))
        fig.update_layout(barmode='group', yaxis_title='normalised benefit (share of reference)', height=300)
        st.plotly_chart(chart_style(fig), width='stretch', key='shock_chart')
        st.caption('Bars use the same fixed normalisation scales for A, B and C, so they are directly comparable. Benefits can '
                   'rise under a stronger storm (tanks fill faster) while residual unmanaged runoff rises more — read both rows.')
        with st.expander('Sensitivity of the comparison'):
            s = comp.sensitivity
            ledger([{'Plan': k, 'Min score': f"{v['min']:.4f}", 'Mean': f"{v['mean']:.4f}", 'Max': f"{v['max']:.4f}", 'Cases': v['cases']}
                    for k, v in s.items() if 'cases' in v])
            if 'max_regret_of_original' in s:
                st.caption(f"Largest score loss from keeping the original plan instead of re-optimising: "
                           f"{s['max_regret_of_original']['value']:.4f} across the perturbations (sensitivity range, not a confidence interval).")
        st.download_button('Export scenario comparison · JSON', comp.model_dump_json(indent=1), f'{comp.comparison_id}.json', 'application/json')


def decisions():
    eng = engine()
    if eng is None:
        return engine_unavailable()
    st.title('What supports this decision?')
    st.write('Follow the selection, its distribution and its evidence before exporting a review brief.')
    history = st.session_state.get('history', {})
    if not history:
        preflight('A decision trail starts with a selection', 'Run the optimiser to inspect the reasons, assumptions and distribution in one place.', [
            'Selection: which projects were chosen, and which constraints decided it?',
            'Distribution: how much investment and benefit reaches each ward?',
            'Evidence: what is observed, what is assumed and what must be validated?'])
        st.button('Build the first decision', type='primary', on_click=navigate, args=('Investment Optimiser',))
        with st.expander('What will the exported brief contain?'):
            st.write('The run ID, input hash, budget, selected projects, weights, solver status, modelled outcomes, data and '
                     'model versions, sources and explicit limitations.')
        return
    keys = list(history)
    active = st.session_state.get('active_run')
    default = keys.index(active.run_id) if active and active.run_id in keys else 0
    selected = st.selectbox('Saved run', keys, index=default, format_func=lambda k: (
        f'{keys.index(k) + 1}. {history[k].request.mode} · {history[k].scenario.name} · INR {history[k].request.budget_inr / 1e7:g} crore · {k}'))
    run = history[selected]
    names = zone_names(eng)
    exp = explanation_for(eng, run)
    st.caption(f'{run.data_mode.value} · solver {STATUS_TEXT[run.solver_status]} · baseline {run.baseline_version} · '
               f'model {run.model_version} · input {run.input_hash[:12]}')
    c1, c2 = st.container(), st.container()
    with c1:
        st.header('What this selection means')
        st.write(exp.narrative)
        st.caption('Narrative source: ' + ('Amazon Bedrock, numbers validated against the run' if exp.explanation_source == 'bedrock'
                                           else 'deterministic explainer') + f' · {exp.bedrock_status}')
        if exp.why_selected:
            with st.expander('Why this portfolio', expanded=True):
                for line in exp.why_selected:
                    st.write('• ' + line)
        project = st.selectbox('Inspect selected or excluded project', [c.candidate_id for c in eng.all_candidates],
                               format_func=lambda k: candidate_label(eng, k))
        if project in run.selected_candidate_counts:
            c = next(c for c in eng.all_candidates if c.candidate_id == project)
            st.info(f'Selected ({run.selected_candidate_counts[project]} unit). Capital INR {c.capex_inr:,.0f}; '
                    f'10-year lifecycle cost INR {c.lcc_inr:,.0f}. It was part of the highest-scoring feasible combination.')
        else:
            st.info(run.rejected.get(project, 'Not selected by the optimiser.'))
        st.header('Whose neighbourhood receives investment?')
        if exp.beneficiaries:
            ledger([{'Ward': f"{b['zone_id']} — {b['zone']}", 'Residents': f"{int(b['population']):,}", 'Capital · INR': f"{b['capex_inr']:,.0f}",
                     'INR / resident': f"{b['inr_per_resident']:,.1f}", 'Flood · m³ per 1,000': b['flood_m3_per_1000'],
                     'Water · m³/yr per 1,000': b['water_m3_yr_per_1000'], 'Heat reduction per 1,000': b['heat_reduction_per_1000']}
                    for b in exp.beneficiaries])
        for line in exp.underserved:
            st.warning(line)
        if exp.binding_constraints:
            st.subheader('Constraints that decided the result')
            for line in exp.binding_constraints:
                st.write('• ' + line)
        st.header('Declared priorities')
        st.caption('Saved priority mode: ' + run.request.mode)
        ledger([{label: f'{run.request.weights[key]:.0%}' for key, label in zip(KEYS, WEIGHT_LABELS)}])
        st.caption('Preferences used by the optimiser for this run. Changing them can change the selected mix.')
    with c2:
        st.header('Trade-offs, uncertainty & consequences')
        if exp.improved or exp.worsened:
            with st.expander('What improved and what became worse', expanded=True):
                for line in exp.improved:
                    st.write('▲ ' + line)
                for line in exp.worsened:
                    st.write('▼ ' + line)
        if exp.shock_findings:
            with st.expander('Under climate shocks', expanded=True):
                for line in exp.shock_findings:
                    st.write('• ' + line)
        else:
            st.caption('No stress test has been run for this plan yet. Use the Climate Shock Lab to add one.')
        with st.expander('Uncertainty'):
            for line in exp.uncertainties:
                st.write('• ' + line)
        with st.expander('Possible unintended consequences'):
            for line in exp.unintended_consequences:
                st.write('• ' + line)
        if exp.alternatives_compared:
            with st.expander('Why alternatives were not chosen'):
                ledger([{'Alternative': a['alternative'], 'Capital · INR': f"{a['capex_inr']:,.0f}", 'Score': a['score'],
                         'Gap to selected': a['score_gap_vs_selected'], 'Reason': a['why_not_chosen']} for a in exp.alternatives_compared])
        with st.expander('Sources & assumptions'):
            prov = eng.baseline.provenance
            ledger(prov[prov['source_id'].isin(run.source_ids)][['source_id', 'dataset_name', 'observation_period', 'evidence_class', 'licence']]
                   .rename(columns={'source_id': 'Source', 'dataset_name': 'Dataset', 'observation_period': 'Period',
                                    'evidence_class': 'Class', 'licence': 'Licence / caveat'}).to_dict('records'))
            st.caption('Declared assumptions used by this run:')
            for line in run.assumptions:
                st.write('• ' + line)
    with st.expander('Compare saved runs'):
        others = st.multiselect('Saved runs to compare', keys, default=[selected])
        ref = (run.baseline_version, run.catalog_version, run.model_version)
        compatible = [k for k in others if (history[k].baseline_version, history[k].catalog_version, history[k].model_version) == ref]
        if len(compatible) != len(others):
            st.warning('Incompatible baseline, catalogue or model versions excluded from comparison.')
        ledger([{'Run': k, 'Mode': history[k].request.mode, 'Scenario': history[k].scenario.name,
                 'Budget · INR': f'{history[k].budget_available_inr:,.0f}', 'Capital · INR': f'{history[k].allocated_inr:,.0f}',
                 'Solver': history[k].solver_status, 'Score': f'{history[k].evaluated_score:.4f}' if history[k].evaluated_score is not None else '—',
                 **{SHORT_UNITS[m]: num(history[k].outcome.metrics[m]) if history[k].outcome else '—' for m in METRICS}} for k in compatible])
    st.header('Decision summary')
    sel = ', '.join(f'{candidate_label(eng, k)} x{n}' for k, n in sorted(run.selected_candidate_counts.items())) or 'None'
    metrics = '\n'.join(f'- {METRIC_TITLES[m]}: {num(run.outcome.metrics[m])} {METRIC_UNITS[m]}' for m in METRICS) if run.outcome else '- Not available (no feasible portfolio)'
    brief = f'''# C1V1C — decision brief

{run.data_mode.value.upper()} — real Bengaluru ward data with declared intervention assumptions. Modelled screening estimates, not forecasts.
Run: {run.run_id} (input hash {run.input_hash[:16]})
Created (UTC): {run.created_at_utc}
Scenario: {run.scenario.name}; budget available INR {run.budget_available_inr:,.0f}
Solver: {run.solver_status} — {run.solver_message}
Selected: {sel}
Capital allocated: INR {run.allocated_inr:,.0f}; unallocated INR {run.unallocated_inr:,.0f}
Weights: {json.dumps(run.request.weights)}
Outcomes:
{metrics}

Narrative ({exp.explanation_source}): {exp.narrative}

Baseline: {run.baseline_version} (sha256 {run.baseline_sha256[:16]}); catalogue {run.catalog_version}; model {run.model_version}.
Sources: {', '.join(run.source_ids)}
Limitations:
''' + '\n'.join('- ' + g for g in run.gaps)
    a, b = st.columns(2)
    a.download_button('Export decision brief · Markdown', brief, f'{selected}.md', 'text/markdown', width='stretch')
    b.download_button('Export run record · JSON', run.model_dump_json(indent=1), f'{selected}.json', 'application/json', width='stretch')
