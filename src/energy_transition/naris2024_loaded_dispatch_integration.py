"""Solve an admitted zonal-load network with explicitly hypothetical generation.

This is a load-to-optimizer integration test, NOT a calibrated Western
generation fleet or a historical transmission-cost estimate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa


def solve_loaded_network(network_path: Path, load_report_path: Path, *,
                         synthetic_fixture: bool = False) -> dict:
    report = json.loads(Path(load_report_path).read_text(encoding="utf-8"))
    if not synthetic_fixture and not all(
        report.get(k) is True for k in (
            "source_provenance_required",
            "western_membership_verified",
            "netcdf_load_roundtrip_verified",
            "netcdf_topology_roundtrip_verified",
        )
    ):
        raise ValueError("Source-backed load admission flags not all present")
    if report.get("optimization_solved") is not False or report.get("historically_calibrated") is not False:
        raise ValueError("Expected unsolved, uncalibrated load-ingestion report")
    n = pypsa.Network(network_path)
    if len(n.buses) < 2 or len(n.links) == 0 or len(n.lines):
        raise ValueError("Expected nonempty zonal Link network, not AC Lines")
    if n.generators.size or n.storage_units.size or n.stores.size:
        raise ValueError("Expected load-only network without preexisting supply")
    if not len(n.snapshots) or len(n.loads) == 0:
        raise ValueError("No hourly loads attached")
    if len(n.snapshots) != report.get("snapshots") or len(n.loads) != report.get("zones"):
        raise ValueError("Load report and network dimensions mismatch")
    demand = n.loads_t.p_set.reindex(index=n.snapshots, columns=n.loads.index)
    if demand.isna().any().any():
        raise ValueError("Missing load snapshot values")
    values = demand.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Invalid load values")
    if not np.isclose(float(values.sum()), float(report.get("total_load_mwh", float("nan"))),
                      rtol=0, atol=max(1e-5, values.size * 1e-8)):
        raise ValueError("Load report total fails conservation check")
    if not n.loads.bus.isin(n.buses.index).all():
        raise ValueError("Unrecognized load bus")
    if not n.links.bus0.isin(n.buses.index).all() or not n.links.bus1.isin(n.buses.index).all():
        raise ValueError("Unrecognized Link endpoint")
    limits = n.links.p_nom.to_numpy(dtype=float)
    if not np.isfinite(limits).all() or (limits <= 0).any():
        raise ValueError("Invalid Link capacities")
    if not np.allclose(n.links.efficiency.to_numpy(dtype=float), 1.0):
        raise ValueError("This demonstration requires lossless directional Links")
    if not np.allclose(n.links.p_min_pu.to_numpy(dtype=float), 0.0):
        raise ValueError("This demonstration requires forward-only Links")
    if not np.allclose(n.links.p_max_pu.to_numpy(dtype=float), 1.0):
        raise ValueError("This demonstration requires fixed directional capacities")

    peak = float(demand.sum(axis=1).max())
    # Hypothetical centrally located supply and fully dispatchable local backup.
    # Costs are arbitrary units per MWh, not published historical operating costs.
    # Place cheap central supply on a link-connected bus, never on an
    # isolated membership zone (e.g., p19). This makes isolation accounting
    # physically meaningful within the hypothetical screening case.
    connected_buses = set(n.links.bus0).union(set(n.links.bus1))
    source = sorted(connected_buses)[0]
    n.add("Generator", "hypothetical_central", bus=source,
          p_nom=max(peak, 1.0), marginal_cost=1.0)
    for bus in n.buses.index:
        n.add("Generator", f"hypothetical_backup_{bus}", bus=bus,
              p_nom=max(peak, 1.0), marginal_cost=100.0)
    status, condition = n.optimize(solver_name="highs")
    if (status, condition) != ("ok", "optimal"):
        raise ValueError(f"Optimization failed: {status}/{condition}")
    production = n.generators_t.p.reindex(index=n.snapshots, columns=n.generators.index)
    p0 = n.links_t.p0.reindex(index=n.snapshots, columns=n.links.index)
    p1 = n.links_t.p1.reindex(index=n.snapshots, columns=n.links.index)
    if (p0.to_numpy(dtype=float) < -1e-4).any() or (
        p0.to_numpy(dtype=float) > limits[None, :] + 1e-4
    ).any():
        raise ValueError("Directional interface capacity violation")
    max_bus_error = 0.0
    for bus in n.buses.index:
        generated = production.loc[:, n.generators.bus.eq(bus)].sum(axis=1)
        consumed = demand.loc[:, n.loads.bus.eq(bus)].sum(axis=1)
        exports = p0.loc[:, n.links.bus0.eq(bus)].sum(axis=1)
        other_end = p1.loc[:, n.links.bus1.eq(bus)].sum(axis=1)
        max_bus_error = max(max_bus_error, float(
            (generated - consumed - exports - other_end).abs().max()
        ))
    if max_bus_error > 1e-3:
        raise ValueError(f"Nodal power balance failed: {max_bus_error} MW")
    # Isolated membership zones must be reported separately: their locally
    # supplied energy is not evidence of interzonal transmission benefit.
    link_endpoints = set(n.links.bus0).union(set(n.links.bus1))
    isolated = sorted(set(n.buses.index) - link_endpoints)
    isolated_load_mwh = float(demand.loc[:, n.loads.bus.isin(isolated)].to_numpy(dtype=float).sum())
    isolated_backup_mwh = float(production.loc[:, n.generators.bus.isin(isolated)].to_numpy(dtype=float).sum())
    if abs(isolated_load_mwh - isolated_backup_mwh) > max(1e-3, isolated_load_mwh * 1e-8):
        raise ValueError("Isolated-zone local supply does not match local demand")
    backup_by_bus_mwh = {
        str(bus): float(production[f"hypothetical_backup_{bus}"].sum())
        for bus in n.buses.index
    }
    if abs(sum(backup_by_bus_mwh.values()) - float(
        production.drop(columns="hypothetical_central").to_numpy(dtype=float).sum()
    )) > 1e-3:
        raise ValueError("Per-zone backup accounting inconsistent")
    generated_mwh = float(production.to_numpy(dtype=float).sum())
    loaded_mwh = float(values.sum())
    if abs(generated_mwh - loaded_mwh) > max(1e-3, loaded_mwh * 1e-8):
        raise ValueError("System-wide energy balance failed")
    return {
        "snapshots": len(n.snapshots),
        "zones": len(n.buses),
        "directional_links": len(n.links),
        "hypothetical_central_source_bus": source,
        "isolated_zone_ids": isolated,
        "isolated_zone_count": len(isolated),
        "isolated_zone_demand_mwh": isolated_load_mwh,
        "isolated_zone_local_generation_mwh": isolated_backup_mwh,
        "hypothetical_backup_by_zone_mwh": backup_by_bus_mwh,
        "input_load_mwh": loaded_mwh,
        "optimized_generation_mwh": generated_mwh,
        "hypothetical_backup_mwh": float(production.drop(
            columns="hypothetical_central").to_numpy(dtype=float).sum()),
        "max_nodal_balance_residual_mw": max_bus_error,
        "solver_status": status,
        "solver_condition": condition,
        "cost_units": float(n.objective),
        "source_backed_load_report_flags_present": not synthetic_fixture,
        "synthetic_fixture": synthetic_fixture,
        "generation_costs_and_capacity_hypothetical": True,
        "historical_calibration": False,
        "empirical_generation_dispatch_claim": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--load-report", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--synthetic-fixture", action="store_true")
    args = parser.parse_args()
    result = solve_loaded_network(args.network, args.load_report,
                                  synthetic_fixture=args.synthetic_fixture)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
