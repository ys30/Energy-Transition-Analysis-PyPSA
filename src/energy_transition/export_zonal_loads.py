"""Export audited state demand as zone-hour PyPSA Load time series.

Accounting-only export. Network topology, bus membership and optimization
must be validated independently; no synthetic topology is inferred here.
"""
import argparse
from pathlib import Path
import pandas as pd

from .multiyear_audit import run
from .zonal_conservation import allocate_hourly_load, validate_utc_year


def export_zonal_loads(load_path, weights_path, audit_path, output_path,
                       *, mapping_path=None, manifest_path=None, require_provenance=True):
    """Fail closed on provenance by default; emit timestamp_utc,zone,load_mw."""
    run(load_path, weights_path, audit_path, mapping_path=mapping_path,
        manifest_path=manifest_path, require_provenance=require_provenance)
    raw = pd.read_csv(load_path)
    raw["timestamp_utc"] = pd.to_datetime(raw["timestamp_utc"], utc=True)
    weights = pd.read_csv(weights_path)
    chunks = []
    for year, group in raw.groupby(raw["timestamp_utc"].dt.year, sort=True):
        wide = group.pivot(index="timestamp_utc", columns="state", values="load_mw").sort_index()
        validate_utc_year(wide.index, int(year))
        allocated = allocate_hourly_load(wide, weights)
        long = allocated.rename_axis("timestamp_utc").reset_index().melt(
            id_vars="timestamp_utc", var_name="zone", value_name="load_mw")
        chunks.append(long)
    result = pd.concat(chunks, ignore_index=True).sort_values(
        ["timestamp_utc", "zone"], kind="stable").reset_index(drop=True)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", required=True)
    parser.add_argument("--weights", required=True)
    parser.add_argument("--audit", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mapping")
    parser.add_argument("--manifest")
    parser.add_argument("--allow-synthetic", action="store_true",
                        help="Disable provenance gate for synthetic fixtures only")
    args = parser.parse_args()
    result = export_zonal_loads(
        args.load, args.weights, args.audit, args.out,
        mapping_path=args.mapping, manifest_path=args.manifest,
        require_provenance=not args.allow_synthetic)
    print(f"Exported {len(result)} zone-hour rows to {args.out}")


if __name__ == "__main__":
    main()
