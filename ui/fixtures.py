"""Temporary, isolated display fixtures. Delete/replace adapter after approval.

Only inventory sums and UI validation are calculated. No benefits are inferred.
"""
import csv
import hashlib
import json
from pathlib import Path
from .contracts import PreviewSnapshot, ScenarioRequest

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'green_roof': 'Green roofs', 'urban_forest': 'Urban forests',
          'rainwater_harvesting': 'Rainwater harvesting', 'drainage_upgrade': 'Drainage improvements'}
COSTS = {'green_roof': 3_000_000, 'urban_forest': 2_000_000,
         'rainwater_harvesting': 1_200_000, 'drainage_upgrade': 5_000_000}
WEIGHTS = {'Balanced': [25,20,20,10,15,10], 'Flood-first': [55,10,10,5,10,10],
           'Water-first': [10,55,10,5,10,10], 'Heat-first': [10,10,55,5,10,10],
           'Equity-first': [15,15,10,5,45,10]}
KEYS = ['F','W','H','G','Equity','LCC']
PORTFOLIOS = {
    'Mixed investment': ('A-drainage_upgrade','B-urban_forest','C-rainwater_harvesting','A-green_roof'),
    'Water emphasis': ('A-rainwater_harvesting','B-rainwater_harvesting','C-rainwater_harvesting','B-urban_forest'),
    'Heat emphasis': ('A-urban_forest','B-urban_forest','C-urban_forest','B-green_roof'),
    'Equal-spend example': ('A-rainwater_harvesting','B-rainwater_harvesting','C-rainwater_harvesting'),
    'No investment': (),
}
# Drawn solely to review comparison layouts, not outputs of any model.
DISPLAY_OUTCOMES = {
    'Mixed investment': [0.12, 90, 140], 'Water emphasis': [0.0, 270, 65],
    'Heat emphasis': [0.0, 0, 220], 'Equal-spend example': [0,270,0], 'No investment': [0,0,0],
}

def zones():
    with (ROOT/'data/synthetic_test/zone_fixture.csv').open() as f:
        return list(csv.DictReader(f))

def catalogue():
    return [{'ID':f'{z}-{t}', 'Zone':z, 'Intervention':label, 'type':t,
             'Capital · INR':COSTS[t], 'Roof · m²':250 if t=='green_roof' else 200 if t=='rainwater_harvesting' else 0,
             'Land · m²':300 if t=='urban_forest' else 0, 'Evidence':'D · synthetic; eligibility unverified'}
            for z in ['A','B','C'] for t,label in LABELS.items()]

def preview(request: ScenarioRequest, fixture_name: str) -> PreviewSnapshot:
    ids = tuple(i for i in PORTFOLIOS[fixture_name] if i.split('-',1)[1] in request.allowed_interventions)
    cost = sum(COSTS[i.split('-',1)[1]] for i in ids)
    if cost > request.budget_inr:
        raise ValueError(f'This display portfolio costs INR {cost:,.0f}, above the entered budget. Choose another fixture or raise the budget; no solver has run.')
    payload = json.dumps({'request':request.model_dump(), 'ids':ids, 'fixture':fixture_name}, sort_keys=True)
    return PreviewSnapshot(preview_id='preview-'+hashlib.sha256(payload.encode()).hexdigest()[:12],
                           request=request, selected_ids=ids, cost_inr=cost, fixture_name=fixture_name)
