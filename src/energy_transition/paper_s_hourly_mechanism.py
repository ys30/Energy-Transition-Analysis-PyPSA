"""Export bounded original-source EFS + synthetic-supply hourly LP mechanism traces.

Only one deterministic highest-demand zone in a given projection year.
Preserves old solver defaults; compares complete summaries against archived 540 cases.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone,SHAPES,DURATIONS
from .efs_ordinal_storage_sensitivity import shape_cf

MEASURES=("demand_mwh","renewable_available_mwh","renewable_direct_mwh",
          "storage_charge_input_mwh","storage_discharge_to_load_mwh",
          "firm_generation_mwh","unused_renewable_mwh","objective_illustrative_variable_usd")


def run(source, archive, year=2030, hours=8760):
    required={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if not required.issubset(source): raise ValueError("Missing original source demand columns")
    a=source[source.year==year].copy()
    if a.empty or a[list(required)].isna().any().any():raise ValueError("Missing selected source year")
    if a.duplicated(["state","reeds_zone","local_hour_id"]).any():raise ValueError("Duplicate hour")
    zones=[]
    for (state,zone),g in a.groupby(["state","reeds_zone"]):
        g=g.sort_values("local_hour_id")
        if not np.array_equal(g.local_hour_id.to_numpy(),np.arange(1,hours+1)):
            raise ValueError("Incomplete source-hour ordinal sequence")
        d=g.allocated_mw.to_numpy(dtype=float)
        if not np.isfinite(d).all() or (d<0).any():raise ValueError("Bad source load")
        zones.append((float(d.sum()),str(state),str(zone),d))
    zones.sort(key=lambda q:(-q[0],q[1],q[2]))
    if len(zones)!=20:raise ValueError("Expected 20 original source zones for target year")
    _,state,zone,demand=zones[0]
    reference=archive[(archive.planning_year==year)&
                      (archive.state.astype(str)==state)&
                      (archive.reeds_zone.astype(str)==zone)]
    if len(reference)!=9:raise ValueError("Selected zone absent or incomplete in archived LP output")
    tables=[];stats=[]
    for shape in SHAPES:
        cf=shape_cf(np.arange(1,hours+1),shape)
        for duration in DURATIONS:
            summary,trace=solve_zone(demand,cf,duration,return_trace=True)
            ref=reference[(reference.synthetic_supply_shape==shape)&
                          (reference.battery_duration_h==duration)]
            if len(ref)!=1:raise ValueError("Missing unique archived zone-year case")
            for k in MEASURES:
                if not np.isclose(summary[k],float(ref.iloc[0][k]),rtol=1e-9,atol=.025):
                    raise ValueError("Original archived LP annual output mismatch: "+k)
            trace.insert(0,"planning_year",year)
            trace.insert(1,"state",state)
            trace.insert(2,"reeds_zone",zone)
            trace.insert(3,"synthetic_supply_shape",shape)
            trace.insert(4,"battery_duration_h",duration)
            p=summary["storage_power_mw"];capacity=summary["storage_capacity_mwh"]
            stats.append({"planning_year":year,"state":state,"reeds_zone":zone,
                          "synthetic_supply_shape":shape,"battery_duration_h":duration,
                          "hours":len(trace),
                          "predispatch_surplus_hours":int((trace.surplus_pre_dispatch_mwh>1e-7).sum()),
                          "predispatch_deficit_hours":int((trace.deficit_pre_dispatch_mwh>1e-7).sum()),
                          "charging_hours":int((trace.storage_charge_input_mwh>1e-7).sum()),
                          "discharging_hours":int((trace.storage_discharge_to_load_mwh>1e-7).sum()),
                          "soc_at_capacity_hours":int(trace.soc_at_energy_limit.sum()),
                          "charge_power_limit_hours":int(trace.charge_at_power_limit.sum()),
                          "discharge_power_limit_hours":int(trace.discharge_at_power_limit.sum()),
                          "battery_power_mw":p,"battery_capacity_mwh":capacity,
                          "annual_toy_cost_usd":summary["objective_illustrative_variable_usd"],
                          "archive_matched":True})
            tables.append(trace)
    hourly=pd.concat(tables,ignore_index=True)
    summary_table=pd.DataFrame(stats)
    if len(hourly)!=hours*9 or len(summary_table)!=9:
        raise ValueError("Incomplete mechanism traces")
    return hourly,summary_table,{"status":"HOURLY_SOURCE_ARCHIVE_RECONCILIATION_PASS",
        "year":year,"state":state,"reeds_zone":zone,"hours_per_case":hours,
        "cases":9,"archive_matched":True,"physical_utc_certified":False,
        "real_renewable_profiles":False,"western_grid_opf":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--year",type=int,choices=(2030,2040,2050),default=2030)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    hourly,stats,meta=run(pd.read_csv(a.source,compression="infer"),pd.read_csv(a.archive),a.year)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    hourly.to_csv(a.out_dir/"representative_zone_hourly_lp.csv.gz",index=False,compression="gzip")
    stats.to_csv(a.out_dir/"representative_zone_mechanism_metrics.csv",index=False)
    (a.out_dir/"representative_zone_mechanism_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps(meta,indent=2))


if __name__=="__main__":main()
