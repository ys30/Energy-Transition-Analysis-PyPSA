# Project A verification checkpoint — 2026-10-31

## CI evidence and scope

GitHub Actions UI screenshot supplied in the project conversation shows successful **CI #809, #810, #811** on the main branch. These are evidence that the repository CI workflow completed successfully for those commits, **not** evidence that a real Western-US multi-year dispatch or calibrated network was solved.

- CI #811: `6a694e6` — upstream LAF aggregation, conservation, missing-region and NaN rejection tests.
- CI #810: `a2e04fe` — source-derived PyPSA-USA `LAF_state` state-to-zone share extraction.
- CI #809: `ccd39e0` — CSV fixture newline correction.
- CI #808 failed before the correction; it is superseded by the later green runs.

The current branch may contain commits newer than #811; **their CI outcomes must be checked separately**.

## Verified engineering boundary

1. Source-derived zone allocation and missing-zone fail-closed gates exist in code and tests.
2. Full-year zonal demand to PyPSA Network/NetCDF ingestion and round-trip assertions exist in code and tests.
3. Synthetic three-zone HiGHS dispatch audit and JSON reporting exist; **synthetic only**.
4. Historical CISO/BPAT EIA-930 quality gates and BPAT wind source-population discrepancy remain unresolved as documented in README.

## Still required before empirical claims

- Obtain an externally sourced, reproducibly versioned Western zonal network NetCDF with documented Bus/Link mapping and ratings; do not treat raw LAF bundles as an already built network.
- Run and archive full-year network ingestion and multi-year dispatch artifacts for each modeled year, with explicit source manifests and complete bus coverage.
- Audit per-zone demand, energy balance, transfer constraints, generator availability and solver status.
- Benchmark model dispatch against observed EIA-930 quantities, explicitly reporting missing data and any failed calibration eligibility gates.
- Do not report storage benefits, congestion reductions, emissions or policy impacts as historical results until the corresponding network and calibration gates pass.

## Reproducibility policy

Each milestone must include commit SHA, CI run URL, input provenance, test/solver status and a downloadable machine-readable audit artifact. Missing CI run IDs are recorded as **unverified**, never inferred as passing.
