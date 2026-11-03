"""Three-bus, three-hour synthetic OPF using two pinned-source AC line records.

Only bus identities, voltage and line resistance/reactance come from the
Breakthrough Energy synthetic source. Ratings, supply, demand and costs are
hypothetical test inputs; not real Palo Verde dispatch or Western OPF.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa


def experiment(network_path: Path, out: Path, anchor="2040841",
               ratings=(25.0, 50.0, 125.0)):
    source=pypsa.Network(str(network_path))
    buses=source.buses
    if anchor not in buses.index:
        raise ValueError("Anchor absent from source topology")
    if not ratings or any(not np.isfinite(v) or v<=0 for v in ratings):
        raise ValueError("Ratings must be positive and finite")
    candidates=source.lines.loc[
        source.lines.bus0.astype(str).eq(anchor) |
        source.lines.bus1.astype(str).eq(anchor)].copy()
    candidates["neighbor"]=candidates.apply(
        lambda r:str(r.bus1) if str(r.bus0)==anchor else str(r.bus0), axis=1)
    candidates["r_valid"]=pd.to_numeric(candidates.r, errors="coerce")
    candidates["x_valid"]=pd.to_numeric(candidates.x, errors="coerce")
    candidates=candidates.loc[
        candidates.neighbor.isin(buses.index) &
        candidates.r_valid.ge(0) &
        candidates.x_valid.gt(0)]
    voltage=float(buses.loc[anchor,"v_nom"])
    candidates=candidates.loc[candidates.neighbor.map(
        lambda k:abs(float(buses.loc[k,"v_nom"])-voltage)<0.01)]
    # Deliberately use two distinct neighbors to create an acyclic 3-bus star.
    candidates=candidates.sort_index().drop_duplicates(subset=["neighbor"]).head(2)
    if len(candidates)!=2:
        raise ValueError("At least two distinct same-voltage positive-x source neighbors required")
    neighbor_ids=candidates.neighbor.astype(str).tolist()
    # Three consecutive synthetic one-hour snapshots, not measured time series.
    times=pd.date_range("2024-01-01", periods=3, freq="h")
    demand=pd.DataFrame({
        neighbor_ids[0]:[60.0,90.0,120.0],
        neighbor_ids[1]:[40.0,75.0,100.0]}, index=times)
    source_lines=[str(k) for k in candidates.index]
    records=[]
    for rating in ratings:
        n=pypsa.Network()
        n.set_snapshots(times)
        for bus_id in [anchor]+neighbor_ids:
            n.add("Bus",bus_id,v_nom=voltage)
        for i,(line_id,branch) in enumerate(candidates.iterrows()):
            n.add("Line",f"source_line_{i}",bus0=str(branch.bus0),
                  bus1=str(branch.bus1),r=float(branch.r_valid),
                  x=float(branch.x_valid),s_nom=float(rating))
        n.add("Generator","cheap_synthetic",bus=anchor,p_nom=500,marginal_cost=1)
        for i,bus in enumerate(neighbor_ids):
            n.add("Generator",f"backup_{i}",bus=bus,p_nom=300,marginal_cost=100)
            n.add("Load",f"load_{i}",bus=bus,p_set=demand[bus])
        status,condition=n.optimize(solver_name="highs")
        if (status,condition)!=("ok","optimal"):
            raise RuntimeError(f"Solver failed: {status}/{condition}")
        for timestamp in times:
            expected_cheap=sum(min(float(rating),float(demand.loc[timestamp,b]))
                               for b in neighbor_ids)
            expected_backup=sum(max(float(demand.loc[timestamp,b])-float(rating),0)
                                for b in neighbor_ids)
            actual_cheap=float(n.generators_t.p.at[timestamp,"cheap_synthetic"])
            actual_backup=sum(float(n.generators_t.p.at[timestamp,f"backup_{i}"]) for i in range(2))
            if abs(expected_cheap-actual_cheap)>0.2 or abs(expected_backup-actual_backup)>0.2:
                raise AssertionError("Multi-hour economic dispatch differs from analytic tree-flow optimum")
            if abs(actual_cheap+actual_backup-float(demand.loc[timestamp].sum()))>0.1:
                raise AssertionError("Snapshot-level source-sink balance failed")
            line_flows=n.lines_t.p0.loc[timestamp]
            if (line_flows.abs()>float(rating)+0.1).any():
                raise AssertionError("Synthetic source-line flow limit exceeded")
            if abs(float(n.generators_t.p.loc[timestamp].sum())-float(demand.loc[timestamp].sum()))>0.1:
                raise AssertionError("Generation and load imbalance")
            records.append({
                "hypothetical_rating_mw":float(rating),
                "snapshot":str(timestamp),
                "total_hypothetical_load_mw":float(demand.loc[timestamp].sum()),
                "low_cost_supply_mw":actual_cheap,
                "backup_supply_mw":actual_backup,
                "max_absolute_branch_flow_mw":float(line_flows.abs().max()),
                "analytic_low_cost_mw":float(expected_cheap),
                "analytic_backup_mw":float(expected_backup),
            })
        expected_obj=sum(
            sum(min(float(rating),float(demand.loc[t,b])) for b in neighbor_ids) +
            100*sum(max(float(demand.loc[t,b])-float(rating),0) for b in neighbor_ids)
            for t in times)
        if abs(float(n.objective)-expected_obj)>1:
            raise AssertionError(f"Optimized cost {n.objective} != analytical {expected_obj}")
        for row in records:
            if row["hypothetical_rating_mw"]==float(rating):
                row["scenario_objective_cost_units"]=float(n.objective)
    totals=[next(x["scenario_objective_cost_units"] for x in records if x["hypothetical_rating_mw"]==float(c))
            for c in ratings]
    if any(a<b-1e-3 for a,b in zip(totals,totals[1:])):
        raise AssertionError("Relaxing synthetic line limits increased total optimal cost")
    summary={
        "network_source":"pinned PyPSA-USA Breakthrough Energy synthetic transmission test network",
        "anchor_source_bus_id":str(anchor),
        "selected_source_line_ids":source_lines,
        "selected_source_bus_ids":[str(anchor)]+neighbor_ids,
        "source_line_electrical_parameters":[{"id":str(i),"bus0":str(r.bus0),"bus1":str(r.bus1),
              "r_ohm":float(r.r_valid),"x_ohm":float(r.x_valid)} for i,r in candidates.iterrows()],
        "snapshots":len(times),
        "solver":"PyPSA + HiGHS",
        "experiment_type":"3-bus 3-snapshot strictly synthetic network-constrained economic dispatch",
        "hypothetical_branch_ratings_mw":list(map(float,ratings)),
        "generation_costs_and_loads":"hypothetical, not actual EIA-860 or system operation",
        "reported_objective_is_usd":False,
        "physical_facility_mapping_verified":False,
        "real_western_opf_executed":False,
        "synthetic_multinode_multiperiod_opf_executed":True,
        "snapshot_results":records,
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return summary


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--network",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--anchor",default="2040841")
    options=parser.parse_args()
    experiment(options.network,options.out,options.anchor)
