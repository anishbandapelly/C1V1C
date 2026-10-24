"""Frozen, versioned baseline snapshot loaded from the curated pipeline outputs."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from c1v1c.config import Settings
from c1v1c.evidence import DataMode, Evidence, Quantity
from c1v1c.schemas import ZoneBaseline

ZONE_QUANTITIES = (
    "area_ha", "population", "sc_st_share", "built_fraction", "impervious_fraction", "vegetation_fraction",
    "runoff_coefficient", "eligible_roof_m2", "plantable_land_m2", "design_p24_mm", "design_event_mm",
    "design_event_runoff_m3", "summer_tmax_c", "heat_index", "vulnerability_weight", "flood_points",
    "drain_length_m", "waterbody_features",
)


class BaselineUnavailable(RuntimeError):
    """Raised when curated inputs are missing or fail integrity checks."""


@dataclass(frozen=True)
class RainSeries:
    cell: str
    dates: np.ndarray
    years: np.ndarray
    rain_mm: np.ndarray
    evidence: Evidence
    source_id: str


@dataclass(frozen=True)
class Baseline:
    version: str
    sha256: str
    data_mode: DataMode
    zones: tuple[ZoneBaseline, ...]
    rain: dict[str, RainSeries]
    manifest: dict
    geojson: dict
    sites: pd.DataFrame
    provenance: pd.DataFrame
    quality: dict
    climate_summary: pd.DataFrame

    def zone(self, zone_id: str) -> ZoneBaseline:
        for z in self.zones:
            if z.zone_id == zone_id:
                return z
        raise KeyError(zone_id)


def _quantity(row: dict, key: str) -> Quantity:
    payload = json.loads(row[key])
    return Quantity(**payload)


def _hash_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for p in sorted(paths):
        digest.update(p.name.encode())
        digest.update(hashlib.sha256(p.read_bytes()).hexdigest().encode())
    return digest.hexdigest()


def load_baseline(directory: Path | None = None) -> Baseline:
    settings = Settings.load()
    base = Path(directory) if directory else settings.curated_dir / settings.baseline_version
    return _load(str(base))


@lru_cache(maxsize=4)
def _load(base_str: str) -> Baseline:
    base = Path(base_str)
    manifest_path = base / "baseline_manifest.json"
    if not manifest_path.exists():
        raise BaselineUnavailable(f"curated baseline not found at {base}; run `python -m c1v1c.pipeline` first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = [base / name for name in manifest["files"]]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise BaselineUnavailable(f"baseline files missing: {missing}")
    for f in files:
        if hashlib.sha256(f.read_bytes()).hexdigest() != manifest["files"][f.name]:
            raise BaselineUnavailable(f"checksum mismatch for {f.name}; baseline has been modified")
    zones_df = pd.read_csv(base / "zones_model_inputs.csv", dtype=str)
    zones = []
    for row in zones_df.to_dict("records"):
        zones.append(ZoneBaseline(
            zone_id=row["zone_id"], name=row["zone_name"], ward_keys=tuple(row["ward_keys"].split(";")),
            gba_corporation=row["gba_corporation"], gba_zone_name=row["gba_zone_name"],
            centroid_lat=float(row["centroid_lat"]), centroid_lon=float(row["centroid_lon"]),
            rainfall_cell=row["rainfall_cell"], selection_reason=row["selection_reason"],
            **{k: _quantity(row, k) for k in ZONE_QUANTITIES},
        ))
    rain_df = pd.read_csv(base / "rainfall_daily.csv", parse_dates=["date"])
    rain = {}
    for cell, g in rain_df.groupby("grid_id"):
        g = g.sort_values("date")
        rain[cell] = RainSeries(cell, g["date"].to_numpy(), g["date"].dt.year.to_numpy(), g["precipitation_mm"].to_numpy(float),
                                Evidence(g["evidence"].iloc[0]), g["source_id"].iloc[0])
    return Baseline(
        version=manifest["baseline_version"],
        sha256=_hash_files(files),
        data_mode=DataMode(manifest["data_mode"]),
        zones=tuple(zones),
        rain=rain,
        manifest=manifest,
        geojson=json.loads((base / "zones.geojson").read_text(encoding="utf-8")),
        sites=pd.read_csv(base / "sites.csv"),
        provenance=pd.read_csv(base / "provenance.csv"),
        quality=json.loads((base / "data_quality_report.json").read_text(encoding="utf-8")),
        climate_summary=pd.read_csv(base / "climate_summary.csv"),
    )
