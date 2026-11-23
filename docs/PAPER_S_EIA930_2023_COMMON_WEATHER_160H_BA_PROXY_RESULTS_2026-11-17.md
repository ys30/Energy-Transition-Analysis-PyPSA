# Paper S — 2023 same-weather EIA-930 160-hour BA-to-state PROXY curve diagnostics (verified)

Date: 2026-11-17. **GitHub Actions run [44217749289](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44217749289) completed SUCCESS**, with independently downloaded source HDF5/CSV MD5 validation, source EIA-930 CSV SHA-256 check, clock and 160-hour completeness tests, and metric/row-count admission gates. Artifact **14390743586** (`paper-s-2023-eia930-ipco-psco-sameweather-160h-proxy-shapes`) contains **24 metric rows** and **3,840 hour-level pairing rows** and a fail-closed source manifest.

**What this does NOT establish:** Neither IPCO nor PSCO equals its nominal target state, and the 2025 EIA county operating fleet weights are *not* a reconstructed 2023 operating-generator capacity series. The original ReEDS source instantaneous weather CF, converted by an explicitly assumed trapezoid point-to-hour rule, is not certified as an observed hour-integrated state MWh. The EIA-930 BA observation is metered **net MW**, with different scheduling/asset coverage from modeled state potential. Independently scaling each 160-hour trace by its *own* positive 95th percentile removes an external capacity denominator but does not resolve geography, generator membership, negative generation, or source integration limitations. This analysis is a **descriptive co-weather curve-shape proxy diagnostic**, not validated predictive skill or independent proof that either siting set is physically correct.

## Zero-clock-offset source comparison

160 common UTC hour-ending records: 2023-07-01T08:00:00Z through 2023-07-07T23:00:00Z (inclusive). Both model source weather and observed BA generation use source calendar year **2023**; 2012 is the model's source reference *hour support*, not the 2023 model weather. Values are observed net MW separately scaled to positive-p95 and model CF separately scaled to positive-p95.

| BA proxy | Fuel | Pearson r ReEDS potential | Pearson r 2025 EIA weights | Δ r EIA−potential | normalized RMSE potential | normalized RMSE EIA |
|---|---|---:|---:|---:|---:|---:|
| IPCO↔Idaho | wind | 0.866509 | 0.849204 | −0.017305 | 0.158442 | 0.176253 |
| IPCO↔Idaho | solar | 0.978430 | 0.985578 | +0.007148 | 0.100706 | 0.090784 |
| PSCO↔Colorado | wind | 0.726955 | 0.804905 | +0.077950 | 0.215772 | 0.189273 |
| PSCO↔Colorado | solar | 0.950543 | 0.959938 | +0.009395 | 0.130324 | 0.120450 |

At **zero prespecified shift**, EIA county weighting has closer sample curve shape for PSCO wind, PSCO solar, and IPCO solar, but *worse* agreement for IPCO wind. In PSCO solar, the source observation includes **42/160 negative reported net-MW hours**, retained without clipping.

## Prespecified clock sensitivity (not tuning)

Three source-hour offsets −1, 0, +1 h were evaluated *without selecting the offset maximizing agreement*. Across these offsets:
- PSCO wind Δ Pearson r (EIA minus potential) = **+0.057594 to +0.081321**: EIA advantage across all three.
- PSCO solar = **+0.001786 to +0.009395**: EIA advantage across all three.
- IPCO wind = **−0.028343 to −0.017305**: ReEDS potential advantage across all three.
- IPCO solar = **−0.012871 to +0.024864**: mixed sign, hence **clock-sensitive**.

These sensitivity results do not certify an actual physical UTC/hour-ending alignment: the CFs are not hour-integrated publisher measurements.

## Manuscript admission limits

This result may enter SI as an exploratory **2023 160-hour BA-to-state proxy** check, with one explicit table and raw series. It must **not** be relabeled model validation, full-year 2019–2023 skill, ex post 2023 county placement, calibrated capacity factors, or evidence that the observed county weights correctly represent BA fleets. Main text should state the contrast qualitatively and retain mechanism/robustness results of the 2×2 and 3×3 LP experiments as the primary contribution.

For actual external validation, separately reconcile 2023 generator IDs to actual 2023 operating counties, BA-specific reporting and Schedule 4 pseudo-tie footprints, duplicate CW1 (plant 59975; 150 MW), capacity basis, source point sampling, and full-year hourly completeness. A full-year first pass can use shape metrics but must not assume BA=state; compare year-by-year over common source weather 2019–2023 once audited.

## Pinned provenance

- New run: [44217749289](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/44217749289), artifact **14390743586**.
- Source observed July 2023 EIA930: original run 43682969646, artifact 14150700990; source SHA-256 `0e72513a99c920391c0fc51a1691e84780ca5da81ba0c34b2fe218ed3fbc2f5a`.
- Code: `src/energy_transition/paper_s_eia930_2023_samework_weather_shape_proxy.py`, tests: `tests/test_paper_s_eia930_2023_samework_weather_shape_proxy.py`.
- Artifact files: `paper_s_2023_july_eia930_160h_BA_state_PROXY_shape_metrics.csv`, `paper_s_2023_july_eia930_160h_BA_state_PROXY_hour_pairs.csv`, `paper_s_2023_july_proxy_comparison_manifest.json`.
- Figures E1–E3, extra 12-pair comparative CSV, and rendered Word/PDF research addendum are available in the conversation as an independent **review bundle**, **not** a GitHub binary release.
- Original 1440 LP, 2160 ATB, 360 2×2 new LP, 2880 3×3 new LP, and Paper C-2 were not modified.
