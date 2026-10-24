"""Builds a SYNTHETIC curated baseline for engine tests (never Bengaluru data).

Zone values come from data/synthetic_test/zone_fixture.csv (master plan fixtures); rainfall is a
seeded, clearly synthetic monsoon-shaped series. Every quantity is labelled Evidence.SYNTHETIC.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from c1v1c.evidence import DataMode, Evidence, Quantity

ROOT = Path(__file__).resolve().parents[1]
FILES = ["zones_model_inputs.csv", "zones.csv", "rainfall_daily.csv", "sites.csv", "wards_summary.csv", "provenance.csv",
         "climate_summary.csv", "interventions.csv", "scenarios.csv", "zones.geojson", "data_quality_report.json"]


def _q(value, unit) -> str:
    return Quantity(value=value, unit=unit, evidence=Evidence.SYNTHETIC, source_ids=("SYNTHETIC_FIXTURE",),
                    note="synthetic test fixture").model_dump_json()


def build(out: Path, *, roof_m2: float | None = None, sc_st: tuple[float, float, float] = (0.10, 0.20, 0.05),
          years: int = 6) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    with (ROOT / "data/synthetic_test/zone_fixture.csv").open(encoding="utf-8") as fh:
        fixture = list(csv.DictReader(fh))
    rows, feats = [], []
    for i, z in enumerate(fixture):
        zid = "Z" + z["zone_id"]
        lat, lon = 13.10 - 0.01 * i, 77.59 + 0.01 * i
        area_ha = float(z["area_ha"])
        c = float(z["runoff_coefficient"])
        p24 = 70.0
        p_event = p24 * (1 / 24) ** (1 / 3)
        roof = float(z["suitable_roof_m2"]) if roof_m2 is None else roof_m2
        rows.append({
            "zone_id": zid, "zone_name": f"Synthetic zone {z['zone_id']} ({z['label']})", "ward_keys": f"SYN-{z['zone_id']}",
            "gba_corporation": "SYNTHETIC", "gba_zone_name": "SYNTHETIC", "centroid_lat": lat, "centroid_lon": lon,
            "rainfall_cell": "SYN_CELL", "selection_reason": "synthetic fixture",
            "area_ha": _q(area_ha, "ha"), "population": _q(float(z["population"]), "persons"), "sc_st_share": _q(sc_st[i], "fraction"),
            "built_fraction": _q(0.4, "fraction"), "impervious_fraction": _q(0.55, "fraction"), "vegetation_fraction": _q(0.45, "fraction"),
            "runoff_coefficient": _q(c, "-"), "eligible_roof_m2": _q(roof, "m2"), "plantable_land_m2": _q(float(z["plantable_land_m2"]), "m2"),
            "design_p24_mm": _q(p24, "mm/day"), "design_event_mm": _q(p_event, "mm in 1 h"),
            "design_event_runoff_m3": _q(c * p_event / 1000 * area_ha * 1e4, "m3 per design event"),
            "summer_tmax_c": _q(34.0, "degC"), "heat_index": _q(float(z["heat_index"]), "0-1 index"),
            "vulnerability_weight": _q(sc_st[i] / (sum(sc_st) / 3), "-"), "flood_points": _q(1.0, "count"),
            "drain_length_m": _q(1000.0, "m"), "waterbody_features": _q(0.0, "count"),
        })
        d = 0.003
        feats.append({"type": "Feature", "properties": {"zone_id": zid},
                      "geometry": {"type": "Polygon", "coordinates": [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d],
                                                                       [lon - d, lat + d], [lon - d, lat - d]]]}})
    pd.DataFrame(rows).to_csv(out / "zones_model_inputs.csv", index=False)
    pd.DataFrame([{"zone_id": r["zone_id"], "zone_name": r["zone_name"]} for r in rows]).to_csv(out / "zones.csv", index=False)
    rng = np.random.default_rng(42)
    dates = pd.date_range("2000-01-01", periods=365 * years, freq="D")
    season = np.clip(np.sin((dates.dayofyear.to_numpy() - 120) / 365 * 2 * np.pi), 0, None)
    rain = np.where(rng.random(len(dates)) < 0.15 + 0.4 * season, rng.gamma(1.2, 8 + 12 * season), 0.0)
    pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "grid_id": "SYN_CELL", "lon": 77.6, "lat": 13.1, "precipitation_mm": rain.round(1),
                  "unit": "mm/day", "evidence": Evidence.SYNTHETIC.value, "source_id": "SYNTHETIC_FIXTURE"}).to_csv(out / "rainfall_daily.csv", index=False)
    pd.DataFrame(columns=["site_id", "point_class", "name", "lon", "lat", "usable_for_counts", "pilot_zone_id"]).to_csv(out / "sites.csv", index=False)
    pd.DataFrame(columns=["ward_key"]).to_csv(out / "wards_summary.csv", index=False)
    pd.DataFrame([{"source_id": "SYNTHETIC_FIXTURE", "dataset_name": "Synthetic test fixture", "observation_period": "none",
                   "spatial_resolution": "-", "evidence_class": "synthetic", "licence": "-"}]).to_csv(out / "provenance.csv", index=False)
    pd.DataFrame([{"zone_id": "ALL", "rainfall_cell": "SYN_CELL"}]).to_csv(out / "climate_summary.csv", index=False)
    (out / "interventions.csv").write_text((ROOT / "config/intervention_assumptions.csv").read_text(encoding="utf-8"), encoding="utf-8")
    (out / "scenarios.csv").write_text((ROOT / "config/scenarios.csv").read_text(encoding="utf-8"), encoding="utf-8")
    (out / "zones.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    (out / "data_quality_report.json").write_text(json.dumps({"checks": [], "quarantined": [], "gaps": ["synthetic fixture"]}), encoding="utf-8")
    manifest = {"baseline_version": "synthetic_test_v1", "data_mode": DataMode.SYNTHETIC.value, "known_gaps": ["synthetic fixture only"],
                "files": {f: hashlib.sha256((out / f).read_bytes()).hexdigest() for f in FILES}}
    (out / "baseline_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return out
