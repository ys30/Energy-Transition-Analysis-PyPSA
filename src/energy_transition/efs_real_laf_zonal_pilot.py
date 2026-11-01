"""Apply verified built-network LAF_state to real EFS state-hour demand.

Pilot only: select states with complete nonnegative LAF and state sum <= 1.0001.
Never normalize absent/overfull state weights. LocalHourID remains local.
"""
import argparse
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa

STATE_NAMES={"AZ":"Arizona","CA":"California","CO":"Colorado","ID":"Idaho","MT":"Montana","NM":"New Mexico","NV":"Nevada","OR":"Oregon","UT":"Utah","WA":"Washington","WY":"Wyoming"}


def run(network: Path, hourly: Path, out: Path):
    n=pypsa.Network(str(network))
    bus=n.buses[["state","reeds_zone","LAF_state"]].copy()
    bus["LAF_state"]=pd.to_numeric(bus["LAF_state"], errors="coerce")
    accepted=[]
    blocked={}
    for state, frame in bus.groupby("state"):
        reasons=[]
        if not np.isfinite(frame["LAF_state"]).all(): reasons.append("nonfinite_bus_laf")
        if (frame["LAF_state"].dropna()<0).any(): reasons.append("negative_bus_laf")
        total=float(frame["LAF_state"].sum())
        if total<=0 or total>1.0001: reasons.append("invalid_state_mass")
        if reasons: blocked[state]=reasons
        elif state in STATE_NAMES.values(): accepted.append(state)
    profiles=pd.read_csv(hourly, compression="gzip")
    if set(profiles.columns)!={"year","state","local_hour_id","load_mw"}:
        raise ValueError("Unexpected real EFS hourly columns")
    profiles["state"]=profiles["state"].map(STATE_NAMES)
    profiles=profiles[profiles["state"].isin(accepted)]
    weights=bus.groupby(["state","reeds_zone"],as_index=False)["LAF_state"].sum().rename(columns={"LAF_state":"weight"})
    joined=profiles.merge(weights,on="state",how="inner",validate="many_to_many")
    joined["allocated_mw"]=joined["load_mw"]*joined["weight"]
    zonal=joined.groupby(["year","local_hour_id","state","reeds_zone"],as_index=False)["allocated_mw"].sum()
    zonal.sort_values(["year","state","local_hour_id","reeds_zone"],inplace=True)
    out.parent.mkdir(parents=True,exist_ok=True)
    target=out.with_suffix(".csv.gz")
    zonal.to_csv(target,index=False,compression="gzip")
    source=profiles.groupby(["year","state"])["load_mw"].sum()
    allocated=zonal.groupby(["year","state"])["allocated_mw"].sum()
    expected={f"{y}:{s}":float(mw*weights.loc[weights.state.eq(s),"weight"].sum()) for (y,s),mw in source.items()}
    residual={f"{y}:{s}":float(allocated.loc[y,s]-value) for key,value in expected.items() for y,s in [key.split(":")] if False}
    checks=[]
    for (y,s),mw in source.items():
        expect=mw*float(weights.loc[weights.state.eq(s),"weight"].sum())
        actual=float(allocated.loc[(y,s)])
        if not np.isclose(actual,expect,rtol=1e-9,atol=0.02): raise ValueError(f"Demand mass mismatch {y}/{s}")
        checks.append({"year":int(y),"state":s,"source_mwh":float(mw),"western_allocated_mwh":actual,"state_laf_sum":float(expect/mw)})
    report={"pilot_only":True,"states_admitted":sorted(accepted),"states_blocked":blocked,"state_year_results":checks,"zonal_rows":len(zonal),"utc_alignment_verified":False,"source_laf_provenance_independently_certified":False,"optimization_solved":False,"zonal_csv":target.name}
    out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="state_year_results"},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True);p.add_argument("--efs",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();run(a.network,a.efs,a.out)
