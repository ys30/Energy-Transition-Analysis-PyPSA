"""Run a reproducible, explicitly synthetic three-zone PyPSA dispatch example.

This is NOT a historical WECC result. All MW and marginal costs are illustrative.
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import pypsa

from .pypsa_network_ingest import attach_bus_loads


def solve_three_zone():
    n = pypsa.Network()
    utc = pd.date_range("2024-01-01", periods=2, freq="h", tz="UTC")
    n.set_snapshots(utc.tz_localize(None))
    for bus in ("A", "B", "C"):
        n.add("Bus", bus)
    n.add("Link", "A_B", bus0="A", bus1="B", p_nom=40.0, efficiency=1.0)
    n.add("Link", "B_C", bus0="B", bus1="C", p_nom=25.0, efficiency=1.0)
    for name, bus, cost in (("cheap_A", "A", 1.0),
                            ("backup_B", "B", 50.0),
                            ("backup_C", "C", 100.0)):
        n.add("Generator", name, bus=bus, p_nom=100.0, marginal_cost=cost)
    attach_bus_loads(n, pd.DataFrame({"B": [20., 20.], "C": [50., 50.]}, index=utc))
    status, condition = n.optimize(solver_name="highs")
    if (status, condition) != ("ok", "optimal"):
        raise ValueError(f"PyPSA solve failed: {status}/{condition}")
    snapshots = []
    for stamp in n.snapshots:
        generators = {k: float(v) for k, v in n.generators_t.p.loc[stamp].items()}
        transfers = {k: float(v) for k, v in n.links_t.p0.loc[stamp].items()}
        nodal = {}
        for bus in n.buses.index:
            gen = float(n.generators_t.p.loc[stamp, n.generators.bus == bus].sum())
            demand = float(n.loads_t.p.loc[stamp, n.loads.bus == bus].sum())
            exports = float(n.links_t.p0.loc[stamp, n.links.bus0 == bus].sum())
            imports_negative = float(n.links_t.p1.loc[stamp, n.links.bus1 == bus].sum())
            nodal[str(bus)] = gen - demand - exports - imports_negative
        if max(abs(x) for x in nodal.values()) > 1e-5:
            raise ValueError("Nodal power balance failed")
        if any(v < -1e-5 or v > float(n.links.loc[k, "p_nom"]) + 1e-5
               for k, v in transfers.items()):
            raise ValueError("Directional transfer capacity violated")
        snapshots.append({
            "timestamp_utc": pd.Timestamp(stamp).isoformat() + "Z",
            "generation_mw": generators,
            "transfer_mw": transfers,
            "nodal_residual_mw": nodal,
            "demand_mw": float(n.loads_t.p.loc[stamp].sum()),
            "dispatch_cost_usd_per_hour": sum(
                power * float(n.generators.loc[name, "marginal_cost"])
                for name, power in generators.items()
            ),
        })
    return {
        "scenario": "synthetic_three_zone_two_hour",
        "historically_calibrated": False,
        "source_backed_transmission": False,
        "physical_ac_power_flow": False,
        "solver_status": status,
        "solver_condition": condition,
        "snapshots": snapshots,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = solve_three_zone()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
