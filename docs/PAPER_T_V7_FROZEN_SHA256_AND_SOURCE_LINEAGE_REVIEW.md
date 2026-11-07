# Paper T v7: repository-frozen SHA256 original-source supplement evidence

**Validated 6 November 2026; no new physical time claim.**

The earlier [source bundle CI #42332230767](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42332230767) archives 16 actual source-derived files: five tables T_S1–T_S5, three source-provenance JSON files, and Figures T1–T4 as SVG and PNG. The original bundle's internal `SHA256SUMS.txt` could be regenerated along with modified files, so its own integrity check alone was insufficient to pin an already-reviewed evidence version.

**New independently accepted lock:** [SHA256 lock CI #42335868902](https://github.com/ys30/Energy-Transition-Analysis-PyPSA/actions/runs/42335868902) successfully retrieved the old published Actions artifact and verified its 16 files against the source-repository-committed `docs/paper_t_frozen_supplement_sha256.txt`, not just its downloaded self-contained manifest. The validator `src/energy_transition/paper_t_frozen_sha_lock.py` and `tests/test_paper_t_frozen_sha_lock.py` reject changed bytes, missing approved entries, duplicate paths and altered scope.

To reproduce, download the accepted artifact (run 42332230767) and a checkout of the repository, then run:

```bash
cd paper-t-original-supplement
sha256sum -c SHA256SUMS.txt
sha256sum -c /absolute/path/to/Energy-Transition-Analysis-PyPSA/docs/paper_t_frozen_supplement_sha256.txt
PYTHONPATH=/absolute/path/to/Energy-Transition-Analysis-PyPSA/src \
  python -m energy_transition.paper_t_frozen_sha_lock \
    --lock /absolute/path/to/Energy-Transition-Analysis-PyPSA/docs/paper_t_frozen_supplement_sha256.txt \
    --bundle .
```

**Publisher-lineage correction:** The official [NLR EFS 2020 catalog](https://data.nlr.gov/submissions/126) states hourly source load scenarios were modeled by EnergyPATHWAYS and subsequently calibrated for use in ReEDS. The separate [ReEDS 2022-demand product](https://zenodo.org/records/18461543), deposited in February 2026, is another published model-data release with an explicit 2012 CST reference calendar. Similar output and near-identical annual energy from these **related model product lineages** are evidence of source-value correspondence, **not independent measurement replication**. Neither source record yet certifies a complete physical EFS2020 LocalHourID→UTC crosswalk.

**Publication status:** The new lock is a reproducibility/integrity improvement, **not** permanent accessibility. Github Actions artifacts still expire (90-day bundle retention) and **no derived-data DOI is registered**. Complete manuscript T v7 remains **private** and is not uploaded to this repository. Confirm dataset permissions before making a permanent public deposit of the tables and derived plots, and treat any data/figure changes as a new controlled checksum-lock version. There is still no original-source-authoritative Idaho time-zone/clock identification, wind/solar hourly synchronization or real Western-grid OPF.
