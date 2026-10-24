# Data pipeline, data quality and pilot zones

**Code:** [`src/c1v1c/pipeline.py`](../src/c1v1c/pipeline.py) · **fetch:** [`scripts/data/fetch_drive_dataset.py`](../scripts/data/fetch_drive_dataset.py) · **outputs:** `data/curated/bengaluru_pilot_v1/` (git-ignored, rebuilt reproducibly)

```bash
python -I scripts/data/fetch_drive_dataset.py      # lists all 5,765 Drive files, downloads the 165 the pilot uses
python -m c1v1c.pipeline                           # raw -> curated baseline (~25 s), writes data_quality_report.json
```

Rebuilding from the same raw files gives byte-identical zone, rainfall, site and geometry outputs; this is tested in `tests/test_pipeline.py::test_pipeline_is_reproducible`.

## 1. Collection inventory (what actually exists)

The shared Drive folder lists **5,765 files (~7.5 GB)**. The fetch keeps the full listing in `data/raw/drive_listing.json` and downloads **165 files**:

- every boundary, hazard, drainage, waterbody, footprint, population, water-supply, soil and catalogue file;
- the 9 IMD 0.5° rainfall cells and the 1° temperature/rainfall cells around Bengaluru;
- the Bengaluru SRTM tile.

It does not download all-India IMD cells, other SRTM tiles, duplicate archives, or the 1.9 GB global HWSD raster.

| Claimed in the brief / inventory | Present? | Used for |
|---|---|---|
| GBA 369-ward boundaries + population attributes | Yes (Dec 2025 KML) | zone geometry, population, SC/ST share |
| IMD rainfall **NetCDF 2015–2025** | **No** — no `.nc` file anywhere | — (gap reported) |
| Daily rain + Tmax/Tmin 1951–2024 | Yes (`DOC-20261023-WA0007.csv`, station undocumented) | independent cross-check only |
| IMD 0.5° rainfall text grids | Yes (1971–2005) | zone rainfall, design storm, tank simulation |
| IMD 1° temperature grids | Yes (1969–2005) | summer Tmax for the heat index |
| **2017 land-use KML/KMZ** | **No** (only global GIAM/WaterBase rasters) | — (gap reported) |
| Lakes, tanks, ponds | Yes (`blr_tanks` 1,356 polygons, `blr_ponds` 6,570) | water-storage proxy |
| ~399 flood / low-lying points | Yes (3 KMLs, 399 points) | hazard markers per ward |
| Groundwater potential | Yes, but urban wards are 100% "Habitation Mask" | not discriminating; recorded only |
| Microsoft building footprints | Yes (597,376 polygons) | built fraction, roof-area upper bound |
| Storm-water drains | Yes (primary, secondary, tertiary + a merged duplicate) | drain length per ward |
| Urban heat CSV | Yes, but every row is near 11.0°N 76.9°E (outside Bengaluru) | rejected |
| Soil (HWSD, FAO WaterBase) | Global rasters | reference only (no local infiltration coefficient) |

`curated/source_inventory.csv` claims 5,745 paths. Three of these are not in the shared folder: `India.shp`, `HWSD_RASTER.zip` and `DEM_SRTM.7z`. They are treated as catalogue claims, not data.

**Personal information:** CSV headers are scanned for personal-data fields, and none were found. PDFs, population web-page prints and XLS reports are kept as references and are not ingested.

## 2. Mandatory data-quality corrections

| # | Issue | Resolution (evidence in `data_quality_report.json`) |
|---|---|---|
| 1 | `curated/rainfall.csv`: 51,136 rows all dated 1971-01-01 | Each IMD SWAT text grid begins with its start date (`19710101`), followed by one value per consecutive day. The 12,784 values per cell end exactly on 2005-12-31. The curated file's values match the raw files **value for value, in order** for all 4 cells. Dates are therefore reconstructed from the source header, not invented. The broken file is **quarantined** and replaced by `rainfall_daily.csv`. |
| 2 | Population total ≠ male + female in 125 wards (max \|diff\| 3,896) | Source values are preserved and `TOT_P` is used as the published total. Each ward is flagged `consistent` / `minor_mismatch` (≤50) / `major_mismatch`. Major-mismatch wards are excluded from pilot selection. Reference year is not stated in the source (delimitation figures). |
| 3 | Invalid and duplicate flood coordinates | `low_lying-83` at (0, 0) is excluded. Six duplicate-coordinate groups (seven redundant rows) are flagged `duplicate_of` and excluded from counts. The 396 valid points are joined to current wards; 2 fall outside all wards. |
| 4 | 2017 land use as present-day | The 2017 layer is absent, so no land-use class is presented as current. Vegetation and non-building imperviousness are declared **assumptions**. |
| 5 | Legacy vs current ward identifiers | `ward_id` repeats across the 5 GBA corporations (257 repeats). The composite key `GBA-C{corporation}-W{ward}` is unique. Flood points' `WARDNO`/`ZONE` are legacy BBMP 198-ward ids, kept as `legacy_*` fields and never used as keys. |
| 6 | Flood points as construction sites | Every point has `status = hazard_marker_not_construction_site`. Candidates are planning units, not surveyed sites. |
| 7 | Inventory entries assumed present | Compared against bytes on disk and the Drive listing (see §1). |
| 8 | Coverage, resolution, units, dates, CRS, licence, provenance | Recorded per source in `provenance.csv`. All processing uses EPSG:32643 (UTM 43N) for areas and lengths. |
| 9 | Personal or unrelated files | Header scan (none found). Documents are not ingested. |

The pipeline also found and handled these:

- Eight invalid ward polygons, repaired topologically.
- One drainage KML that is a byte-identical duplicate.
- A "merged" drainage layer equal to primary + secondary + tertiary (328.5 + 438.8 + 1,219 ≈ 1,988.5 km), excluded to avoid double counting.
- Four malformed tertiary-drain geometries, dropped and counted.
- Three "waterbody" KMLs that are copies of the flood-point files, reclassified.

## 3. The three pilot zones

**Rule (reproducible):** start from the 31 wards in GBA zone *Yelahanka*, which is the master plan's Yelahanka sub-catchment context. Remove wards with major population inconsistencies, leaving 30. Then pick one ward per distinct dominant stress:

| Zone | Ward (composite key) | Profile and selection metric | Area | Population | SC/ST share | Built fraction | Hazard markers | Drains | Design-event runoff |
|---|---|---|---|---|---|---|---|---|---|
| **ZA** | Brundavana Nagara (`GBA-C2-W062`) | Rain: highest density of validated flood/low-lying markers (5.96 per km²) | 67.1 ha | 28,749 | 7.3% | 0.494 | 4 | 3.74 km | 10,943 m³ |
| **ZB** | Dinnur (`GBA-C2-W050`) | Heat: highest building-footprint fraction (0.499) | 50.9 ha | 27,395 | 7.5% | 0.499 | 1 | 1.32 km | 8,328 m³ |
| **ZC** | R.T Nagar (`GBA-C2-W053`) | Water: no tanks or ponds; tie broken by largest population | 62.8 ha | 29,905 | 3.6% | 0.493 | 2 | 0.82 km | 10,233 m³ |

**Shared climate (honest coarseness):** all three wards fall in the same IMD 0.5° rainfall cell (X775Y130) and the same 1° temperature cell. They therefore share these values:

- mean annual rainfall: 902 mm (1971–2005);
- mean annual-maximum daily rainfall: 72.0 mm;
- 1-hour design depth: 24.95 mm (IMD reduction formula);
- Mar–May mean Tmax: 34.4 °C.

Climate does not differentiate the wards; geometry, buildings, hazards and population do.

**Opportunities and limitations:**

- **ZA** has the most hazard markers and drain length, so it is the natural place to test retention and conveyance. Downstream effects are unknown.
- **ZB** is the densest; roof-based measures (green roofs, tanks) compete for the same roofs.
- **ZC** has no mapped surface storage and the lowest SC/ST share, so the equity weight is lowest there.
- All three wards are similar (built fraction ≈ 0.49), so differences in results are modest by construction. The source attribute assigns Brundavana Nagara to assembly constituency "154 – Rajarajeshwarinagar"; this looks inconsistent with its Yelahanka zone and is reported, not altered.

## 4. Curated outputs (data dictionary)

| File | Rows | Key | Contents (units) |
|---|---|---|---|
| `zones.geojson` | 3 | `zone_id` | ward polygons (EPSG:4326, simplified to ~2 m) |
| `zones.csv` | 3 | `zone_id` | flat zone table: ha, persons, fractions, counts, m, mm/day, mm in 1 h, °C, selection rule, `source_ids` |
| `zones_model_inputs.csv` | 3 | `zone_id` | each indicator as a JSON `Quantity` {value, unit, evidence, source_ids, note, low, high, missing_reason} |
| `rainfall_daily.csv` | 12,784 | `date`+`grid_id` | mm/day, observed, `IMD_RF_0P5` |
| `sites.csv` | 398 | `site_id` | hazard markers with validity, duplicate flags, current ward key, legacy ids, pilot zone |
| `wards_summary.csv` | 369 | `ward_key` | city-wide ward indicators (used for selection) |
| `climate_summary.csv` | 4 | `zone_id` | annual rain statistics, Tmax, plus city cross-check |
| `interventions.csv`, `scenarios.csv` | 4 / 4 | id | copies of the declared configuration used |
| `provenance.csv` | 12 | `source_id` | dataset, path, period, resolution, evidence class, licence, sha256 |
| `data_quality_report.json` | — | — | every check, quarantine and gap |
| `baseline_manifest.json` | — | — | version, data mode, sha256 of every file; the engine refuses a modified baseline |

**Evidence classes:**

| Class | Grade | Meaning |
|---|---|---|
| Observed | A | Source values as published |
| Derived | B | Deterministic transforms of observed data |
| Estimated | C | Literature value transferred to Bengaluru |
| Assumed | D | Declared planning assumption |
| Synthetic | — | Tests only |
| Missing | — | `value = null` plus a reason; never zero |

The application's data mode is **mixed-evidence pilot**.

## 5. Licensing note

Microsoft footprints are released under CDLA Permissive 2.0. IMD gridded data and the GBA/KSRSAC layers state no licence in the files. For that reason the curated baseline (which includes a daily IMD series and ward polygons) is **not committed to the public GitHub repository**. It is rebuilt by the pipeline, or copied into the deployment image from a local build. Confirm licences before publishing the curated files.
