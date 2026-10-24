"""Reproducible Bengaluru data pipeline: raw Drive collection -> validated curated baseline.

Run:  python -m c1v1c.pipeline [--raw DIR] [--out DIR]

Every output row carries units, a stable identifier and a source_id that resolves in
provenance.csv. Values are classed observed / derived / estimated / assumed / missing and
never silently substituted. Known source defects are corrected only where the source itself
supports the correction, otherwise quarantined (see data_quality_report.json).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import warnings
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
from shapely.geometry import Point

from c1v1c.catalogue import load_parameters
from c1v1c.config import Settings
from c1v1c.evidence import DataMode, Evidence, Quantity
from c1v1c.models import equity, heat, hydrology

warnings.filterwarnings("ignore", message=".*KML.*")
UTM = "EPSG:32643"  # WGS84 / UTM zone 43N, metres, covers Bengaluru
WGS = "EPSG:4326"
BLR_BBOX = (77.2, 12.7, 77.9, 13.3)  # lon_min, lat_min, lon_max, lat_max (generous city window)
PILOT_GBA_ZONE = "Yelahanka"

WARDS = "raw/boundaries/gba-369-wards-december-2025.kml"
FLOOD_DIR = "raw/references/flood_locations"
FOOTPRINTS = "raw/references/building_footprints/building_footprints_bengaluru.geojsonl"
DRAIN_DIR = "raw/references/stormwater_drainage/maps"
GROUNDWATER = "raw/references/groundwater_potential/1dda919d-ff28-4aa9-90ce-bd18e708927b.kml"
WATERBODIES = "raw/waterbodies"
IMD05 = "raw/rainfall/IMD_GRIDED_WEATHER/IMD_gridded_PCP_0.5deg"
IMD1T = "raw/rainfall/IMD_GRIDED_WEATHER/IMD_1deg_temperature"
IMD1P = "raw/rainfall/IMD_GRIDED_WEATHER/IMD_1deg_rainfall"
DAILY_CSV = "raw/rainfall/DOC-20261023-WA0007.csv"
HEAT_CSV = "raw/references/urban_heat/extracted/urban_heat_island_spatiotemporal_dataset.csv"
CURATED_RAIN = "curated/rainfall.csv"
OLD_SITES = "curated/sites.csv"

SOURCES = {
    "GBA_WARDS_2025": ("Greater Bengaluru Authority 369-ward boundaries (Dec 2025) with delimitation population attributes", WARDS,
                       "2025-12", "ward polygons", "observed", "Licence not stated in file; government open-data release - verify before redistribution"),
    "MS_FOOTPRINTS": ("Microsoft Global ML Building Footprints, India quadkey 123303312 (index 2026-08-13)", FOOTPRINTS,
                      "imagery vintage varies", "building polygons", "observed", "CDLA Permissive 2.0"),
    "BLR_FLOOD_POINTS": ("Bengaluru flood-prone, flood-vulnerable and low-lying location KMLs", FLOOD_DIR,
                         "not stated", "points", "observed", "Licence not stated; hazard markers, not construction sites"),
    "BLR_SWD": ("Bengaluru storm-water drain network (primary + secondary) KMLs", DRAIN_DIR,
                "not stated", "polylines", "observed", "Licence not stated; geometry only, no capacity/condition"),
    "BLR_WATERBODIES": ("Bengaluru tanks (blr_tanks) and ponds (blr_ponds) polygon KMLs", WATERBODIES,
                        "not stated", "polygons", "observed", "Licence not stated; current water-spread not verified"),
    "BLR_GW_POTENTIAL": ("Bengaluru groundwater potential polygons (GW_PROS classes)", GROUNDWATER,
                         "not stated", "polygons", "observed", "Licence not stated; qualitative potential classes"),
    "IMD_RF_0P5": ("IMD gridded daily rainfall 0.5 deg (SWAT text grids, header = start date)", IMD05,
                   "1971-01-01..2005-12-31", "0.5 deg grid", "observed", "IMD data policy; redistribution of raw grids not assumed"),
    "IMD_T_1P0": ("IMD gridded daily max/min temperature 1 deg (SWAT text grids)", IMD1T,
                  "1969-01-01..2005-12-31", "1 deg grid", "observed", "IMD data policy"),
    "DAILY_WEATHER_CSV": ("Daily rain / Tmax / Tmin table 1951-2024 (file DOC-20261023-WA0007.csv)", DAILY_CSV,
                          "1951-01-01..2024-06-20", "single series, location not stated", "observed", "Provenance and station unknown"),
    "CFG_INTERVENTIONS": ("Declared intervention assumptions (master plan Table 9 illustrative units)", "config/intervention_assumptions.csv",
                          "2026-10-24", "per unit", "assumed", "Project configuration"),
    "CFG_PARAMETERS": ("Declared model parameters with evidence classes", "config/model_parameters.json",
                       "2026-10-24", "-", "assumed", "Project configuration"),
    "CFG_SCENARIOS": ("Illustrative stress-test presets (master plan §6.3)", "config/scenarios.csv",
                      "2026-10-24", "-", "assumed", "Project configuration"),
}


@dataclass
class Report:
    checks: list[dict] = field(default_factory=list)
    quarantined: list[dict] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)

    def check(self, dataset: str, name: str, status: str, detail: str, **extra) -> None:
        self.checks.append({"dataset": dataset, "check": name, "status": status, "detail": detail, **extra})


def q(value, unit, evidence: Evidence, sources=(), note="", low=None, high=None) -> str:
    if value is not None and isinstance(value, (float, np.floating)) and not np.isfinite(value):
        value = None
    if value is None and evidence is not Evidence.MISSING:
        return Quantity.missing(unit, note or "not available", tuple(sources)).model_dump_json()
    return Quantity(value=None if value is None else float(value), unit=unit, evidence=evidence, source_ids=tuple(sources),
                    note=note, low=low, high=high).model_dump_json()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_kml(path: Path) -> gpd.GeoDataFrame:
    """Read every layer; malformed geometries become null (counted in column _bad_geometry) instead of aborting."""
    frames = []
    for layer, _ in pyogrio.list_layers(path):
        d = gpd.read_file(path, layer=layer, on_invalid="ignore").assign(_layer=layer)
        d["_bad_geometry"] = d.geometry.isna() | d.geometry.is_empty
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]


# --------------------------------------------------------------------------- inventory
def inventory(raw: Path, report: Report) -> pd.DataFrame:
    rows = []
    for p in sorted(raw.rglob("*")):
        if not p.is_file() or p.suffix == ".part":
            continue
        rel = p.relative_to(raw).as_posix()
        rows.append({"relative_path": rel, "size_bytes": p.stat().st_size, "extension": p.suffix.lower(),
                     "sha256": sha256(p) if p.stat().st_size < 300_000_000 else ""})
    inv = pd.DataFrame(rows)
    listing_path = raw.parent / "drive_listing.json"
    if listing_path.exists():
        listing = pd.DataFrame(json.loads(listing_path.read_text(encoding="utf-8")))
        listing["relative_path"] = listing["path"].str.replace("\\", "/", regex=False)
        present = set(inv["relative_path"])
        listing["downloaded"] = listing["relative_path"].isin(present)
        not_dl = listing[~listing["downloaded"]]
        report.check("collection", "drive_listing_vs_local", "info",
                     f"{len(listing)} files listed in the shared Drive folder; {int(listing['downloaded'].sum())} present locally; "
                     f"{len(not_dl)} not downloaded (all-India IMD cells outside the Bengaluru window, non-Bengaluru SRTM tiles, "
                     "duplicate archives, 1.9 GB global HWSD raster)")
        inv = inv.merge(listing[["relative_path", "id"]], on="relative_path", how="left").rename(columns={"id": "drive_file_id"})
    claimed = raw / "curated" / "source_inventory.csv"
    if claimed.exists():
        cl = pd.read_csv(claimed, encoding="utf-8-sig")
        cl_paths = set(cl["relative_path"].str.replace("\\", "/", regex=False))
        listed = set(inv["relative_path"].str.replace("^raw/", "", regex=True))
        if listing_path.exists():
            listed |= set(listing["relative_path"].str.replace("^raw/", "", regex=True))
        missing_claims = sorted(p for p in cl_paths if p not in listed)
        report.check("collection", "source_inventory_claims", "warn" if missing_claims else "pass",
                     f"{len(cl_paths)} paths claimed in curated/source_inventory.csv; {len(missing_claims)} are not in the shared folder",
                     examples=missing_claims[:15])
    # Personal-information screen on tabular files: header names only, values are not exported.
    pii = re.compile(r"(phone|mobile|email|aadhaar|address|owner|person|name_of|customer)", re.I)
    flagged = []
    for p in raw.rglob("*.csv"):
        try:
            header = pd.read_csv(p, nrows=0, encoding="utf-8-sig", encoding_errors="replace").columns
        except Exception:
            continue
        hits = [c for c in header if pii.search(str(c))]
        if hits:
            flagged.append({"file": p.relative_to(raw).as_posix(), "columns": hits})
    report.check("collection", "personal_information_screen", "warn" if flagged else "pass",
                 "CSV headers scanned for personal-data fields" + (f"; flagged {flagged}" if flagged else "; none found"),
                 flagged=flagged)
    report.check("collection", "unrelated_or_document_files", "info",
                 "PDF/XLS reports, population web-page prints and archive duplicates are retained as references only and "
                 "are not ingested into the application")
    nc = list(raw.rglob("*.nc"))
    report.check("collection", "netcdf_2015_2025", "fail" if not nc else "pass",
                 "No NetCDF files exist in the collection; the 2015-2025 IMD NetCDF rainfall described in the brief is absent"
                 if not nc else f"{len(nc)} NetCDF files present")
    if not nc:
        report.gaps.append("2015-2025 IMD NetCDF rainfall is not present in the collection; gridded rainfall ends 2005.")
    kml_lu = [p for p in raw.rglob("*.km[lz]") if "land" in p.as_posix().lower()]
    report.check("collection", "landuse_2017_kml", "fail" if not kml_lu else "pass",
                 "No 2017 land-use KML/KMZ layer exists in the collection; land-use rasters present are global/continental "
                 "products (GIAM ~10 km, WaterBase) unsuitable for ward scale" if not kml_lu else f"{len(kml_lu)} land-use KML/KMZ files")
    if not kml_lu:
        report.gaps.append("No ward-scale land-use layer (the 2017 KML/KMZ is absent); vegetation and non-building imperviousness are assumptions.")
    return inv


# --------------------------------------------------------------------------- wards
def load_wards(raw: Path, report: Report) -> gpd.GeoDataFrame:
    g = read_kml(raw / WARDS)
    g = g[[c for c in g.columns if not c.endswith("_kn")]].copy()
    num = ["TOT_P", "TOT_M", "TOT_F", "SC_P", "ST_P", "low_range", "high_range"]
    for c in num:
        g[c] = pd.to_numeric(g[c], errors="coerce")
    g["ward_key"] = "GBA-C" + g["corporation_id"].astype(str) + "-W" + g["ward_id"].astype(str).str.zfill(3)
    dup = int(g["ward_key"].duplicated().sum())
    report.check("wards", "composite_key_unique", "pass" if dup == 0 else "fail",
                 f"ward_id repeats across the 5 corporations ({int(g['ward_id'].duplicated().sum())} repeats); composite key "
                 f"corporation_id+ward_id has {dup} duplicates")
    invalid = int((~g.is_valid).sum())
    g["geometry"] = g.geometry.make_valid()
    report.check("wards", "geometry_validity", "corrected" if invalid else "pass",
                 f"{invalid} invalid polygons repaired with make_valid (topology only)")
    gu = g.to_crs(UTM)
    g["area_m2"] = gu.area
    g["centroid_lon"] = gu.centroid.to_crs(WGS).x
    g["centroid_lat"] = gu.centroid.to_crs(WGS).y
    diff = g["TOT_P"] - (g["TOT_M"] + g["TOT_F"])
    g["pop_sum_mismatch"] = diff
    g["pop_flag"] = np.where(diff.abs() > 0.5, np.where(diff.abs() > 50, "major_mismatch", "minor_mismatch"), "consistent")
    n_bad = int((diff.abs() > 0.5).sum())
    report.check("wards", "population_total_vs_sex_sum", "warn",
                 f"{n_bad} of {len(g)} wards have TOT_P != TOT_M + TOT_F (max |diff| {diff.abs().max():.0f}); source values "
                 "preserved, TOT_P used as published total, records flagged",
                 wards_major=sorted(g.loc[g.pop_flag == "major_mismatch", "ward_key"].tolist()))
    g["sc_st_share"] = (g["SC_P"] + g["ST_P"]) / g["TOT_P"]
    outside = int((~((g.TOT_P >= g.low_range) & (g.TOT_P <= g.high_range))).sum())
    report.check("wards", "population_within_delimitation_band", "pass" if outside == 0 else "warn",
                 f"{outside} wards fall outside their own low_range/high_range delimitation band; population reference year "
                 "is not stated in the source (delimitation figures, likely Census-2011-based)")
    return g


# --------------------------------------------------------------------------- flood points
def load_flood_points(raw: Path, wards: gpd.GeoDataFrame, report: Report) -> gpd.GeoDataFrame:
    frames = []
    for p in sorted((raw / FLOOD_DIR).glob("*.kml")):
        d = read_kml(p)
        d["source_file"] = p.name
        frames.append(d)
    pts = pd.concat(frames, ignore_index=True)
    pts["point_class"] = pts["_layer"].map({"flood_prone_locations": "flood_prone", "flood_vulnerable_locations": "flood_vulnerable",
                                            "lowlying_locations": "low_lying"}).fillna(pts["_layer"])
    pts["lon"] = pts.geometry.x
    pts["lat"] = pts.geometry.y
    pts["site_id"] = pts["point_class"] + "-" + pts["OBJECTID"].astype("Int64").astype(str)
    n = len(pts)
    finite = np.isfinite(pts.lon) & np.isfinite(pts.lat)
    in_bbox = finite & pts.lon.between(BLR_BBOX[0], BLR_BBOX[2]) & pts.lat.between(BLR_BBOX[1], BLR_BBOX[3])
    pts["coord_valid"] = in_bbox
    bad = pts.loc[~in_bbox, ["site_id", "lon", "lat"]]
    report.check("flood_points", "coordinate_validity", "corrected" if len(bad) else "pass",
                 f"{len(bad)} of {n} points have invalid or out-of-area coordinates and are excluded",
                 excluded=bad.to_dict("records"))
    pts["coord_key"] = pts.lon.round(6).astype(str) + "," + pts.lat.round(6).astype(str)
    valid = pts[pts.coord_valid].copy()
    dup_groups = valid[valid.duplicated("coord_key", keep=False)].groupby("coord_key")["site_id"].apply(list)
    valid["duplicate_of"] = None
    first = valid.drop_duplicates("coord_key").set_index("coord_key")["site_id"]
    is_dup = valid.duplicated("coord_key")
    valid.loc[is_dup, "duplicate_of"] = valid.loc[is_dup, "coord_key"].map(first)
    report.check("flood_points", "duplicate_coordinates", "corrected" if len(dup_groups) else "pass",
                 f"{len(dup_groups)} duplicate-coordinate groups; {int(is_dup.sum())} redundant rows retained but flagged "
                 "duplicate_of and excluded from counts", groups=[list(v) for v in dup_groups.values])
    joined = gpd.sjoin(valid.set_crs(WGS, allow_override=True), wards[["ward_key", "ward_name", "zone_name", "geometry"]],
                       how="left", predicate="within").drop(columns="index_right")
    outside_city = int(joined["ward_key"].isna().sum())
    report.check("flood_points", "ward_join", "pass", f"{len(joined) - outside_city} valid points joined to current GBA wards; "
                 f"{outside_city} fall outside all 369 wards")
    joined = joined.rename(columns={"WARD_NAME": "legacy_ward_name", "WARDNO": "legacy_ward_no", "ZONE": "legacy_zone"})
    for c in ("legacy_ward_name", "legacy_ward_no", "legacy_zone"):
        if c not in joined:
            joined[c] = None
    report.check("flood_points", "legacy_identifiers", "info",
                 "WARDNO/ZONE attributes on flood-vulnerable points are legacy BBMP (198-ward) identifiers; they are kept as "
                 "legacy_* fields and never used as current GBA ward keys")
    joined["usable_for_counts"] = joined["duplicate_of"].isna() & joined["ward_key"].notna()
    joined["status"] = "hazard_marker_not_construction_site"
    return joined


# --------------------------------------------------------------------------- footprints, drains, groundwater
def footprints_by_ward(raw: Path, wards: gpd.GeoDataFrame, report: Report) -> pd.DataFrame:
    fp = pyogrio.read_dataframe(raw / FOOTPRINTS, columns=[])
    fp = fp.set_crs(WGS, allow_override=True)
    fu = fp.to_crs(UTM)
    cent = gpd.GeoDataFrame({"area_m2": fu.area.values}, geometry=fu.centroid.to_crs(WGS).values, crs=WGS)
    j = gpd.sjoin(cent, wards[["ward_key", "geometry"]], how="inner", predicate="within")
    agg = j.groupby("ward_key").agg(footprint_m2=("area_m2", "sum"), building_count=("area_m2", "size")).reset_index()
    report.check("footprints", "spatial_assignment", "pass",
                 f"{len(fp):,} footprints; {len(j):,} assigned to wards by centroid; total area {cent.area_m2.sum() / 1e6:.1f} km2. "
                 "Footprints are detected roofs, not proof of structural capacity, ownership, access or permission")
    return agg


def drains_by_ward(raw: Path, wards: gpd.GeoDataFrame, report: Report) -> pd.DataFrame:
    files = sorted((raw / DRAIN_DIR).glob("*.kml"))
    seen, frames = {}, []
    for p in files:
        h = sha256(p)
        if h in seen:
            report.check("drainage", "duplicate_file", "corrected", f"{p.name} is byte-identical to {seen[h]}; ignored")
            continue
        seen[h] = p.name
        d = read_kml(p)
        if d["_bad_geometry"].any():
            report.check("drainage", "malformed_geometry", "corrected",
                         f"{p.name}: {int(d['_bad_geometry'].sum())} of {len(d)} features have malformed/empty geometry and are dropped")
        if "merged" in set(d["_layer"]):
            report.check("drainage", "merged_layer", "corrected",
                         f"{p.name}: layer 'merged' is the union of the primary, secondary and tertiary files (same OBJECTIDs "
                         "and lengths); excluded to avoid double counting")
            d = d[d["_layer"] != "merged"]
        d = d[d.geom_type.isin(["LineString", "MultiLineString"])]
        if len(d):
            d = d.assign(drain_class=d["_layer"].str.replace(".geojson", "", regex=False).str.replace("blr_swd_", "swd_", regex=False))
            frames.append(d[["drain_class", "geometry"]])
    if not frames:
        report.gaps.append("No storm-water drain geometry available.")
        return pd.DataFrame(columns=["ward_key", "drain_length_m"])
    lines = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=WGS).to_crs(UTM)
    w = wards[["ward_key", "geometry"]].to_crs(UTM)
    inter = gpd.overlay(lines, w, how="intersection", keep_geom_type=True)
    inter["length_m"] = inter.length
    agg = inter.pivot_table(index="ward_key", columns="drain_class", values="length_m", aggfunc="sum", fill_value=0.0)
    agg.columns = [f"drain_{c}_m" for c in agg.columns]
    agg["drain_length_m"] = agg.sum(axis=1)
    agg = agg.reset_index()
    report.check("drainage", "network_length", "info",
                 f"{len(lines)} drain features ({', '.join(sorted(lines.drain_class.unique()))}); length per ward computed. "
                 "Network geometry does not give hydraulic capacity or condition")
    return agg


def groundwater_by_ward(raw: Path, wards: gpd.GeoDataFrame, report: Report) -> pd.DataFrame:
    path = raw / GROUNDWATER
    if not path.exists():
        report.gaps.append("Groundwater potential layer missing.")
        return pd.DataFrame(columns=["ward_key"])
    gw = read_kml(path)[["GW_PROS", "geometry"]].to_crs(UTM)
    gw["geometry"] = gw.geometry.make_valid()
    w = wards[["ward_key", "geometry"]].to_crs(UTM)
    inter = gpd.overlay(gw, w, how="intersection", keep_geom_type=True)
    inter["a"] = inter.area
    share = inter.pivot_table(index="ward_key", columns="GW_PROS", values="a", aggfunc="sum", fill_value=0)
    share = share.div(share.sum(axis=1), axis=0)
    share.columns = [f"gw_share_{c.lower().replace(' ', '_')}" for c in share.columns]
    report.check("groundwater", "class_shares", "info", f"groundwater potential classes {sorted(gw.GW_PROS.dropna().unique())} "
                 "intersected with wards (area shares)")
    return share.reset_index()


def waterbodies_by_ward(raw: Path, wards: gpd.GeoDataFrame, report: Report) -> pd.DataFrame:
    """Lake/tank and pond polygons per ward. Files identical to flood-point KMLs are reclassified, not counted."""
    folder = raw / WATERBODIES
    files = sorted(folder.glob("*.kml")) if folder.exists() else []
    flood_hashes = {sha256(p): p.name for p in (raw / FLOOD_DIR).glob("*.kml")}
    frames = []
    for p in files:
        h = sha256(p)
        if h in flood_hashes:
            report.check("waterbodies", "classification", "corrected", f"{p.name} is identical to flood-location file "
                         f"{flood_hashes[h]}; it is a hazard-point layer, not a waterbody layer")
            continue
        d = read_kml(p)
        d = d[d.geom_type.isin(["Polygon", "MultiPolygon"])]
        report.check("waterbodies", "classification", "info", f"{p.name}: layer(s) {sorted(d['_layer'].unique())}, "
                     f"{len(d)} polygons used as waterbodies")
        frames.append(d.assign(wb_class=d["_layer"].str.replace("blr_", "", regex=False))[["wb_class", "geometry"]])
    if not frames:
        report.gaps.append("No lake/tank/pond polygon layer could be verified in raw/waterbodies.")
        return pd.DataFrame(columns=["ward_key", "waterbody_area_m2", "waterbody_count"])
    wb = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=WGS).to_crs(UTM)
    wb["geometry"] = wb.geometry.make_valid()
    inter = gpd.overlay(wb, wards[["ward_key", "geometry"]].to_crs(UTM), how="intersection", keep_geom_type=True)
    inter["a"] = inter.area
    area = inter.pivot_table(index="ward_key", columns="wb_class", values="a", aggfunc="sum", fill_value=0.0)
    area.columns = [f"{c}_area_m2" for c in area.columns]
    count = inter.pivot_table(index="ward_key", columns="wb_class", values="a", aggfunc="size", fill_value=0)
    count.columns = [f"{c}_count" for c in count.columns]
    out = area.join(count, how="outer").fillna(0)
    out["waterbody_area_m2"] = out[[c for c in out.columns if c.endswith("_area_m2")]].sum(axis=1)
    out["waterbody_count"] = out[[c for c in out.columns if c.endswith("_count")]].sum(axis=1).astype(int)
    report.check("waterbodies", "ward_overlay", "info", f"{len(wb)} tank/pond polygons intersected with wards; source date and "
                 "current water-spread not stated (polygons may include dry or encroached tanks)")
    return out.reset_index()


# --------------------------------------------------------------------------- climate
def read_swat_grid(path: Path, columns: tuple[str, ...]) -> pd.DataFrame:
    """SWAT weather text grid: line 1 = start date YYYYMMDD, then one record per consecutive day."""
    lines = path.read_text(encoding="utf-8").split()
    start = datetime.strptime(lines[0], "%Y%m%d").date()
    values = [ln.split(",") for ln in lines[1:]]
    df = pd.DataFrame(values, columns=list(columns)).apply(pd.to_numeric, errors="coerce")
    df.insert(0, "date", pd.date_range(start, periods=len(df), freq="D"))
    return df


def imd_rainfall(raw: Path, report: Report) -> pd.DataFrame:
    folder = raw / IMD05
    frames = []
    for p in sorted(folder.glob("X*Y*.txt")):
        m = re.match(r"X(\d+)Y(\d+)", p.stem)
        lon, lat = int(m.group(1)) / 10, int(m.group(2)) / 10
        if not (BLR_BBOX[0] - 0.5 <= lon <= BLR_BBOX[2] + 0.5 and BLR_BBOX[1] - 0.5 <= lat <= BLR_BBOX[3] + 0.5):
            continue
        d = read_swat_grid(p, ("precipitation_mm",))
        d["grid_id"], d["lon"], d["lat"] = p.stem, lon, lat
        frames.append(d)
    rain = pd.concat(frames, ignore_index=True)
    neg = int((rain.precipitation_mm < 0).sum())
    nan = int(rain.precipitation_mm.isna().sum())
    rain.loc[rain.precipitation_mm < 0, "precipitation_mm"] = np.nan  # SWAT missing flag (-99) -> missing, never zero
    report.check("rainfall", "imd_time_axis", "corrected",
                 f"{rain.grid_id.nunique()} IMD 0.5 deg cells parsed; dates reconstructed from each file's own start-date header "
                 f"({rain.date.min().date()}..{rain.date.max().date()}, {rain.groupby('grid_id').size().iloc[0]} consecutive days)",
                 missing_flags=neg, unparseable=nan)
    curated = raw / CURATED_RAIN
    if curated.exists():
        old = pd.read_csv(curated)
        report.quarantined.append({"file": "curated/rainfall.csv", "rows": int(len(old)),
                                   "reason": f"all rows dated {sorted(old['date'].unique())[:3]}; superseded by reconstruction"})
        matches = []
        for gid, g in old.groupby("grid_id"):
            src = rain[rain.grid_id == gid]
            same = len(src) == len(g) and np.allclose(src.precipitation_mm.to_numpy(), g.precipitation_raw.to_numpy(), equal_nan=True)
            matches.append({"grid_id": gid, "rows_curated": int(len(g)), "rows_source": int(len(src)), "values_identical_in_order": bool(same)})
        ok = all(m["values_identical_in_order"] for m in matches)
        report.check("rainfall", "curated_file_date_bug", "corrected" if ok else "warn",
                     "curated/rainfall.csv had every row dated 1971-01-01. Its values match the raw IMD files value-for-value "
                     "in order, so the correct date of each row is the source start date plus row offset; the broken file is "
                     "quarantined and replaced by rainfall_daily.csv" if ok else "curated values do not match raw sources; quarantined only",
                     cells=matches)
    return rain


def imd_temperature(raw: Path, report: Report) -> pd.DataFrame:
    frames = []
    for p in sorted((raw / IMD1T).glob("TY*X*.txt")):
        m = re.match(r"TY(\d+)X(\d+)", p.stem)
        lat, lon = int(m.group(1)) / 10, int(m.group(2)) / 10
        if not (12.0 <= lat <= 14.0 and 77.0 <= lon <= 78.0):
            continue
        d = read_swat_grid(p, ("tmax_c", "tmin_c"))
        d["grid_id"], d["lat"], d["lon"] = p.stem, lat, lon
        frames.append(d)
    t = pd.concat(frames, ignore_index=True)
    for c in ("tmax_c", "tmin_c"):
        t.loc[(t[c] < -50) | (t[c] > 60), c] = np.nan
    report.check("temperature", "imd_time_axis", "pass", f"{t.grid_id.nunique()} IMD 1 deg temperature cells, "
                 f"{t.date.min().date()}..{t.date.max().date()}; dates from file headers")
    return t


def daily_weather_csv(raw: Path, report: Report) -> pd.DataFrame:
    p = raw / DAILY_CSV
    d = pd.read_csv(p)
    d["date"] = pd.to_datetime(d["Date"], format="%d-%m-%Y", errors="coerce")
    trace = int((d["Rain"].astype(str).str.strip().str.lower() == "tr").sum())
    d["rain_mm"] = pd.to_numeric(d["Rain"].replace({"Tr": 0.05, "tr": 0.05, "TR": 0.05}), errors="coerce")
    d["tmax_c"] = pd.to_numeric(d["Temp Max"], errors="coerce")
    d["tmin_c"] = pd.to_numeric(d["Temp Min"], errors="coerce")
    bad_dates = int(d["date"].isna().sum())
    dup = int(d["date"].duplicated().sum())
    gaps = int(pd.date_range(d.date.min(), d.date.max()).difference(d.date.dropna()).size)
    report.check("daily_weather_csv", "parse", "warn",
                 f"{len(d)} rows {d.date.min().date()}..{d.date.max().date()}; {trace} 'Tr' (trace) values set to 0.05 mm; "
                 f"{bad_dates} unparseable dates; {dup} duplicate dates; {gaps} missing days. Station location and units are "
                 "not documented, so this series is used only as a city-level cross-check, not as zone input")
    return d[["date", "rain_mm", "tmax_c", "tmin_c"]].dropna(subset=["date"])


def urban_heat_check(raw: Path, report: Report) -> None:
    p = raw / HEAT_CSV
    if not p.exists():
        report.check("urban_heat", "coverage", "fail", "urban heat CSV not present locally")
        return
    d = pd.read_csv(p)
    lat = next((c for c in d.columns if c.lower() in ("latitude", "lat")), None)
    lon = next((c for c in d.columns if c.lower() in ("longitude", "lon", "long")), None)
    if lat is None or lon is None:
        report.check("urban_heat", "coverage", "fail", f"no coordinate columns in {list(d.columns)[:10]}")
        return
    inside = d[lat].between(BLR_BBOX[1], BLR_BBOX[3]) & d[lon].between(BLR_BBOX[0], BLR_BBOX[2])
    report.check("urban_heat", "coverage", "fail" if inside.sum() == 0 else "warn",
                 f"{len(d)} rows spanning lat {d[lat].min():.2f}..{d[lat].max():.2f}, lon {d[lon].min():.2f}..{d[lon].max():.2f}; "
                 f"{int(inside.sum())} rows inside the Bengaluru window. Rows outside Bengaluru are rejected and none are joined "
                 "to pilot zones")
    report.quarantined.append({"file": HEAT_CSV, "rows": int(len(d)), "reason": f"{int((~inside).sum())} rows outside Bengaluru"})
    if inside.sum() == 0:
        report.gaps.append("No Bengaluru land-surface-temperature observations; heat uses IMD 1 deg air temperature (coarse).")


# --------------------------------------------------------------------------- pilot zones
def select_pilot_zones(wards: gpd.GeoDataFrame, report: Report) -> tuple[pd.DataFrame, str]:
    """Three wards of GBA's Yelahanka zone with distinct dominant stresses (rule is fully data-driven)."""
    cand = wards[wards["zone_name"] == PILOT_GBA_ZONE].copy()
    cand = cand[cand["pop_flag"] != "major_mismatch"]
    cand["flood_density"] = cand["flood_points"] / (cand["area_m2"] / 1e6)
    # Water-stress proxy: least surface-water storage (tank + pond area) per resident. The groundwater-potential
    # layer masks built-up wards as 'Habitation Mask', so it cannot discriminate between urban wards.
    cand["waterbody_m2_per_resident_neg"] = -(cand["waterbody_area_m2"] / cand["TOT_P"])
    chosen, rows = [], []
    rules = [
        ("rain", "flood_density", "highest density of validated flood/low-lying hazard markers (per km2)"),
        ("heat", "built_fraction", "highest building-footprint fraction of ward area (heat-exposure proxy)"),
        ("water", "waterbody_m2_per_resident_neg", "least tank + pond surface area per resident (water-storage proxy); ties broken by largest population (greatest demand)"),
    ]
    for profile, col, why in rules:
        pool = cand[~cand["ward_key"].isin(chosen)].sort_values([col, "TOT_P"], ascending=[False, False])
        if pool[col].isna().all() or (profile == "rain" and pool[col].max() <= 0):
            pool = cand[~cand["ward_key"].isin(chosen)].sort_values(["drain_density", "TOT_P"], ascending=False)
            why = "no validated hazard markers in candidate wards; highest storm-drain density used instead"
        pick = pool.iloc[0]
        chosen.append(pick["ward_key"])
        rows.append({"ward_key": pick["ward_key"], "profile": profile, "rule": why, "value": float(pick[col]) if pd.notna(pick[col]) else None})
    sel = pd.DataFrame(rows)
    rule = (f"Candidates: the {len(cand)} wards of GBA zone '{PILOT_GBA_ZONE}' (master plan Yelahanka sub-catchment context) "
            "excluding wards with major population inconsistencies; one ward per distinct dominant stress.")
    report.check("pilot_zones", "selection", "pass", rule, selected=rows)
    return sel, rule


def build(raw: Path, out: Path, version: str) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    report = Report()
    params = load_parameters()
    inv = inventory(raw, report)
    wards = load_wards(raw, report)
    sites = load_flood_points(raw, wards, report)
    counts = sites[sites.usable_for_counts].groupby("ward_key").size().rename("flood_points")
    fp = footprints_by_ward(raw, wards, report)
    dr = drains_by_ward(raw, wards, report)
    gw = groundwater_by_ward(raw, wards, report)
    wb = waterbodies_by_ward(raw, wards, report)
    urban_heat_check(raw, report)
    rain = imd_rainfall(raw, report)
    temp = imd_temperature(raw, report)
    daily = daily_weather_csv(raw, report)

    w = wards.merge(fp, on="ward_key", how="left").merge(dr, on="ward_key", how="left").merge(gw, on="ward_key", how="left")
    w = w.merge(wb, on="ward_key", how="left").merge(counts, on="ward_key", how="left")
    w["waterbody_area_m2"] = w["waterbody_area_m2"].fillna(0.0)
    w["waterbody_count"] = w["waterbody_count"].fillna(0).astype(int)
    w["flood_points"] = w["flood_points"].fillna(0).astype(int)
    w["footprint_m2"] = w["footprint_m2"].fillna(0.0)
    w["building_count"] = w["building_count"].fillna(0).astype(int)
    w["drain_length_m"] = w["drain_length_m"].fillna(0.0)
    w["built_fraction"] = (w["footprint_m2"] / w["area_m2"]).clip(0, 1)
    w["drain_density"] = w["drain_length_m"] / (w["area_m2"] / 1e6)
    w = gpd.GeoDataFrame(w, geometry="geometry", crs=WGS)

    sel, rule = select_pilot_zones(w, report)
    city_sc_st = float((w.SC_P.sum() + w.ST_P.sum()) / w.TOT_P.sum())
    nbi = float(params["non_building_impervious_fraction"])
    c_imp, c_per = float(params["c_impervious"]), float(params["c_pervious"])
    dur = float(params["design_storm_duration_h"])
    roof_frac, plant_frac = float(params["roof_eligible_fraction"]), float(params["plantable_fraction_of_open_land"])
    t_lo, t_hi = params["temperature_norm_bounds_c"]
    cells = rain.groupby("grid_id")[["lon", "lat"]].first()
    tcells = temp.groupby("grid_id")[["lon", "lat"]].first()

    zone_rows, flat_rows, feats, climate_rows = [], [], [], []
    rain_keep = set()
    letters = "ABC"
    for i, s in enumerate(sel.itertuples()):
        r = w[w.ward_key == s.ward_key].iloc[0]
        zid = f"Z{letters[i]}"
        # nearest IMD 0.5 deg rainfall cell and the 1 deg temperature cell containing the centroid
        d2 = (cells.lon - r.centroid_lon) ** 2 + (cells.lat - r.centroid_lat) ** 2
        cell = d2.idxmin()
        rain_keep.add(cell)
        rc = rain[rain.grid_id == cell].dropna(subset=["precipitation_mm"])
        annual_max = rc.groupby(rc.date.dt.year)["precipitation_mm"].max()
        annual_tot = rc.groupby(rc.date.dt.year)["precipitation_mm"].sum()
        p24 = float(annual_max.mean())
        p_event = hydrology.imd_short_duration_depth_mm(p24, dur)
        td = (tcells.lon - r.centroid_lon).abs() + (tcells.lat - r.centroid_lat).abs()
        tcell = td.idxmin()
        tc = temp[temp.grid_id == tcell]
        summer = tc[tc.date.dt.month.isin([3, 4, 5])]["tmax_c"].mean()
        area_m2 = float(r.area_m2)
        built = float(r.built_fraction)
        imperv = built + (1 - built) * nbi
        veg = max(0.0, 1.0 - imperv)
        c = hydrology.composite_runoff_coefficient(imperv, c_imp, c_per)
        event_runoff = c * p_event / 1000.0 * area_m2
        tnorm = heat.normalise_temperature(float(summer), t_lo, t_hi)
        h = heat.heat_index(tnorm, imperv, veg)
        v = equity.vulnerability_weight(float(r.sc_st_share), city_sc_st, float(params["equity_alpha"]))
        pop_note = f"published TOT_P; sex-sum check {r.pop_flag} (diff {r.pop_sum_mismatch:+.0f}); reference year not stated"
        name = f"{r.ward_name} ({r.zone_name})"
        zone_rows.append({
            "zone_id": zid, "zone_name": name, "ward_keys": r.ward_key, "gba_corporation": r.Corporation,
            "gba_zone_name": r.zone_name, "centroid_lat": round(r.centroid_lat, 6), "centroid_lon": round(r.centroid_lon, 6),
            "rainfall_cell": cell, "selection_reason": f"{s.profile}-stress profile: {s.rule}",
            "area_ha": q(area_m2 / 1e4, "ha", Evidence.DERIVED, ["GBA_WARDS_2025"], "geodesic area in UTM 43N"),
            "population": q(r.TOT_P, "persons", Evidence.OBSERVED, ["GBA_WARDS_2025"], pop_note),
            "sc_st_share": q(r.sc_st_share, "fraction", Evidence.DERIVED, ["GBA_WARDS_2025"], "(SC_P + ST_P) / TOT_P"),
            "built_fraction": q(built, "fraction", Evidence.DERIVED, ["MS_FOOTPRINTS", "GBA_WARDS_2025"],
                                f"{int(r.building_count):,} footprints, {r.footprint_m2:,.0f} m2"),
            "impervious_fraction": q(imperv, "fraction", Evidence.ASSUMED, ["MS_FOOTPRINTS", "CFG_PARAMETERS"],
                                     f"buildings + {nbi:.0%} of remaining area assumed paved"),
            "vegetation_fraction": q(veg, "fraction", Evidence.ASSUMED, ["CFG_PARAMETERS"], "1 - impervious (no ward land-cover layer)"),
            "runoff_coefficient": q(c, "-", Evidence.DERIVED, ["MS_FOOTPRINTS", "CFG_PARAMETERS"], f"area-weighted C ({c_imp}/{c_per})",
                                    low=hydrology.composite_runoff_coefficient(imperv, 0.75, 0.10),
                                    high=hydrology.composite_runoff_coefficient(imperv, 0.95, 0.35)),
            "eligible_roof_m2": q(r.footprint_m2 * roof_frac, "m2", Evidence.ASSUMED, ["MS_FOOTPRINTS", "CFG_PARAMETERS"],
                                  f"{roof_frac:.0%} of detected footprint area; eligibility not surveyed"),
            "plantable_land_m2": q((area_m2 - r.footprint_m2) * plant_frac, "m2", Evidence.ASSUMED, ["MS_FOOTPRINTS", "CFG_PARAMETERS"],
                                   f"{plant_frac:.0%} of non-building area; public land availability not verified"),
            "design_p24_mm": q(p24, "mm/day", Evidence.DERIVED, ["IMD_RF_0P5"], f"mean annual maximum daily rainfall, cell {cell}, "
                               f"{annual_max.index.min()}-{annual_max.index.max()}", low=float(annual_max.quantile(0.1)),
                               high=float(annual_max.quantile(0.9))),
            "design_event_mm": q(p_event, "mm in 1 h", Evidence.ESTIMATED, ["IMD_RF_0P5"], "IMD reduction formula P24 (t/24)^(1/3)"),
            "design_event_runoff_m3": q(event_runoff, "m3 per design event", Evidence.DERIVED, ["IMD_RF_0P5", "MS_FOOTPRINTS"],
                                        "C x P_event x area"),
            "summer_tmax_c": q(summer, "degC", Evidence.OBSERVED, ["IMD_T_1P0"], f"Mar-May mean daily max, 1 deg cell {tcell}, "
                               f"{tc.date.min().year}-{tc.date.max().year}; same cell for nearby zones (coarse)"),
            "heat_index": q(h, "0-1 index", Evidence.DERIVED, ["IMD_T_1P0", "MS_FOOTPRINTS", "CFG_PARAMETERS"],
                            "0.5 Tnorm + 0.3 impervious + 0.2 (1 - vegetation)"),
            "vulnerability_weight": q(v, "-", Evidence.DERIVED, ["GBA_WARDS_2025", "CFG_PARAMETERS"],
                                      f"1 + alpha (SC/ST share / city mean {city_sc_st:.3f} - 1)"),
            "flood_points": q(int(r.flood_points), "count", Evidence.OBSERVED, ["BLR_FLOOD_POINTS"],
                              "validated, de-duplicated hazard markers inside the ward"),
            "drain_length_m": q(r.drain_length_m, "m", Evidence.DERIVED, ["BLR_SWD"], "primary + secondary + tertiary drain length inside ward"),
            "waterbody_features": q(int(r.waterbody_count), "count", Evidence.OBSERVED, ["BLR_WATERBODIES"],
                                    f"tank/pond polygons intersecting the ward; {r.waterbody_area_m2:,.0f} m2 total"),
        })
        flat_rows.append({
            "zone_id": zid, "zone_name": name, "ward_key": r.ward_key, "ward_name": r.ward_name, "gba_zone_name": r.zone_name,
            "gba_corporation": r.Corporation, "assembly": r.Assembly, "area_ha": round(area_m2 / 1e4, 2),
            "population_persons": int(r.TOT_P), "population_flag": r.pop_flag, "population_reference_year": "not stated in source",
            "sc_st_share": round(float(r.sc_st_share), 4), "building_count": int(r.building_count),
            "footprint_m2": round(float(r.footprint_m2), 1), "built_fraction": round(built, 4),
            "flood_points_count": int(r.flood_points), "drain_length_m": round(float(r.drain_length_m), 1),
            "waterbody_count": int(r.waterbody_count), "waterbody_area_m2": round(float(r.waterbody_area_m2), 1),
            "rainfall_cell": cell, "temperature_cell": tcell, "design_p24_mm_day": round(p24, 2), "design_event_mm_1h": round(p_event, 2),
            "runoff_coefficient": round(c, 3), "summer_tmax_c": round(float(summer), 2), "heat_index_0_1": round(h, 4),
            "selection_profile": s.profile, "selection_rule": s.rule, "source_ids": "GBA_WARDS_2025;MS_FOOTPRINTS;BLR_FLOOD_POINTS;BLR_SWD;BLR_WATERBODIES;IMD_RF_0P5;IMD_T_1P0",
            **{k: round(float(r[k]), 4) for k in r.index if str(k).startswith("gw_share_") and pd.notna(r[k])},
        })
        feats.append({"type": "Feature", "properties": {"zone_id": zid, "zone_name": name, "ward_key": r.ward_key,
                                                        "population": int(r.TOT_P), "area_ha": round(area_m2 / 1e4, 2),
                                                        "source_id": "GBA_WARDS_2025"},
                      "geometry": json.loads(gpd.GeoSeries([r.geometry], crs=WGS).simplify(0.00002).to_json())["features"][0]["geometry"]})
        climate_rows.append({"zone_id": zid, "rainfall_cell": cell, "years": f"{annual_tot.index.min()}-{annual_tot.index.max()}",
                             "mean_annual_rain_mm": round(float(annual_tot.mean()), 1), "p10_annual_rain_mm": round(float(annual_tot.quantile(0.1)), 1),
                             "p90_annual_rain_mm": round(float(annual_tot.quantile(0.9)), 1), "mean_annual_max_daily_mm": round(p24, 1),
                             "max_daily_mm": round(float(rc.precipitation_mm.max()), 1), "temperature_cell": tcell,
                             "summer_tmax_c": round(float(summer), 2), "source_ids": "IMD_RF_0P5;IMD_T_1P0"})

    # City-level cross-check from the long daily series (not a zone input).
    dy = daily.dropna(subset=["rain_mm"])
    climate_rows.append({"zone_id": "CITY_XCHECK", "rainfall_cell": "DAILY_WEATHER_CSV", "years": f"{dy.date.dt.year.min()}-{dy.date.dt.year.max()}",
                         "mean_annual_rain_mm": round(float(dy.groupby(dy.date.dt.year).rain_mm.sum().iloc[1:-1].mean()), 1),
                         "p10_annual_rain_mm": None, "p90_annual_rain_mm": None,
                         "mean_annual_max_daily_mm": round(float(dy.groupby(dy.date.dt.year).rain_mm.max().iloc[1:-1].mean()), 1),
                         "max_daily_mm": round(float(dy.rain_mm.max()), 1), "temperature_cell": "DAILY_WEATHER_CSV",
                         "summer_tmax_c": round(float(daily[daily.date.dt.month.isin([3, 4, 5])].tmax_c.mean()), 2),
                         "source_ids": "DAILY_WEATHER_CSV"})

    zones_model = pd.DataFrame(zone_rows)
    zones_flat = pd.DataFrame(flat_rows)
    rain_out = rain[rain.grid_id.isin(rain_keep)].dropna(subset=["precipitation_mm"]).copy()
    rain_out["date"] = rain_out["date"].dt.strftime("%Y-%m-%d")
    rain_out["unit"] = "mm/day"
    rain_out["evidence"] = Evidence.OBSERVED.value
    rain_out["source_id"] = "IMD_RF_0P5"
    sites_out = pd.DataFrame(sites.drop(columns="geometry"))
    sites_out = sites_out[["site_id", "point_class", "Name", "lon", "lat", "coord_valid", "duplicate_of", "ward_key", "ward_name",
                           "zone_name", "legacy_ward_name", "legacy_ward_no", "legacy_zone", "usable_for_counts", "status", "source_file"]]
    sites_out = sites_out.rename(columns={"Name": "name", "zone_name": "gba_zone_name"})
    sites_out["source_id"] = "BLR_FLOOD_POINTS"
    sites_out["pilot_zone_id"] = sites_out["ward_key"].map(dict(zip(zones_flat.ward_key, zones_flat.zone_id)))
    wards_out = pd.DataFrame(w.drop(columns="geometry"))
    wards_out = wards_out[["ward_key", "ward_name", "Corporation", "zone_name", "TOT_P", "pop_flag", "pop_sum_mismatch", "sc_st_share",
                           "area_m2", "centroid_lat", "centroid_lon", "building_count", "footprint_m2", "built_fraction", "flood_points",
                           "drain_length_m", "drain_density", "waterbody_count", "waterbody_area_m2"]
                          + [c for c in w.columns if str(c).startswith(("gw_share_", "drain_swd_"))]]
    scen = pd.read_csv(Settings.load().config_dir / "scenarios.csv")
    interventions = pd.read_csv(Settings.load().config_dir / "intervention_assumptions.csv")

    prov_rows = []
    for sid, (name, path, period, res, ev, lic) in SOURCES.items():
        p = raw / path if not path.startswith("config") else Settings.load().root / path
        prov_rows.append({"source_id": sid, "dataset_name": name, "path": path, "observation_period": period, "spatial_resolution": res,
                          "evidence_class": ev, "licence": lic, "crs": "EPSG:4326 (processed in EPSG:32643)" if not path.startswith("config") else "-",
                          "sha256": sha256(p) if p.is_file() else "", "present": p.exists()})
    prov = pd.DataFrame(prov_rows)

    files = {
        "zones_model_inputs.csv": zones_model, "zones.csv": zones_flat, "rainfall_daily.csv": rain_out[["date", "grid_id", "lon", "lat", "precipitation_mm", "unit", "evidence", "source_id"]],
        "sites.csv": sites_out, "wards_summary.csv": wards_out, "provenance.csv": prov, "climate_summary.csv": pd.DataFrame(climate_rows),
        "interventions.csv": interventions, "scenarios.csv": scen, "inventory.csv": inv,
    }
    for name, df in files.items():
        df.to_csv(out / name, index=False)
    (out / "zones.geojson").write_text(json.dumps({"type": "FeatureCollection", "name": f"C1V1C pilot zones {version}",
                                                   "crs_note": "EPSG:4326", "features": feats}), encoding="utf-8")
    quality = {"generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "checks": report.checks,
               "quarantined": report.quarantined, "gaps": report.gaps, "pilot_selection_rule": rule}
    (out / "data_quality_report.json").write_text(json.dumps(quality, indent=1, default=str), encoding="utf-8")
    manifest_files = ["zones_model_inputs.csv", "zones.csv", "rainfall_daily.csv", "sites.csv", "wards_summary.csv", "provenance.csv",
                      "climate_summary.csv", "interventions.csv", "scenarios.csv", "zones.geojson", "data_quality_report.json"]
    manifest = {
        "baseline_version": version, "data_mode": DataMode.MIXED_PILOT.value,
        "data_mode_reason": "Zone geometry, population, footprints, hazard markers and IMD climate are observed/derived; "
                            "intervention costs, effects and eligibility fractions are declared assumptions.",
        "geography": "Bengaluru GBA 369-ward boundary; three Yelahanka-zone pilot wards", "coordinate_reference_system": "EPSG:4326",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "pilot_selection_rule": rule,
        "known_gaps": report.gaps, "files": {f: sha256(out / f) for f in manifest_files},
        "raw_inputs": {sid: row["sha256"] for sid, row in prov.set_index("source_id").iterrows() if row["sha256"]},
    }
    (out / "baseline_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> None:
    s = Settings.load()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", type=Path, default=s.raw_dir)
    ap.add_argument("--out", type=Path, default=s.curated_dir / s.baseline_version)
    ap.add_argument("--version", default=s.baseline_version)
    a = ap.parse_args(argv)
    if not (a.raw / WARDS).exists():
        raise SystemExit(f"raw dataset not found under {a.raw}; run scripts/data/fetch_drive_dataset.py first")
    m = build(a.raw, a.out, a.version)
    print(json.dumps({"baseline_version": m["baseline_version"], "out": str(a.out), "files": len(m["files"]),
                      "gaps": m["known_gaps"]}, indent=1))


if __name__ == "__main__":
    main()
