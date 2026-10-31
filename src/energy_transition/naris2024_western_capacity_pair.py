"""Paired Western network capacity sensitivity with explicitly hypothetical loads.

The same synthetic demand/generation is solved twice; only NARIS Link ratings
change. This is a topology/congestion diagnostic, never historical savings.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pypsa
import numpy as np


def experiment(source: Path, multiplier: float) -> dict:
    n=pypsa.Network(source)
    if not np.isfinite(multiplier) or multiplier < 1:
        raise ValueError("Capacity multiplier must be finite and >= 1")
    if len(n.buses)<2 or len(n.links)==0:
        raise ValueError("Missing western zonal topology")
    n.set_snapshots(["2024-01-01T00:00"])
    n.links["p_nom"]=n.links.p_nom.astype(float)*multiplier
    origin=sorted(n.buses.index)[0]
    for bus in n.buses.index:
        n.add("Load",f"test_load_{bus}",bus=bus,p_set=100.0)
        n.add("Generator",f"test_backup_{bus}",bus=bus,p_nom=100.0,marginal_cost=100.0)
    n.add("Generator","test_central_supply",bus=origin,
          p_nom=len(n.buses)*100.0,marginal_cost=1.0)
    status,termination=n.optimize(solver_name="highs")
    if (status,termination)!=("ok","optimal"):
        raise ValueError("Optimization did not converge")
    snapshot=n.snapshots[0]
    flows=n.links_t.p0.loc[snapshot].reindex(n.links.index).to_numpy(dtype=float)
    ratings=n.links.p_nom.to_numpy(dtype=float)
    if (flows>ratings+1e-4).any() or (flows < -1e-4).any():
        raise ValueError("Directed transfer capacity exceeded")
    generated=float(n.generators_t.p.loc[snapshot].sum())
    demand=float(n.loads_t.p.loc[snapshot].sum())
    if abs(generated-demand)>1e-3:
        raise ValueError("Dispatch power balance mismatch")
    backup=float(n.generators_t.p.loc[snapshot].drop("test_central_supply").sum())
    return {"capacity_multiplier":multiplier,"source_regions":len(n.buses),
            "source_directed_links":len(n.links),"hypothetical_demand_mw":demand,
            "local_backup_mw":backup,"dispatch_cost_arbitrary_units":float(n.objective),
            "binding_interfaces":int(np.isclose(flows,ratings,atol=1e-4,rtol=1e-7).sum()),
            "solver_status":status}


def paired(source: Path) -> dict:
    baseline=experiment(source,1.0)
    expanded=experiment(source,10.0)
    if expanded["dispatch_cost_arbitrary_units"]>baseline["dispatch_cost_arbitrary_units"]+1e-3:
        raise ValueError("Relaxing transmission cannot increase optimum cost")
    return {"baseline":baseline,"tenfold_capacity":expanded,
            "modeled_objective_reduction_arbitrary_units":baseline["dispatch_cost_arbitrary_units"]-expanded["dispatch_cost_arbitrary_units"],
            "interpretation":"Synthetic dispatch comparison over published NARIS zonal limits, not a real network upgrade valuation",
            "real_historical_calibration":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=paired(a.network)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
