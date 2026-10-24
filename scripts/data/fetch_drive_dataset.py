"""Fetch the shared C1V1C Bengaluru dataset folder from Google Drive into data/raw/drive.

The folder holds ~5,700 files (~7.5 GB), mostly all-India IMD grid cells, SRTM tiles
and a global soil raster. This script lists the whole tree (saved to
data/raw/drive_listing.json so the inventory is complete even for skipped bytes) and
downloads only what the Bengaluru pilot pipeline uses:

* every non-IMD, non-terrain, non-soil-raster file under the size cap;
* IMD grid-cell text files whose cell centre lies in the Bengaluru window;
* the single SRTM tile covering Bengaluru (srtm_52_10).

Resumable: files already present with non-zero size are skipped.
Usage: python -I scripts/data/fetch_drive_dataset.py [--all]
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import gdown
import requests

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "raw" / "drive"
LISTING = ROOT / "data" / "raw" / "drive_listing.json"
FOLDER_URL = "https://drive.google.com/drive/folders/1couEReZl1kt9KqVtcH09a5O2JUz4BbE6"

# Bengaluru window (degrees) used to select gridded climate cells.
LAT_RANGE = (12.25, 13.75)
LON_RANGE = (76.75, 78.25)
# Archives whose extracted contents are listed alongside them, and a 1.9 GB global soil raster.
SKIP_PATTERNS = (re.compile(r"hwsd\.bil$", re.I), re.compile(r"DEM_SRTM\.7z$", re.I),
                 re.compile(r"IMD_GRIDED_WEATHER\.7z$", re.I))
SRTM_KEEP = "srtm_52_10"


def imd_cell(path: str) -> tuple[float, float] | None:
    """IMD grids are named X<lon*10>Y<lat*10> (0.5 deg, e.g. X775Y130 = 77.5E, 13.0N)
    or PY|TY<lat*10>X<lon*10> (1 deg rain|temperature, e.g. PY125X775 = 12.5N, 77.5E); .txt and .dbf."""
    m = re.search(r"X(\d{3,4})Y(\d{2,3})\.(?:txt|dbf)$", path)
    if m:
        return int(m.group(1)) / 10, int(m.group(2)) / 10
    m = re.search(r"[PT]Y(\d{2,3})X(\d{3,4})\.(?:txt|dbf)$", path)
    return (int(m.group(2)) / 10, int(m.group(1)) / 10) if m else None


def wanted(path: str) -> bool:
    if any(p.search(path) for p in SKIP_PATTERNS):
        return False
    cell = imd_cell(path)
    if cell is not None:
        lon, lat = cell
        return LON_RANGE[0] <= lon <= LON_RANGE[1] and LAT_RANGE[0] <= lat <= LAT_RANGE[1]
    if "DEM_SRTM" in path and path.lower().endswith((".tif", ".tfw", ".hdr", ".zip")):
        return SRTM_KEEP in path
    return True


def list_folder() -> list:
    for attempt in range(6):
        try:
            return gdown.download_folder(FOLDER_URL, output=str(DEST), skip_download=True, quiet=True)
        except Exception as exc:  # network flakiness while listing
            print(f"listing failed ({exc.__class__.__name__}); retry {attempt + 1}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise SystemExit("could not list the Drive folder")


def download(file_id: str, target: Path) -> None:
    """Stream one Drive file. drive.usercontent with confirm=t bypasses the large-file
    virus-scan interstitial; an HTML response means Drive refused the file."""
    url = "https://drive.usercontent.google.com/download"
    tmp = target.with_name(target.name + ".part")
    with requests.get(url, params={"id": file_id, "export": "download", "confirm": "t"}, stream=True, timeout=60) as r:
        r.raise_for_status()
        if "text/html" in r.headers.get("content-type", ""):
            raise RuntimeError("Drive returned an HTML page instead of file bytes")
        with tmp.open("wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    tmp.replace(target)


def main(argv: list[str]) -> int:
    take_all = "--all" in argv
    DEST.mkdir(parents=True, exist_ok=True)
    if LISTING.exists() and "--relist" not in argv:
        listing = json.loads(LISTING.read_text(encoding="utf-8"))
    else:
        listing = [{"id": f.id, "path": f.path} for f in list_folder()]
    for row in listing:
        row["selected"] = take_all or wanted(row["path"])
    LISTING.write_text(json.dumps(listing, indent=1), encoding="utf-8")
    selected = [r for r in listing if r["selected"]]
    print(f"listed={len(listing)} selected={len(selected)}", flush=True)
    failed = []
    for row in selected:
        target = DEST / Path(row["path"].replace("\\", "/"))
        if target.exists() and target.stat().st_size > 0:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(6):
            try:
                download(row["id"], target)
                print(f"ok {row['path']} {target.stat().st_size}", flush=True)
                break
            except Exception as exc:
                print(f"retry {attempt + 1} {row['path']}: {exc}", flush=True)
                time.sleep(4 * (attempt + 1))
        else:
            failed.append(row["path"])
    print(f"done selected={len(selected)} failed={len(failed)}", flush=True)
    for p in failed:
        print("FAILED", p, flush=True)
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
