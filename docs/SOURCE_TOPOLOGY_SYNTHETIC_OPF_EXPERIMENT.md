# Source-topology synthetic two-bus OPF experiment (not physical dispatch)

**Research purpose.** This is the first isolated constrained-optimization experiment on a line selected from the pinned Breakthrough Energy synthetic Western source topology, rather than a fully invented line. It is **not** Palo Verde's real transmission model, not an EIA-860 generator mapping, and not a complete Western-system OPF.

## Reproducible experiment

`python -m energy_transition.source_topology_synthetic_dispatch --network /path/to/source-western.nc --anchor 2040841 --out outputs/synthetic_source_topology_dispatch.json`

The script finds the first original AC Line (sorted by source line ID) incident on anchor model bus `2040841`, with positive reactance and same nominal voltage on both endpoints. It copies only the source-model line endpoints, nominal voltages, and original per-line `r` and `x`.

Everything else is **declared synthetic**: 100 MW receiving-end demand; 200 MW nameplate cheap generator at anchor with marginal cost 1; 200 MW backup generator at the remote bus with cost 100; 25, 50 and 125 MW line capacity scenarios. The source line's original power rating is *not claimed* to have been measured or validated.

Expected analytical outputs for `rating = c` and 100 MW demand:

- cheap supply and line transfer `min(c,100)` MW;
- backup dispatch `100 - min(c,100)` MW;
- synthetic cost objective `min(c,100) + 100 * (100 - min(c,100))`.

Expected sweep (synthetic cost units, not USD):

| Assumed line capacity (MW) | Cheap supply (MW) | Backup supply (MW) | Optimal synthetic cost |
|---:|---:|---:|---:|
| 25 | 25 | 75 | 7525 |
| 50 | 50 | 50 | 5050 |
| 125 | 100 | 0 | 100 |

The GitHub CI compares the computed values to this analytical benchmark with numerical tolerances. **The table is the experiment specification, not a claim of successful CI execution.** Actual solver execution must be verified in [source-topology-synthetic-dispatch.yml](../.github/workflows/source-topology-synthetic-dispatch.yml).

## Scientific limitations

Only a two-bus **island extracted from a synthetic source grid** is solved. No verified Palo Verde generator, real operator line rating, contingency set, N-1 constraints, 8760-hour fleet, or actual transmission condition is represented. This experiment is valuable for validating provenance-preserving extraction and the solver's response to line limits, but cannot support real-world regional energy-transition outcomes.

See [synthetic source network provenance](WESTERN_SYNTHETIC_NETWORK_PROVENANCE.md).
