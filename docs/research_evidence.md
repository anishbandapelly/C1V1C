# Research-to-implementation evidence register

> The entries below are transcribed/summarised from the supplied master plan. They describe **methodological inspiration and limitations**, not validated Bengaluru coefficient values. Full papers are not redistributed into a potentially public GitHub repository.

## Source register (from Appendix C)

- [PS]  Sustainable_Development(2).docx. “The Sustainability Paradox: Optimising a City That Cannot Afford to Grow Greener.” Original hackathon problem statement and MVP/AWS/expected-outcome tables.
- [BP]  Urban Sustainability / Code-Level Blueprint (23 October 2026), 19 pages. Supplied architecture proposal; especially data contracts, immutable runs, evidence gaps, and AWS/CKAN trade-offs.
- [R1]  Jamwal, P. et al. (2024). Building Resilience to Urban Floods: Strategy and Action Plan for Bengaluru. ATREE. ISBN 978-81-940887-9-0.
- [R2]  Leng, L., Jia, H., Chen, A. S., Zhu, D. Z., Xu, T., & Yu, S. (2021). Multi-objective optimization for green-grey infrastructures in response to external uncertainties. Science of the Total Environment, 775, 145831.
- [R3]  Manivasagam, V. S., Saai Shreyaa, G. V., & Ganesh, S. D. (2025). Food-energy-water sustainability in urban spaces: insights from open geospatial datasets in Coimbatore, India. Computational Urban Science, 5:54. DOI: 10.1007/s43762-025-00213-w.
- [R4]  Gobatti, L., Bach, P. M., Maurer, M., & Leitão, J. P. (2025). Impact of soil moisture content on urban tree evaporative cooling and human thermal comfort. npj Urban Sustainability, 5:26. DOI: 10.1038/s42949-025-00220-0.
- [R5]  Nathawat, R. et al. (2025). Urban Green Infrastructure Planning in Jaipur, India: A GIS-Based Suitability Model for Semi-Arid Cities. Sustainability, 17, 2420. DOI: 10.3390/su17062420.
- [R6]  Pan, H. et al. (2023). Contribution of prioritized urban nature-based solutions allocation to carbon neutrality. Nature Climate Change, 13, 862–870. DOI: 10.1038/s41558-023-01737-x.
- [R7]  Kuznetsov, I. et al. (2025). Transforming climate services with LLMs and multi-source data integration. npj Climate Action, 4:97. DOI: 10.1038/s44168-025-00300-y.
- [R8]  Dorner, J., Scherner, M., Thaler, T., & Friesenecker, M. (2026). Taming the green gentrification cycle? Evidence from street greening in Vienna. Urban Geography. DOI: 10.1080/02723638.2026.2656265.
- [R9]  Caparros-Midwood, D., Barr, S., & Dawson, R. (2017). Spatial Optimization of Future Urban Development with Regards to Climate Risk and Sustainability Objectives. Risk Analysis, 37(11). DOI: 10.1111/risa.12777.
- [R10]  Castro, C. V. (2022). Optimizing nature-based solutions by combining social equity, hydro-environmental efficiency, and economic costs through a novel Gini coefficient. Earth and Space Science Open Archive preprint. DOI: 10.1002/essoar.10508767.1.

## Implementation traceability (from master-plan table)

| Reference | Exact contribution to project | Do not overclaim |
| --- | --- | --- |
| [PS] | Mandatory scope, interventions, scenarios, AWS service suggestions and expected decision outcomes. | Does not supply specific data, methods or validated coefficients. |
| [BP] | Typed contracts, data gaps, score breakdown, immutable run IDs, clear service boundaries. | Its toy additive simulator and CKAN/EKS architecture are not required for this MVP. |
| [R1] ATREE Bengaluru | Catchment framing; flood hazard/exposure/vulnerability distinction; local study context. | Its calibrated HEC-HMS/HEC-RAS findings are not automatically reproduced by our screening model. |
| [R2] Leng et al. | Joint green–grey optimisation and explicit uncertain climate conditions. | Its outcomes or model parameters are not transplanted to Bengaluru. |
| [R3] Manivasagam et al. | Building-footprint-based rooftop assessment and water feasibility workflow. | Rooftop footprints do not prove structural eligibility. |
| [R4] Gobatti et al. | Soil moisture and urban form affect tree cooling; drought reduces certainty. | Zurich cooling magnitudes cannot be used as Bengaluru observations. |
| [R5] Nathawat et al. | Suitability logic using land cover, temperature, moisture, slope and rainfall. | Jaipur-specific weights/results are not Bengaluru coefficients. |
| [R6] Pan et al. | Direct and indirect carbon pathways, resource-saving interactions and spatial priorities. | EU carbon reduction percentages are not a local factor. |
| [R7] Kuznetsov et al. | Ground language explanations in numerical climate data and literature. | LLM explanations do not validate physical predictions. |
| [R8] Dorner et al. | Social side-effects must be contextual, not assumed universally. | Greening does not imply demonstrable gentrification in our zones. |
| [R9] Caparros-Midwood | Non-dominated options and trade-offs in spatial planning. | Only sampled solutions are claimed unless a complete Pareto frontier is computed. |
| [R10] Castro | Equity in the allocation objective rather than only downstream displays. | Equity weights and vulnerability data remain policy/data assumptions. |

## Coefficient validity rule

Do not populate `effect_factors.csv` from a paper's context-specific percentage unless the site, unit, outcome, timescale and source assumptions are comparable and explicitly documented. If not, use a clearly labelled synthetic fixture **only for software testing**, and mark production estimates unvalidated.

## Source IDs

Use `[PS]` for official requirement, `[BP]` for supplied AWS/CKAN blueprint, and `[R1]`–`[R10]` for selected papers as above. Every claimed measured indicator or literature-derived parameter must point to a precise source and date.
