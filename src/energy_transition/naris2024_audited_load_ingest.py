"""Attach audited EFS state demand to an existing zonal PyPSA network.

This adapter never invents allocation weights, topology, or generators.
Synthetic operation requires an explicit opt-in and cannot imply calibration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def prepare_network_loads(
    network_path, state_load_csv, weights_csv, zone_bus_csv,
    output_network, audit_csv, zonal_csv,
    *, mapping_json=None, provenance_json=None, allow_synthetic=False,
):
    import pypsa
    from .export_zonal_loads import export_zonal_loads
    from .pypsa_load_adapter import build_load_matrix
    from .pypsa_network_ingest import attach_bus_loads

    if not allow_synthetic and (mapping_json is None or provenance_json is None):
        raise ValueError("Source-backed mode requires both mapping and provenance files")
    network = pypsa.Network(network_path)
    if network.buses.empty:
        raise ValueError("Network must contain existing buses")
    if not network.loads.empty:
        raise ValueError("Expected topology-only network without existing loads")

    # Source evidence is checked by the upstream export before any network mutation.
    export_zonal_loads(
        state_load_csv, weights_csv, audit_csv, zonal_csv,
        mapping_path=mapping_json, manifest_path=provenance_json,
        require_provenance=not allow_synthetic,
    )
    matrix = build_load_matrix(
        zonal_csv, zone_bus_csv, require_complete_years=True,
    )
    if set(matrix.columns) - set(network.buses.index):
        raise ValueError("Mapped load buses absent from actual network")
    if not isinstance(matrix.index, pd.DatetimeIndex) or matrix.index.tz is None:
        raise ValueError("Load matrix must be UTC-aware")

    # PyPSA expects timezone-naive timestamps; upstream has already verified UTC.
    network.set_snapshots(matrix.index.tz_convert("UTC").tz_localize(None))
    names = attach_bus_loads(network, matrix)
    target = Path(output_network)
    target.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(target)
    report = {
        "network_file": str(target),
        "snapshots": int(len(matrix.index)),
        "zones": int(len(matrix.columns)),
        "added_loads": names,
        "total_load_mwh": float(matrix.to_numpy().sum()),
        "source_provenance_required": not allow_synthetic,
        "synthetic_opt_in": bool(allow_synthetic),
        "optimization_solved": False,
        "historically_calibrated": False,
    }
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--network", type=Path, required=True)
    p.add_argument("--state-load", type=Path, required=True)
    p.add_argument("--weights", type=Path, required=True)
    p.add_argument("--zone-bus", type=Path, required=True)
    p.add_argument("--mapping", type=Path)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--allow-synthetic", action="store_true")
    p.add_argument("--output-network", type=Path, required=True)
    p.add_argument("--audit", type=Path, required=True)
    p.add_argument("--zonal", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    report = prepare_network_loads(
        a.network, a.state_load, a.weights, a.zone_bus,
        a.output_network, a.audit, a.zonal,
        mapping_json=a.mapping, provenance_json=a.manifest,
        allow_synthetic=a.allow_synthetic,
    )
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
