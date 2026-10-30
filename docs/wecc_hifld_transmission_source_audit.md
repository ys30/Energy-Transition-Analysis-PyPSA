# Real-grid transmission evidence: initial source audit (2026-10-30)

## Public sources checked

1. **WECC Anchor Data Set (ADS)** — https://www.wecc.org/program-areas/reliability-planning-performance-analysis/reliability-modeling/anchor-data-set-ads

   WECC describes ADS as planning data containing **load, resource, and transmission topology** compatible with production-cost and power-flow models. The official page distinguishes **public data** from **NDA-confidential** datasets. This is the preferred candidate for a genuine Western Interconnection model subject to separate licensing, download, vintage, BA-to-bus mapping, and branch-parameter checks. **No physical CISO–BPAT branch ratings, impedance values, or complete 2024 topology were verified from the page in this audit.** The listed ADS vintages include planning years beyond the historical 2024 comparison, so do not silently label a planning case as 2024 historical grid truth.

2. **HIFLD open US transmission-lines GIS** — https://hifld.publicenvirodata.org/collections/hifld/datasets/transmission-lines-1 and https://services2.arcgis.com/LYMgRMwHfrWWEg3s/arcgis/rest/services/HIFLD_US_Electric_Power_Transmission_Lines/FeatureServer/0

   HIFLD covers geospatial line segments and reported line attributes; it is useful for geographic topology screening, not an audited network-equivalent AC load-flow case. Line geometry or nominal voltage **alone does not establish** an operating thermal MW/MVA rating, resistance/reactance in ohms, BA electrical endpoint aggregation, security limits, or temporal historical validity.

## Admission criteria before a calibrated PyPSA Line study

- Document the data edition, public redistribution terms, source archive URL, raw-file hashes, and historical/planning year.
- Verify each electrical bus, voltage base, electrical connectivity, AC resistance/reactance (ohms or rigorously converted from p.u. with a documented common base), branch thermal MVA ratings, and endpoints.
- Distinguish power-flow branch limits (typically MVA) from simple DC-model MW screening approximations; quantify this modeling approximation.
- Match generation and demand to independently supported 2024 BA-to-bus crosswalks; do not infer network thermal ratings from EIA-930 observed interchange.
- Reject incomplete or inconsistent inputs; do not set `evidence_status=independently_verified` merely because a URL is present.
- Check observed cross-border flows, transmission losses, congestion, security constraints, and coverage before making any empirical performance claim.

## Status and next milestone

**Discovery-only; real physical branch inputs not yet ingested or certified.** The existing `transmission_evidence_gate.py` and `pypsa_line_evidence_adapter.py` enforce elementary structural and value checks, not full provenance authentication. Synthetic two-bus optimization is separately verified in [the AC Line sensitivity record](verified_synthetic_ac_line_sweep.md); its numbers are fictional test fixtures. The next material milestone is *download a license-compatible WECC public case, inspect its actual branch fields and base definitions, then run a physically meaningful and clearly labeled scenario*.
