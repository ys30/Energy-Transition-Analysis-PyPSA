"""Chronological storage feasibility experiment; deliberately separate from representative hours.

A 168-hour contiguous observed-demand window is mandatory. Storage energy
conservation cannot be represented by the existing month-by-hour snapshots.
This scenario uses an explicitly assumed 4-hour battery, not historical dispatch.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

def validate_window(hourly, hours=168):
    data=hourly.copy()
    required={"period","respondent","value"}
    if required-set(data):raise ValueError("Missing EIA-930 hourly inputs")
    data["period"]=pd.to_datetime(data.period,utc=True)
    if data.duplicated(["respondent","period"]).any():raise ValueError("Duplicate BA-hour demand")
    wide=data.pivot(index="period",columns="respondent",values="value").sort_index()
    if wide.isna().any().any():raise ValueError("Missing BA demand in contiguous window")
    if len(wide)!=hours or not wide.index.to_series().diff().iloc[1:].eq(pd.Timedelta(hours=1)).all():
        raise ValueError("Storage model requires exactly contiguous hourly observations")
    if not wide.gt(0).all().all():raise ValueError("Nonpositive demand")
    return wide.sum(axis=1)

def solve_window(hourly, output, *, battery_mw=1000.,duration_h=4.,
                 generation_mw=10000.,generation_cost=50.):
    import pypsa
    demand=validate_window(hourly)
    if min(battery_mw,duration_h,generation_mw,generation_cost)<=0:
        raise ValueError("Storage scenario parameters must be positive")
    n=pypsa.Network()
    n.add("Bus","pilot")
    n.set_snapshots(demand.index.tz_convert(None))
    n.add("Load","observed_EIA930",bus="pilot",p_set=demand.to_numpy())
    n.add("Generator","assumed_firm_supply",bus="pilot",p_nom=generation_mw,
          marginal_cost=generation_cost)
    n.add("Generator","unserved",bus="pilot",p_nom=1e7,marginal_cost=10000.)
    # StorageUnit links charge, discharge and state of charge across true hourly snapshots.
    n.add("StorageUnit","assumed_battery",bus="pilot",p_nom=battery_mw,
          max_hours=duration_h,efficiency_store=0.95,efficiency_dispatch=0.95,
          cyclic_state_of_charge=False,state_of_charge_initial=0.,
          marginal_cost=0.1)
    status,condition=n.optimize(solver_name="highs")
    if status!="ok" or condition!="optimal":raise RuntimeError(f"Storage solve: {status}, {condition}")
    charge=n.storage_units_t.p_store["assumed_battery"]
    discharge=n.storage_units_t.p_dispatch["assumed_battery"]
    soc=n.storage_units_t.state_of_charge["assumed_battery"]
    residual=soc.diff()
    residual.iloc[0]=soc.iloc[0]
    residual=residual-(charge*0.95-discharge/0.95)
    max_error=float(residual.abs().max())
    if max_error>1e-3:raise ValueError(f"Battery conservation residual {max_error} MWh")
    output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame({"demand_mw":demand.to_numpy(),"charge_mw":charge.to_numpy(),
                  "discharge_mw":discharge.to_numpy(),"state_of_charge_mwh":soc.to_numpy()},
                 index=demand.index).to_csv(output/"chronological_storage_dispatch.csv")
    report={"status":condition,"hours":len(demand),"battery_mw_assumed":battery_mw,
            "battery_duration_hours_assumed":duration_h,"capacity_mwh_assumed":battery_mw*duration_h,
            "round_trip_efficiency_assumed":0.95**2,
            "max_storage_conservation_error_mwh":max_error,
            "unserved_mwh":float(n.generators_t.p["unserved"].sum()),
            "scope":"Illustrative one-bus 168-hour chronological battery experiment, not observed storage calibration.",
            "data_warning":"Requires contiguous hourly observed demand; never apply to 288 representative snapshots."}
    (output/"chronological_storage_provenance.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--start",required=True,help="UTC beginning of the continuous 168-hour window")
    p.add_argument("--hours",type=int,default=168)
    p.add_argument("--output",type=Path,default=Path("outputs/chronological_storage"))
    args=p.parse_args()
    df=pd.read_csv(args.hourly)
    df["period"]=pd.to_datetime(df.period,utc=True)
    begin=pd.Timestamp(args.start,tz="UTC") if pd.Timestamp(args.start).tzinfo is None else pd.Timestamp(args.start).tz_convert("UTC")
    df=df[df.period.ge(begin)&df.period.lt(begin+pd.Timedelta(hours=args.hours))]
    if args.hours!=168:raise ValueError("Pilot currently limited to a 168-hour contiguous window")
    solve_window(df,args.output)
if __name__=="__main__":main()
