"""Multi-year hourly allocation audit runner.

Usage:
python -m energy_transition.multiyear_audit --load state_hourly.csv --weights zonal_weights.csv --out audit.csv

load CSV: timestamp_utc,state,load_mw
weights CSV: state,zone,weight
No real-source provenance or calibration is implied by a passing accounting audit.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .zonal_conservation import allocate_hourly_load, validate_utc_year, conservation_audit
from .efs_geographic_provenance_gate import assess_weight_provenance


def run(load_path, weight_path, output_path, *, mapping_path=None, manifest_path=None):
    if (mapping_path is None) != (manifest_path is None):
        raise ValueError('mapping and manifest must be provided together')
    if mapping_path is not None:
        evidence = assess_weight_provenance(
            json.loads(Path(mapping_path).read_text(encoding='utf-8')),
            Path(weight_path).read_bytes(),
            json.loads(Path(manifest_path).read_text(encoding='utf-8')),
        )
        if not evidence['ready_for_full_network_dispatch']:
            raise ValueError('provenance or mapped network admission failed: ' + str(evidence['provenance_errors']))
    raw = pd.read_csv(load_path)
    needed = {"timestamp_utc", "state", "load_mw"}
    if not needed.issubset(raw.columns) or raw.empty:
        raise ValueError("load file needs timestamp_utc,state,load_mw")
    if raw[list(needed)].isna().any().any():
        raise ValueError("missing load fields")
    # Require explicit UTC offsets; utc=True alone silently assumes naive strings are UTC.\n    stamps = raw["timestamp_utc"].astype(str)\n    if not stamps.str.contains(r"(?:Z|[+]00:00)$", case=False, regex=True).all():\n        raise ValueError("timestamp_utc requires explicit UTC Z or +00:00 offset")\n    raw["timestamp_utc"] = pd.to_datetime(stamps, utc=True, errors="raise")
    raw["load_mw"] = pd.to_numeric(raw["load_mw"], errors="raise")
    if raw.duplicated(["timestamp_utc", "state"]).any():
        raise ValueError("duplicate timestamp/state")
    weights = pd.read_csv(weight_path)
    states = set(raw["state"])
    if not states:
        raise ValueError("no states")
    rows = []
    for year, group in raw.groupby(raw["timestamp_utc"].dt.year, sort=True):
        wide = group.pivot(index="timestamp_utc", columns="state", values="load_mw").sort_index()
        validate_utc_year(wide.index, int(year))
        if set(wide.columns) != states or wide.isna().any().any():
            raise ValueError(f"incomplete state coverage in {year}")
        zones = allocate_hourly_load(wide, weights)
        report = conservation_audit(wide, zones, weights)
        report.insert(0, "year", int(year))
        report["hours"] = len(wide)
        report["relative_error"] = np.where(report["source_mwh"] != 0,
            report["difference_mwh"] / report["source_mwh"], 0.0)
        rows.append(report)
    result = pd.concat(rows, ignore_index=True)
    if not np.allclose(result["difference_mwh"], 0, atol=1e-6, rtol=0):
        raise ValueError("annual conservation failure")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mapping", default=None, help="Require source-backed mapping and weights gate")
    parser.add_argument("--manifest", default=None, help="SHA-256 and geography metadata manifest")
    args = parser.parse_args()
    print(run(args.load, args.weights, args.out, mapping_path=args.mapping, manifest_path=args.manifest).to_string(index=False))


if __name__ == "__main__":
    main()
