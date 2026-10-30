# Project B — reproducible 2024 hourly engineering baseline

## Scope and acceptance

This guide reproduces the **independent, assumption-driven gas-only CISO and BPAT 2024 hourly engineering pilots**, not a calibrated multi-BA interconnected electricity network. For verified same-revision results see [the 2024 numerical acceptance record](verified_2024_two_ba_hourly_numerical_acceptance.md). The underlying official EIA-930 data may be revised. No missing NG hours are filled for the observed-versus-modeled comparison.

## Requirements

Python 3.11 and the repository package with modeling dependencies:

```bash
python -m pip install -e '.[model,dev]'
export EIA_API_KEY='your-own-EIA-API-key'
```

GitHub Actions supplies the configured `EIA_API_KEY` secret. Never commit this key.

## Reproduce CISO 2024

```bash
mkdir -p outputs/hourly_dispatch_pilot
python - <<'PY'
from pathlib import Path
from energy_transition.eia930_west import fetch_eia_demand
from energy_transition.eia930_generation_audit import fetch_net_generation
p=Path("outputs/hourly_dispatch_pilot")
fetch_eia_demand(2024,["CISO"]).to_csv(p/"observed_demand_hourly.csv",index=False)
fetch_net_generation(2024,["CISO"]).to_csv(p/"observed_net_generation_hourly.csv",index=False)
PY
python -m energy_transition.eia930_full_hour_pilot \
  --demand outputs/hourly_dispatch_pilot/observed_demand_hourly.csv \
  --year 2024 --bas CISO --output outputs/hourly_dispatch_pilot
python -m energy_transition.eia930_hourly_model_comparison \
  --observed outputs/hourly_dispatch_pilot/observed_net_generation_hourly.csv \
  --modeled outputs/hourly_dispatch_pilot/modeled_generation_hourly.csv \
  --year 2024 --bas CISO --output outputs/hourly_dispatch_pilot
```

For BPAT, substitute `BPAT` for `CISO` and use `outputs/bpat_hourly`. The respective GitHub Actions workflows include source/output SHA-256 manifests, numerical checks and upload artifacts.

## Evidence and interpretation

- Full 2024 chronological model demand spans **8,784 hourly UTC snapshots** in each BA.
- CISO NG matching in the verified evidence covers 8,760 hours. The **24-hour missing NG interval** is 2024-11-02 08:00 UTC through 2024-11-03 07:00 UTC inclusive. BPAT NG matching covers all 8,784 hours. Do not impute or extrapolate the missing values.
- A gas-plus-synthetic-unserved-load hourly accounting identity is verified. Zero residual in this simplified identity does not validate realistic network dispatch.
- MAE/RMSE compare **assumed gas-only generation** against observed EIA-930 **total BA net generation**; these represent descriptive structural mismatch, **not historical calibration skill**.
- The 288 weighted representative-hour study, EIA-923 technology comparison, hourly storage scenarios, and BPAT wind reconciliation are distinct research tracks and must not be conflated with this pilot.
- GitHub Actions artifacts are time-limited (generally 90 days for these current pilot runs). Archive the input CSVs, output CSVs, NetCDF, SHA-256 manifests, and workflow logs to a durable archival location if they will support a paper.

## Verification checklist

A successful engineer handoff requires: two successful runs sharing one commit SHA; 8,784 modeled hours per BA; numerical observed coverage with timestamp-level missingness; validated per-hour demand = gas + synthetic unserved; finite error diagnostics with sample sizes; SHA-256 integrity; and honest evidence boundaries. See `.github/workflows/project-b-two-ba-acceptance.yml` for the machine-checked paired-run and artifact gate.

This guide completes the documentation for the **narrow baseline engineering pipeline**. Further expansion to a real generator mix, physical transmission, calibrated BA interchange, storage optimization, and long-term dataset archival remains outstanding and is not implicitly covered by the pilot's success.
