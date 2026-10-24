"""Data-engine tests: parsing, coordinate/duplicate validation, date reconstruction and real-baseline integrity."""
import hashlib
import json

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point, box

from c1v1c import pipeline
from c1v1c.baseline import BaselineUnavailable, load_baseline
from c1v1c.evidence import Evidence
from conftest import REAL_BASELINE, requires_raw, requires_real


def test_swat_grid_dates_come_from_the_file_header(tmp_path):
    p = tmp_path / "X775Y130.txt"
    p.write_text("19710101\n0.0\n1.5\n-99.0\n", encoding="utf-8")
    d = pipeline.read_swat_grid(p, ("precipitation_mm",))
    assert d["date"].dt.strftime("%Y-%m-%d").tolist() == ["1971-01-01", "1971-01-02", "1971-01-03"]
    assert d["precipitation_mm"].tolist()[:2] == [0.0, 1.5]


def test_swat_day_count_spans_1971_to_2005(tmp_path):
    p = tmp_path / "X775Y130.txt"
    p.write_text("19710101\n" + "0.0\n" * 12784, encoding="utf-8")
    d = pipeline.read_swat_grid(p, ("precipitation_mm",))
    assert d["date"].iloc[-1].strftime("%Y-%m-%d") == "2005-12-31"
    assert d["date"].is_monotonic_increasing and d["date"].diff().dropna().dt.days.eq(1).all()


def _wards():
    return gpd.GeoDataFrame({"ward_key": ["GBA-C9-W001"], "ward_name": ["Test ward"], "zone_name": ["Test"]},
                            geometry=[box(77.55, 12.95, 77.65, 13.05)], crs="EPSG:4326")


def test_flood_points_invalid_and_duplicate_coordinates(tmp_path):
    folder = tmp_path / pipeline.FLOOD_DIR
    folder.mkdir(parents=True)
    pts = gpd.GeoDataFrame({"Name": ["a", "b", "c", "d", "e"], "OBJECTID": [1, 2, 3, 4, 5]},
                           geometry=[Point(77.60, 13.00), Point(77.60, 13.00), Point(0.0, 0.0), Point(77.61, 13.01),
                                     Point(77.80, 13.20)], crs="EPSG:4326")
    pts.to_file(folder / "lowlying.kml", driver="KML", layer="lowlying_locations")
    report = pipeline.Report()
    out = pipeline.load_flood_points(tmp_path, _wards(), report)
    assert len(out) == 4                                    # (0,0) excluded
    assert out["duplicate_of"].notna().sum() == 1           # second copy flagged, not deleted
    assert out["usable_for_counts"].sum() == 2              # duplicate and out-of-ward point not counted
    assert out.loc[out.duplicate_of.notna(), "status"].eq("hazard_marker_not_construction_site").all()
    statuses = {c["check"]: c["status"] for c in report.checks}
    assert statuses["coordinate_validity"] == "corrected" and statuses["duplicate_coordinates"] == "corrected"


def test_quantity_serialisation_never_turns_missing_into_zero():
    from c1v1c.evidence import Quantity
    q = Quantity(**json.loads(pipeline.q(float("nan"), "m", Evidence.DERIVED)))
    assert q.value is None and q.evidence is Evidence.MISSING


def test_missing_or_tampered_baseline_is_refused(tmp_path, synthetic_dir):
    from c1v1c.baseline import _load
    _load.cache_clear()
    with pytest.raises(BaselineUnavailable):
        load_baseline(tmp_path / "does-not-exist")
    zones = synthetic_dir / "zones_model_inputs.csv"
    zones.write_text(zones.read_text(encoding="utf-8").replace("6500", "9999"), encoding="utf-8")
    _load.cache_clear()
    with pytest.raises(BaselineUnavailable, match="checksum"):
        load_baseline(synthetic_dir)


@requires_real
def test_real_baseline_integrity_and_labels():
    from c1v1c.baseline import _load
    _load.cache_clear()
    b = load_baseline(REAL_BASELINE)
    assert b.data_mode.value == "mixed-evidence pilot" and len(b.zones) == 3
    manifest = json.loads((REAL_BASELINE / "baseline_manifest.json").read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((REAL_BASELINE / name).read_bytes()).hexdigest() == digest
    for z in b.zones:
        assert z.gba_zone_name == "Yelahanka" and z.ward_keys[0].startswith("GBA-C")
        assert z.population.evidence is Evidence.OBSERVED and z.population.value > 0
        assert z.eligible_roof_m2.evidence is Evidence.ASSUMED  # footprints are not proof of eligibility
        for f in ("area_ha", "population", "runoff_coefficient", "design_p24_mm", "summer_tmax_c", "heat_index"):
            q = getattr(z, f)
            assert q.source_ids and q.unit and q.evidence is not Evidence.SYNTHETIC
        assert 0 < z.runoff_coefficient.value < 1 and 0 <= z.heat_index.value <= 1
    zones = pd.read_csv(REAL_BASELINE / "zones.csv")
    assert zones["ward_key"].is_unique and (zones["population_persons"] > 0).all()


@requires_real
def test_real_rainfall_dates_are_reconstructed_not_invented():
    rain = pd.read_csv(REAL_BASELINE / "rainfall_daily.csv", parse_dates=["date"])
    for _, g in rain.groupby("grid_id"):
        assert g["date"].min().strftime("%Y-%m-%d") == "1971-01-01" and g["date"].max().strftime("%Y-%m-%d") == "2005-12-31"
        assert g["date"].nunique() == len(g) == 12784
    assert (rain["precipitation_mm"] >= 0).all() and rain["unit"].eq("mm/day").all()
    report = json.loads((REAL_BASELINE / "data_quality_report.json").read_text(encoding="utf-8"))
    checks = {(c["dataset"], c["check"]): c for c in report["checks"]}
    bug = checks[("rainfall", "curated_file_date_bug")]
    assert bug["status"] == "corrected" and all(c["values_identical_in_order"] for c in bug["cells"])
    assert any(q["file"] == "curated/rainfall.csv" for q in report["quarantined"])


@requires_real
def test_real_quality_checks_cover_known_defects():
    report = json.loads((REAL_BASELINE / "data_quality_report.json").read_text(encoding="utf-8"))
    checks = {(c["dataset"], c["check"]): c for c in report["checks"]}
    assert checks[("flood_points", "coordinate_validity")]["excluded"] == [{"site_id": "low_lying-83", "lon": 0.0, "lat": 0.0}]
    assert len(checks[("flood_points", "duplicate_coordinates")]["groups"]) == 6
    assert checks[("wards", "population_total_vs_sex_sum")]["status"] == "warn"
    assert checks[("wards", "composite_key_unique")]["status"] == "pass"
    assert checks[("urban_heat", "coverage")]["status"] == "fail"           # non-Bengaluru rows rejected
    assert checks[("drainage", "merged_layer")]["status"] == "corrected"     # no double counting
    assert checks[("collection", "netcdf_2015_2025")]["status"] == "fail"    # absence reported, not assumed
    assert checks[("flood_points", "legacy_identifiers")]
    sites = pd.read_csv(REAL_BASELINE / "sites.csv")
    assert sites["status"].eq("hazard_marker_not_construction_site").all()
    assert not ((sites["lon"] == 0) & (sites["lat"] == 0)).any()


@requires_raw
def test_pipeline_is_reproducible(tmp_path):
    from c1v1c.config import Settings
    s = Settings.load()
    m = pipeline.build(s.raw_dir, tmp_path / "rebuild", "bengaluru_pilot_v1")
    if (REAL_BASELINE / "baseline_manifest.json").exists():
        ref = json.loads((REAL_BASELINE / "baseline_manifest.json").read_text(encoding="utf-8"))["files"]
        for name in ("zones_model_inputs.csv", "zones.csv", "rainfall_daily.csv", "sites.csv", "zones.geojson"):
            assert m["files"][name] == ref[name], name
