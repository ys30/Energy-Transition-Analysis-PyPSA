"""Reproducible two-bus OPF on an ORIGINAL synthetic-source branch.

The selected branch endpoints, nominal voltages and electrical r/x are from a
pinned source network. Generators, load, line rating and costs are conspicuously
synthetic experimental inputs. Not a physical Palo Verde dispatch or full OPF.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa


def experiment(network_path: Path, out: Path, anchor: str="2040841",
               ratings=(25.0, 50.0, 125.0)):
    source=pypsa.Network(str(network_path))
    bus_ids=set(source.buses.index.astype(str))
    if anchor not in bus_ids:
        raise ValueError(f"Anchoring bus absent from original source: {anchor}")
    if any(not np.isfinite(x) or x<=0 for x in ratings):
        raise ValueError("Synthetic line ratings must be positive and finite")
    original=source.lines.loc[source.lines.bus0.astype(str).eq(anchor)|
                              source.lines.bus1.astype(str).eq(anchor)].copy()
    original["r_num"]=pd.to_numeric(original.r,errors="coerce")
    original["x_num"]=pd.to_numeric(original.x,errors="coerce")
    original["candidate_neighbor"]=original.apply(
        lambda z: str(z.bus1) if str(z.bus0)==anchor else str(z.bus0),axis=1)
    original=original.loc[original.r_num.ge(0)&original.x_num.gt(0)&
                          original.candidate_neighbor.isin(bus_ids)]
    # Same-voltage endpoints permit an AC line test without inventing transformer taps.
    original=original.loc[original.candidate_neighbor.map(
        lambda k: abs(float(source.buses.loc[k,"v_nom"])-float(source.buses.loc[anchor,"v_nom"]))<0.01)]
    original=original.sort_index()
    if original.empty:
        raise ValueError("No eligible positive-reactance same-voltage source Line from anchor")
    source_id=str(original.index[0])
    branch=original.iloc[0]
    other=str(branch.candidate_neighbor)
    results=[]
    for rating in ratings:
        n=pypsa.Network()
        n.set_snapshots(pd.date_range("2024-01-01",periods=1,freq="h"))
        for bus in (anchor,other):
            n.add("Bus",bus,v_nom=float(source.buses.loc[bus,"v_nom"]))
        n.add("Line","selected_source_branch_synthetic_rating",
              bus0=str(branch.bus0),bus1=str(branch.bus1),
              r=float(branch.r_num),x=float(branch.x_num),s_nom=float(rating))
        # Consistent direction: cheap plant at anchor, load and expensive backup at other.
        n.add("Generator","synthetic_low_cost",bus=anchor,p_nom=200,marginal_cost=1)
        n.add("Generator","synthetic_backup",bus=other,p_nom=200,marginal_cost=100)
        n.add("Load","synthetic_demand",bus=other,p_set=100)
        status,condition=n.optimize(solver_name="highs")
        if (status,condition)!=("ok","optimal"):
            raise RuntimeError(f"Synthetic network solve failed: {status}/{condition}")
        cheap=float(n.generators_t.p.at[n.snapshots[0],"synthetic_low_cost"])
        backup=float(n.generators_t.p.at[n.snapshots[0],"synthetic_backup"])
        flow=float(n.lines_t.p0.iat[0,0])
        exp=min(float(rating),100.0)
        if abs(cheap-exp)>0.15 or abs(backup-(100-exp))>0.15:
            raise AssertionError(f"Dispatch violates synthetic expected economic optimum: {cheap}, {backup}")
        if abs(cheap+backup-100)>0.1 or abs(flow)>rating+0.1:
            raise AssertionError("Synthetic power balance or flow capacity violated")
        obj=float(n.objective)
        if abs(obj-(exp+100*(100-exp)))>1:
            raise AssertionError("Synthetic objective inconsistent with analytic optimum")
        results.append({"synthetic_line_rating_mw":float(rating),
                        "cheap_generator_dispatch_mw":cheap,
                        "backup_dispatch_mw":backup,
                        "line_flow_mw":flow,"objective_synthetic_cost_units":obj})
    if any(a["objective_synthetic_cost_units"]<=b["objective_synthetic_cost_units"]
           for a,b in zip(results,results[1:])):
        raise AssertionError("Increasing synthetic line rating failed to reduce objective")
    report={"network_provenance":"pinned PyPSA-USA Breakthrough Energy synthetic USATestSystem",
            "original_source_anchor_bus_id":anchor,
            "original_source_branch_id":source_id,
            "source_branch_bus0":str(branch.bus0),"source_branch_bus1":str(branch.bus1),
            "source_branch_r_ohm":float(branch.r_num),"source_branch_x_ohm":float(branch.x_num),
            "source_bus_voltage_kv":float(source.buses.loc[anchor,"v_nom"]),
            "experimental_generator_and_load_data":"synthetic, not EIA-860",
            "experimental_line_ratings":"synthetic, not actual facility ratings",
            "source_facility_identity_verified":False,
            "real_western_opf_executed":False,
            "synthetic_two_bus_opf_executed":True,
            "capacity_sweep":results}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--anchor",default="2040841")
    a=p.parse_args()
    experiment(a.network,a.out,anchor=a.anchor)


if __name__=="__main__":
    main()
