"""Four-node two-EFS-load AC-line dispatch pilot with illustrative generators.

Uses source line parameters and original EFS hourly load at two distinct buses.
Only a small structural test: no observed generation, boundary interchange,
UTC synchronization or full Western optimization is claimed.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa

PATH_BUSES = ("2040602", "2040610", "2040614", "2040645")
PATH_LINES = ("97145", "97156", "97159")


def solve(network: Path, out: Path, hours: int = 24):
    src = pypsa.Network(str(network))
    if hours != 24 or len(src.snapshots) < hours:
        raise ValueError("Pilot requires 24 source hourly snapshots")
    if any(b not in src.buses.index for b in PATH_BUSES):
        raise ValueError("Missing original Western path bus")
    if any(l not in src.lines.index for l in PATH_LINES):
        raise ValueError("Missing original Western AC line")
    rows = src.lines.loc[list(PATH_LINES)]
    observed = {frozenset((str(r.bus0), str(r.bus1))) for r in rows.itertuples()}
    expected = {frozenset((a, b)) for a, b in zip(PATH_BUSES, PATH_BUSES[1:])}
    if observed != expected:
        raise ValueError("Selected original AC path changed")
    sub = pypsa.Network()
    snaps = src.snapshots[:hours]
    sub.set_snapshots(snaps)
    for b in PATH_BUSES:
        sub.add("Bus", b, v_nom=float(src.buses.at[b, "v_nom"]))
    for lid, r in rows.iterrows():
        if not (np.isfinite(float(r.r)) and float(r.r) >= 0
                and np.isfinite(float(r.x)) and float(r.x) > 0
                and np.isfinite(float(r.s_nom)) and float(r.s_nom) >= 100):
            raise ValueError(f"Source AC line parameters invalid: {lid}")
        sub.add("Line", str(lid), bus0=str(r.bus0), bus1=str(r.bus1),
                r=float(r.r), x=float(r.x), s_nom=float(r.s_nom))
    profiles = {}
    for bus in (PATH_BUSES[0], PATH_BUSES[-1]):
        ids = [i for i in src.loads.index[src.loads.bus.astype(str).eq(bus)]
               if str(i).startswith("EFS_") and i in src.loads_t.p_set.columns]
        if not ids:
            raise ValueError(f"No admitted dynamic EFS load on {bus}")
        demand = src.loads_t.p_set.loc[snaps, ids].sum(axis=1).astype(float)
        if not np.isfinite(demand.to_numpy()).all() or (demand <= 0).any():
            raise ValueError(f"Bad EFS sample for {bus}")
        profiles[bus] = demand
        sub.add("Load", f"EFS_{bus}", bus=bus, p_set=demand.to_numpy())
    peak = float(sum(profiles.values()).max())
    # Intentionally put inexpensive illustrative supply at smaller-load end,
    # and expensive backup at the larger-load end, to test congestion.
    low_load_bus = min(profiles, key=lambda b: float(profiles[b].sum()))
    high_load_bus = next(b for b in profiles if b != low_load_bus)
    sub.add("Generator", "illustrative_cheap", bus=low_load_bus,
            p_nom=peak * 2, marginal_cost=10)
    sub.add("Generator", "illustrative_backup", bus=high_load_bus,
            p_nom=peak * 2, marginal_cost=100)
    status, condition = sub.optimize(solver_name="highs")
    if (status, condition) != ("ok", "optimal"):
        raise RuntimeError(f"Solver: {status}/{condition}")
    actual = float(sum(x.sum() for x in profiles.values()))
    dispatched = float(sub.generators_t.p.sum().sum())
    if abs(actual - dispatched) > max(0.01, actual * 1e-8):
        raise ValueError("Aggregated generation/load mismatch")
    residuals = {}
    for b in PATH_BUSES:
        generation = sub.generators_t.p.loc[:, sub.generators.index[sub.generators.bus == b]].sum(axis=1)
        loads = sub.loads_t.p_set.loc[:, sub.loads.index[sub.loads.bus == b]].sum(axis=1)
        outgoing = sum(
            (sub.lines_t.p0[lid] if sub.lines.at[lid, "bus0"] == b
             else sub.lines_t.p1[lid])
            for lid in PATH_LINES if b in (sub.lines.at[lid, "bus0"], sub.lines.at[lid, "bus1"])
        )
        residuals[b] = float((generation - loads - outgoing).abs().max())
    max_residual = max(residuals.values())
    if max_residual > 1e-3:
        raise ValueError(f"Nodal power residual exceeds tolerance: {max_residual}")
    usage = sub.lines_t.p0.abs().divide(sub.lines.s_nom, axis=1)
    max_usage = float(usage.max().max())
    if max_usage > 1.000001:
        raise ValueError("Source line rating exceeded")
    result = {
        "planning_year": int(snaps[0].year),
        "snapshot_hours": hours, "buses": list(PATH_BUSES), "lines": list(PATH_LINES),
        "actual_efs_load_buses": list(profiles),
        "efs_load_mwh_by_bus": {b: float(v.sum()) for b, v in profiles.items()},
        "efs_load_mwh_total": actual, "dispatch_mwh_total": dispatched,
        "generator_bus_placement": {"illustrative_cheap": low_load_bus,
                                    "illustrative_backup": high_load_bus},
        "generator_mwh": {str(k): float(sub.generators_t.p[k].sum()) for k in sub.generators.index},
        "peak_abs_line_flow_mw": {str(k): float(sub.lines_t.p0[k].abs().max()) for k in sub.lines.index},
        "max_line_utilization": {str(k): float(usage[k].max()) for k in usage.columns},
        "binding_line_ids": [str(k) for k in usage.columns if (usage[k] >= 0.999999).any()],
        "maximum_nodal_residual_mw": max_residual,
        "objective_illustrative_usd": float(sub.objective),
        "solver_status": status, "solver_condition": condition,
        "source_real_ac_line_parameters": True,
        "source_real_efs_loads": True,
        "generation_illustrative": True,
        "timezone_aligned": False, "full_western_optimized": False,
        "network_boundary_injections_verified": False,
        "limitations": "Isolated line path, source EFS local-hour profiles; original lines but illustrative generators/costs; no external boundary injections or calibrated full grid.",
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    solve(args.network, args.out)
