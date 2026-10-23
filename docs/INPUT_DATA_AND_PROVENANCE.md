# Input readiness, provenance and valid claims

This is the **data-handoff contract**, not a claim that city datasets have already been downloaded or checked. The synthetic fixtures live under `data/synthetic_test/` and MUST NEVER be presented as measured Bengaluru or Yelahanka facts.

## Data modes
1. **Synthetic demonstration:** all indicators/coefficients are test fixtures and marked `synthetic` with evidence grade D.
2. **Mixed-evidence pilot:** some real spatial/meteorological inputs, others cited estimates/assumptions; labels and sources visible *per metric*.
3. **Observed-data pilot:** use only for values whose actual source, location, date and measurement/model status have been verified. Note that remotely modelled population estimates are not direct census measurements.

## Required record fields
`record_id`, `zone_id` or `site_id`, `metric`, `value`, `unit`, `spatial_scope`, `spatial_resolution`, `observation_date`, `source_id`, `source_url`, `method`, `evidence_class`, `known_limitations`, `baseline_version`, `data_quality_status`.

Allowed evidence classes: A = measured local; B = credible published/modelled spatial data; C = literature transfer with applicability caveats; D = synthetic or illustrative assumption. These are qualitative grades, NOT calibrated confidence probabilities.

## Frozen data input process (member 3)
1. Identify consistent pilot geometry and coordinate reference system; use a single reference horizon.
2. Obtain/publicly verify rainfall, land cover, population and eligible roof/green areas using sources in `data/source_registry.csv`; verify source restrictions and spatial resolution.
3. Confirm capacity, water demand, costs and effects individually or mark them as assumptions; never substitute absent values with zero.
4. Produce `zones.csv`, `sites.csv`, `interventions.csv`, `provenance.csv`, `scenarios.csv` under `data/curated/` with source IDs. Their empty schemas are in `data/templates/`.
5. Validate identifiers, positivity/bounds, local scope, joined keys, dated source layers, uncertainties and overlap.
6. Freeze SHA256 checksums and version into `baseline_manifest.json`; save it with every immutable run.

## Granularity safeguards
- Yelahanka sub-catchment research does NOT automatically supply three official zone polygons.
- CHIRPS / NASA POWER grid resolution does NOT justify block-level rainfall claims.
- Rooftop footprints do NOT demonstrate rooftop structure/support eligibility.
- Runoff peaks, drainage exceedance, flood hazard/exposure and measured flood *depth* are distinct.
- A climate scenario multiplier is a stress test, not a climate forecast.
- Carbon factors require boundary + time horizon; absent factor -> `not estimated`, never invented zero.

## Baseline fallback
If the verified local geography/data aren't ready, retain the synthetic mode, with prominent banners in the app and exported reports. Code and tests may be complete in synthetic mode; claims about real Bengaluru environmental outcomes must remain blocked.
