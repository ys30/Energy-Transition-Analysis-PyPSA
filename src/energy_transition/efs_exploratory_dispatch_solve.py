"""Exploratory HiGHS dispatch on real EFS demand; generation assumptions synthetic.

This deliberately does NOT claim a calibrated Western network or AC power flow.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import pypsa

def run(zonal: Path, out: Path, year=2030, hours=24):
    data=pd.read_csv(zonal,compression="gzip")
    data=data[(data.year==year)&data.local_hour_id.between(1,hours)]
    if data.empty or data.local_hour_id.nunique()!=hours: raise ValueError("Incomplete pilot hours")
    network=pypsa.Network()
    network.set_snapshots(pd.date_range(f"{year}-01-01",periods=hours,freq="h"))
    for (state,zone),group in data.groupby(["state","reeds_zone"]):
        bus=f"{state}__{zone}"
        network.add("Bus",bus)
        demand=group.set_index("local_hour_id").allocated_mw.reindex(range(1,hours+1))
        if demand.isna().any():raise ValueError(f"Missing source EFS hour for {bus}")
        network.add("Load",f"efs_{bus}",bus=bus,p_set=demand.to_numpy())
        # Explicit illustrative marginal costs/capacities, NOT observed assets.
        peak=float(demand.max())
        network.add("Generator",f"illustrative_firm_{bus}",bus=bus,p_nom=peak*1.2,marginal_cost=90)
        network.add("Generator",f"illustrative_renewable_{bus}",bus=bus,p_nom=peak*0.3,
                    p_max_pu=0.5,marginal_cost=5)
    status,condition=network.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":raise RuntimeError(f"Optimization {status}, {condition}")
    total_demand=float(network.loads_t.p_set.sum().sum())
    supplied=float(network.generators_t.p.sum().sum())
    if abs(total_demand-supplied)>max(0.01,total_demand*1e-7):raise ValueError("Supply and demand mismatch")
    result={"year":year,"hours":hours,"buses":len(network.buses),
            "real_efs_zonal_demand_mwh":total_demand,
            "illustrative_dispatch_mwh":supplied,
            "objective_cost_usd_illustrative":float(network.objective),
            "solver_status":status,"solver_condition":condition,
            "synthetic_generation_capacities":True,"synthetic_generation_costs":True,
            "network_transmission_constraints_modeled":False,
            "utc_aligned":False,"research_claim_calibrated":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--year",type=int,default=2030)
    p.add_argument("--hours",type=int,default=24)
    a=p.parse_args();run(a.zonal,a.out,a.year,a.hours)
