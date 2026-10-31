"""Full Western NARIS zonal topology optimization with hypothetical demand.

Source-backed: zonal network and directional transfer capacities only.
Hypothetical: single-hour loads, generators, fuel costs. Not 2024 calibration.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pypsa


def solve_western(network_path: Path) -> dict:
    n=pypsa.Network(network_path)
    if len(n.buses)<2 or len(n.links)<1:
        raise ValueError("Western region graph is empty")
    if len(n.loads) or len(n.generators) or len(n.storage_units):
        raise ValueError("Expected topology-only network, not an existing dispatch case")
    # Source-wide, deterministic synthetic experiment: 100 MW demand and
    # dispatchable local backup at every zone; cheap supply at one region.
    n.set_snapshots(["2024-01-01T00:00"])
    for bus in n.buses.index:
        n.add("Load",f"demand_{bus}",bus=bus,p_set=100.0)
        n.add("Generator",f"backup_{bus}",bus=bus,p_nom=100.0,marginal_cost=100.0)
    source=str(sorted(n.buses.index)[0])
    n.add("Generator","hypothetical_low_cost_supply",bus=source,
          p_nom=100.0*len(n.buses),marginal_cost=1.0)
    status,condition=n.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":
        raise ValueError(f"Optimization failed: {status}/{condition}")
    t=n.snapshots[0]
    total_demand=float(n.loads_t.p.loc[t].sum())
    total_gen=float(n.generators_t.p.loc[t].sum())
    flows=n.links_t.p0.loc[t].reindex(n.links.index).to_numpy(dtype=float)
    ratings=n.links.p_nom.to_numpy(dtype=float)
    if not np.isfinite(flows).all() or (flows < -1e-5).any() or (flows>ratings+1e-4).any():
        raise ValueError("Directional NARIS Link rating violation")
    if abs(total_demand-total_gen)>1e-3:
        raise ValueError("System generation/load mismatch")
    return {"buses":len(n.buses),"directional_links":len(n.links),
            "synthetic_demand_mw":total_demand,"optimized_generation_mw":total_gen,
            "hypothetical_low_cost_generation_mw":float(n.generators_t.p.loc[t,"hypothetical_low_cost_supply"]),
            "backup_generation_mw":float(n.generators_t.p.loc[t].drop("hypothetical_low_cost_supply").sum()),
            "max_link_utilization_fraction":float((flows/ratings).max()),
            "binding_link_count":int(np.sum(np.isclose(flows,ratings,atol=1e-4,rtol=1e-7))),
            "solver_status":status,"solver_condition":condition,
            "assumptions":"100 MW demand and 100 MW backup supply per bus; 1 vs 100 marginal cost; one-hour illustrative experiment",
            "source_backed":"NARIS2024 zonal directed transfer interface capacities",
            "historical_calibrated":False,"physical_ac_power_flow":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=solve_western(a.network)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
