"""Two-bus AC-line-constrained HiGHS experiment with real Western line and EFS load.

Real: original Western bus names, line r/x/s_nom and original zonal EFS load.
Illustrative: two generator capacity/cost assumptions. NOT a full Western solve.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pypsa


def solve(network: Path, out: Path, hours: int = 24):
    source = pypsa.Network(str(network))
    if hours < 1 or hours > len(source.snapshots):
        raise ValueError("Bad hours")
    load_buses = set(source.loads.bus)
    lines = source.lines.copy()
    for col in ("x", "r", "s_nom"):
        lines[col] = pd.to_numeric(lines[col], errors="coerce")
    candidates = lines.loc[
        (lines.bus0.isin(load_buses) ^ lines.bus1.isin(load_buses))
        & np.isfinite(lines.x) & (lines.x > 0)
        & np.isfinite(lines.r) & (lines.r >= 0)
        & np.isfinite(lines.s_nom) & (lines.s_nom >= 100)
    ].sort_values("s_nom", ascending=False)
    if candidates.empty:
        raise ValueError("No rated real line connecting one loaded and one unloaded bus")
    line_id, line = next(iter(candidates.iterrows()))
    receiving = line.bus0 if line.bus0 in load_buses else line.bus1
    sending = line.bus1 if receiving == line.bus0 else line.bus0
    load_ids = source.loads.index[source.loads.bus == receiving]
    actual = source.loads_t.p_set.loc[source.snapshots[:hours], load_ids].sum(axis=1)
    if actual.isna().any() or (actual <= 0).any():
        raise ValueError("Invalid real EFS hourly load")
    net = pypsa.Network()
    net.set_snapshots(source.snapshots[:hours])
    for bus in (sending, receiving):
        net.add("Bus", str(bus), v_nom=float(source.buses.at[bus, "v_nom"]))
    net.add("Line", str(line_id), bus0=str(sending), bus1=str(receiving),
            r=float(line.r), x=float(line.x), s_nom=float(line.s_nom))
    net.add("Load", "actual_EFS_load", bus=str(receiving), p_set=actual.to_numpy())
    peak=float(actual.max())
    # Costs and generation are solely illustrative; local generation keeps solve feasible.
    net.add("Generator", "illustrative_remote", bus=str(sending),
            p_nom=peak*2, marginal_cost=10)
    net.add("Generator", "illustrative_local_backup", bus=str(receiving),
            p_nom=peak*2, marginal_cost=100)
    status, condition=net.optimize(solver_name="highs")
    if (status,condition)!=("ok","optimal"):
        raise RuntimeError(f"Solver {status}/{condition}")
    f=net.lines_t.p0[str(line_id)].abs()
    rating=float(line.s_nom)
    if (f>rating+max(1e-4,rating*1e-6)).any():
        raise ValueError("AC line thermal rating violated")
    demand_mwh=float(actual.sum())
    gen_mwh=float(net.generators_t.p.sum().sum())
    if not np.isclose(demand_mwh,gen_mwh,rtol=1e-8,atol=0.01):
        raise ValueError("Dispatch demand mismatch")
    result={"real_line_id":str(line_id),"sending_bus":str(sending),
        "receiving_bus":str(receiving),"real_line_r":float(line.r),
        "real_line_x":float(line.x),"real_line_s_nom_mva":rating,
        "hours":hours,"demand_source":"actual 2030 seven-state EFS/LAF Western load network",
        "actual_efs_demand_mwh":demand_mwh,"illustrative_generation_mwh":gen_mwh,
        "maximum_line_flow_mw":float(f.max()),"line_limit_verified":True,
        "solver_status":status,"solver_condition":condition,
        "objective_illustrative_usd":float(net.objective),
        "real_line_parameters":True,"generator_parameters_illustrative":True,
        "full_western_network_solved":False,"utc_aligned":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--hours",type=int,default=24)
    a=p.parse_args();solve(a.network,a.out,a.hours)
